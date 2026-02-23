import hashlib
import json
from pathlib import Path

from pipeline.ingest import ingest, jobs_to_dicts
from pipeline.extract_text import extract_text_and_metadata
from pipeline.chunk_text import clean_and_tokenize, chunk_tokens, chunks_to_dicts
from pipeline.embed import embed_texts
from pipeline.db_qdrant import get_client, ensure_collection, upsert_points

COLLECTION_NAME = "m02_documents"


def stable_point_id(doc_id: str, chunk_index: int) -> str:
    return hashlib.sha256(f"{doc_id}:{chunk_index}".encode("utf-8")).hexdigest()


def main():
    input_dir = Path("data/input")
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs = ingest(input_dir)
    print("\nIngestion complete")
    print("Files found:", len(jobs))

    # Connect to Qdrant
    client = get_client()

    collection_ready = False

    for j in jobs:
        path = Path(j.filepath)

        # 1) Extract text + metadata
        raw_text, meta = extract_text_and_metadata(path)
        print(f"\n--- {j.filename} ---")
        print("Raw chars:", len(raw_text))
        print("Metadata:", meta)

        # 2) Clean + tokenize
        tokens = clean_and_tokenize(raw_text)
        print("Tokens after cleaning:", len(tokens))

        # 3) Chunk
        chunks = chunk_tokens(tokens, chunk_size=200, overlap=50)
        print("Chunks created:", len(chunks))

        # Save local proof artifacts
        (output_dir / f"{j.doc_id}_raw.txt").write_text(raw_text, encoding="utf-8")
        chunks_path = output_dir / f"{j.doc_id}_chunks.json"
        chunks_path.write_text(
            json.dumps(
                {
                    "doc_id": j.doc_id,
                    "filename": j.filename,
                    "filepath": j.filepath,
                    "mime_type": j.mime_type,
                    "metadata": meta,
                    "chunk_size_tokens": 200,
                    "overlap_tokens": 50,
                    "num_chunks": len(chunks),
                    "chunks": chunks_to_dicts(chunks),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        if not chunks:
            print("No chunks to embed; skipping DB write.")
            continue

        # 4) Embeddings
        chunk_texts = [c.chunk_text for c in chunks]
        vectors = embed_texts(chunk_texts)

        # 5) Ensure collection exists (needs vector size)
        if not collection_ready:
            ensure_collection(client, COLLECTION_NAME, vector_size=len(vectors[0]))
            collection_ready = True
            print(f"✅ Qdrant collection ready: {COLLECTION_NAME}")

        # 6) Upsert into Qdrant
        points = []
        for c, v in zip(chunks, vectors):
            pid = stable_point_id(j.doc_id, c.chunk_index)
            payload = {
                "doc_id": j.doc_id,
                "filename": j.filename,
                "filepath": j.filepath,
                "mime_type": j.mime_type,
                "chunk_index": c.chunk_index,
                "token_count": c.token_count,
                "metadata": meta,
                "text": c.chunk_text,
            }
            points.append({"id": pid, "vector": v, "payload": payload})

        upsert_points(client, COLLECTION_NAME, points)
        print(f"✅ Upserted {len(points)} chunks into Qdrant")

    # Save manifest
    manifest_path = output_dir / "ingestion_manifest.json"
    manifest_path.write_text(json.dumps(jobs_to_dicts(jobs), indent=2), encoding="utf-8")
    print("\nManifest written to:", manifest_path.resolve())
    print("✅ Done: embeddings stored in Qdrant")


if __name__ == "__main__":
    main()