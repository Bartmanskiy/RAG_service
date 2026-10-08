class RAGService:
    def __init__(
        self,
        retrieval_service,
        llm_client,
    ):
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client

    async def answer(
        self,
        question: str,
        top_k: int | None = None,
        document_ids: list[str] | None = None,
    ) -> dict:
        results = await self.retrieval_service.search(
            question=question,
            top_k=top_k,
            document_ids=document_ids,
        )

        if not results:
            return {
                "answer": "У документах не знайдено інформації за цим запитом",
                "sources": [],
            }

        context_parts = []

        for index, result in enumerate(results, start=1):
            context_parts.append(
                f"[Source {index}]\n"
                f"{result['text']}"
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a corporate knowledge base assistant.

Answer the user's question ONLY using the information from the provided context.

If the answer cannot be found in the context, say that the information is not available in the provided documents.

Do not use outside knowledge.
Do not invent facts.

Context:
{context}

Question:
{question}

Answer:
""".strip()

        answer = await self.llm_client.generate(prompt)

        sources = [
            {
                "document_id": str(result["document_id"]),
                "page": result["page"],
                "score": result["score"],
                "snippet": result["text"],
            }
            for result in results
        ]

        return {
            "answer": answer,
            "sources": sources,
        }