from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache
def get_model():
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    model = get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def cosine_similarity(
    first: list[float],
    second: list[float],
) -> float:
    a = np.asarray(first)
    b = np.asarray(second)

    return float(np.dot(a, b))