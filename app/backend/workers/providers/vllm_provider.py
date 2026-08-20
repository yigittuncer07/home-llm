import json
import httpx
from typing import AsyncGenerator
from providers.base_provider import BaseProvider
from core.logger import logger
from core.exceptions import LLMAPIError, LLMConnectionError

class VLLMProvider(BaseProvider):
    async def stream_response(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> AsyncGenerator[str, None]:
        api_base = model_config.get("api_base")
        if not api_base:
            raise ValueError("api_base is missing from model configuration.")

        max_tokens = model_config.get("max_tokens", 4096)
        chat_id = model_config.get("chat_id", 0)
        url = f"{api_base}/v1/chat/completions"

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "max_tokens": max_tokens
        }

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
        """Extract content delta from a vLLM SSE line."""
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
        self, messages: list[dict], model_name: str, api_base: str, chat_id: int
    ) -> tuple[int, int]:
        """Queries the vLLM /tokenize endpoint to check context size and limits."""
        tokenize_url = f"{api_base}/tokenize"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    tokenize_url,
                    json={"model": model_name, "messages": messages}
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("count", 0), data.get("max_model_len", 4096)
                else:
                    raise LLMConnectionError(
                        chat_id=chat_id,
                        original_error=Exception(f"Tokenize request failed with status {response.status_code}")
                    )
        except httpx.RequestError as e:
            raise LLMConnectionError(chat_id=chat_id, original_error=e) from e

    async def truncate_messages(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> list[dict]:
        """
        Truncates conversation history by popping oldest user/assistant pairs
        until the context fits within the model's context window.
        """
        api_base = model_config.get("api_base")
        max_tokens = model_config.get("max_tokens", 4096)
        chat_id = model_config.get("chat_id", 0)

        if not api_base:
            return messages

        # Work on a shallow copy to prevent side effects
        truncated = list(messages)

        while len(truncated) > 1:
            total_tokens, max_model_len = await self._get_token_count(
                truncated, model_name, api_base, chat_id
            )

            if total_tokens <= (max_model_len - max_tokens):
                break

            # If system prompt + at least 1 turn pair exists, pop oldest turn
            if len(truncated) >= 3:
                truncated.pop(1)  # Remove oldest user message
                truncated.pop(1)  # Remove oldest assistant message
            else:
                truncated.pop(1)

        return truncated