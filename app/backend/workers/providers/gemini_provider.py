import os
import json
import httpx
from typing import AsyncGenerator
from providers.base_provider import BaseProvider
from core.logger import logger
from core.exceptions import LLMAPIError, LLMConnectionError

class GeminiProvider(BaseProvider):
    async def stream_response(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> AsyncGenerator[str, None]:
        
        api_base = model_config.get("api_base")
        api_key_env_var = model_config.get("api_key_env_var", "GEMINI_API_KEY")
        api_key = os.getenv(api_key_env_var)

        if not api_key:
            raise ValueError(f"Missing API key: {api_key_env_var} environment variable is not set.")

        # Gemini uses Server-Sent Events with the ?alt=sse query parameter
        url = f"{api_base}/models/{model_name}:streamGenerateContent?alt=sse&key={api_key}"

        gemini_messages = self._format_messages_for_gemini(messages)
        payload = {"contents": gemini_messages}

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code >= 400:
                        await response.aread()
                        raise LLMAPIError(
                            chat_id=0,
                            api_status_code=response.status_code,
                            api_error_body=response.text,
                            headers=dict(response.headers) 
                        )

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[len("data: "):]
                            try:
                                chunk = json.loads(data_str)
                                # Extract text from the Gemini response structure
                                text = chunk.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
                                if text:
                                    yield text
                            except (json.JSONDecodeError, IndexError):
                                continue

        except httpx.RequestError as e:
            raise LLMConnectionError(chat_id=0, original_error=e) from e

    def _format_messages_for_gemini(self, messages: list[dict]) -> list[dict]:
        """Translates OpenAI-style roles to Gemini-style roles."""
        gemini_history = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # Gemini expects 'user' and 'model'
            if role == "assistant":
                role = "model"
            elif role == "system":
                # Note: Gemini system instructions are usually handled at the root payload level,
                # but for simplicity, we map it to a user prompt if it's the first message.
                role = "user"
                
            gemini_history.append({
                "role": role,
                "parts": [{"text": content}]
            })
        return gemini_history