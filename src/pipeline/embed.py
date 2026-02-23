from __future__ import annotations

from typing import List
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = SentenceTransformer(_MODEL_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    vectors = _model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()
