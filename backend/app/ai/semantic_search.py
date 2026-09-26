from app.ai.embeddings import (
    cosine_similarity,
    generate_embedding,
)


class SemanticSearch:

    def rank(
        self,
        query: str,
        documents: list[dict],
    ) -> list[dict]:

        query_embedding = generate_embedding(query)

        results = []

        for document in documents:
            text = document.get("text", "")

            if not text:
                document["similarity"] = 0.0
                results.append(document)
                continue

            embedding = generate_embedding(text)

            similarity = cosine_similarity(
                query_embedding,
                embedding,
            )

            item = dict(document)
            item["similarity"] = round(
                similarity,
                4,
            )

            results.append(item)

        return sorted(
            results,
            key=lambda item: item["similarity"],
            reverse=True,
        )


semantic_search = SemanticSearch()