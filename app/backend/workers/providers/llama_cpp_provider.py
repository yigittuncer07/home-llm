import json
import httpx
from typing import AsyncGenerator
from workers.providers.base_provider import BaseProvider
from core.logger import logger
from core.exceptions import LLMAPIError, LLMConnectionError

class LlamaCPPProvider(BaseProvider):
    async def stream_response(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> AsyncGenerator[str, None]:
        api_base = model_config.get("api_base")
        if not api_base:
            raise ValueError("api_base is missing from model configuration.")

        max_tokens = model_config.get("max_generation_tokens", 1024)
        chat_id = model_config.get("chat_id", 0)
        url = f"{api_base}/chat/completions"

        payload = {
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens,
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        }

        logger.info(f"Sending request to llama.cpp API for chat {chat_id}")

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code >= 400:
                        await response.aread()
                        raise LLMAPIError(
                            chat_id=chat_id,
                            api_status_code=response.status_code,
                            api_error_body=response.text,
                            headers=dict(response.headers) 
                        )

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or line == "data: [DONE]":
                            continue

                        content = self._parse_sse_line(line, chat_id)
                        if content:
                            yield content

        except httpx.RequestError as e:
            raise LLMConnectionError(chat_id=chat_id, original_error=e) from e

    def _parse_sse_line(self, line: str, chat_id: int) -> str | None:
        """Extract content delta from a llama.cpp SSE line."""
        if not line.startswith("data: "):
            return None

        data = line[len("data: "):].strip()
        if data == "[DONE]":
            return None

        try:
            chunk = json.loads(data)
            return chunk["choices"][0].get("delta", {}).get("content", "")
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"JSON decode error for chat {chat_id}. Raw data: '{data}'. Error: {e}")
            return None

    async def _get_token_count(
        self, messages: list[dict], api_base: str, chat_id: int
    ) -> tuple[int, int]:
        """Queries the native llama.cpp endpoints for token count and context size."""
        
        # 1. get Context Size (n_ctx)
        n_ctx = 4096  # safe fallback
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                props_resp = await client.get(f"{api_base}/props")
                if props_resp.status_code == 200:
                    data = props_resp.json()
                    n_ctx = data.get("default_generation_settings", {}).get("n_ctx", 4096)
        except Exception as e:
            logger.warning(f"Failed to fetch /props for chat {chat_id}: {e}")

        # 2. get Token Count
        # llama.cpp /tokenize only accepts a string. sadly we have to guess, we crudely format it as ChatML.
        raw_text = "\n".join([f"<|im_start|>{m['role']}\n{m.get('content', '')}<|im_end|>" for m in messages])
        token_count = 0
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                tok_resp = await client.post(
                    f"{api_base}/tokenize",
                    json={"content": raw_text}
                )
                if tok_resp.status_code == 200:
                    tokens = tok_resp.json().get("tokens", [])
                    token_count = len(tokens)
                else:
                    logger.warning(f"Tokenize request failed with status {tok_resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to fetch /tokenize for chat {chat_id}: {e}")

        return token_count, n_ctx

    async def truncate_messages(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> list[dict]:
        """
        Truncates conversation history to fit within llama.cpp's n_ctx window.
        """
        api_base = model_config.get("api_base")
        max_generation_tokens = model_config.get("max_generation_tokens", 1024)
        chat_id = model_config.get("chat_id", 0)

        if not api_base:
            return messages

        truncated = list(messages)

        while len(truncated) > 2:
            total_tokens, max_model_len = await self._get_token_count(
                truncated, api_base, chat_id
            )

            if total_tokens <= (max_model_len - max_generation_tokens):
                break

            logger.info(f"Truncating messages for chat {chat_id}. Total tokens: {total_tokens}, Max model length: {max_model_len}")
            
            if len(truncated) >= 3:
                truncated.pop(1)
                truncated.pop(1)
            else:
                truncated.pop(1)

        return truncated