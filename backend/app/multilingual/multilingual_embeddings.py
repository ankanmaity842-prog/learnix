from app.ai.embeddings import (
    generate_embedding,
    generate_embeddings,
)


def embed_text(
    text: str,
) -> list[float]:
    return generate_embedding(text)


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    return generate_embeddings(texts)