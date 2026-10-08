from abc import ABC, abstractmethod


class EmbeddingClient(ABC):

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        pass