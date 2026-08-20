from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseProvider(ABC):
    @abstractmethod
    def stream_response(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> AsyncGenerator[str, None]:
        """
        Yields string tokens from the LLM stream.
        """
        ...

    async def truncate_messages(
        self, model_name: str, messages: list[dict], model_config: dict
    ) -> list[dict]:
        """
        Optional: Truncate messages if they exceed the model's limits.
        Defaults to returning the messages untouched if not overridden.
        """
        return messages