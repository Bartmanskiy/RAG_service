import httpx
import json

from collections.abc import AsyncIterator

from app.clients.embedding_client import EmbeddingClient
from app.clients.llm_client import LLMClient
from app.config import settings


class OllamaClient(EmbeddingClient, LLMClient):

    def __init__(self):
        self.base_url = settings.ollama_url
        self.embedding_model = settings.embedding_model
        self.llm_model = settings.llm_model

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.embedding_model,
                    "input": text,
                },
            )

            response.raise_for_status()

            data = response.json()

            return data["embeddings"][0]

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                },
            )

            response.raise_for_status()

            data = response.json()

            return data["response"]

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    data = json.loads(line)

                    if data.get("done"):
                        break

                    token = data.get("response", "")

                    if token:
                        yield token