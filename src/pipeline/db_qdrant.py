from __future__ import annotations

from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest


def get_client(host: str = "localhost", port: int = 6333) -> QdrantClient:
    return QdrantClient(host=host, port=port)


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
    )


def upsert_points(client: QdrantClient, collection_name: str, points: List[Dict[str, Any]]) -> None:
    client.upsert(
        collection_name=collection_name,
        points=[
            rest.PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
            for p in points
        ],
    )