from functools import lru_cache
import os


@lru_cache(maxsize=1)
def get_collection():
    import chromadb

    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "chroma"),
        port=int(os.getenv("CHROMA_PORT", "8000")),
    )
    
    return client.get_or_create_collection(name="document_chunks")


def store_chunk_embedding(
    chunk_id: int,
    document_id: int,
    content: str,
    embedding: list[float],
):
    get_collection().add(
        ids=[str(chunk_id)],
        embeddings=[embedding],
        documents=[content],
        metadatas=[
            {
                "document_id": document_id,
                "chunk_id": chunk_id,
            }
        ],
    )

def delete_document_embeddings(document_id: int):
    get_collection().delete(
        where={
            "document_id": document_id
        }
    )


def search_similar_chunks(
    embedding: list[float],
    document_ids: list[int],
    limit: int = 5,
    max_distance: float = 0.8,
):
    if not document_ids:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    results = get_collection().query(
        query_embeddings=[embedding],
        n_results=limit,
        where={
            "document_id": {
                "$in": document_ids
            }
        },
    )

    filtered = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }

    for i, distance in enumerate(
        results["distances"][0]
    ):
        if distance <= max_distance:
            filtered["ids"][0].append(
                results["ids"][0][i]
            )
            filtered["documents"][0].append(
                results["documents"][0][i]
            )
            filtered["metadatas"][0].append(
                results["metadatas"][0][i]
            )
            filtered["distances"][0].append(
                distance
            )

    return filtered


def get_collection_count():
    return get_collection().count()
