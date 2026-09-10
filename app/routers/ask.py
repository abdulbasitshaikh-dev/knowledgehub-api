from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time
from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Document
from ..schemas import (
    AskRequest,
    AskResponse,
    AskSource,
)
from ..services.embedding_service import generate_embedding
from ..services.vector_store import search_similar_chunks
from ..services.llm_service import generate_answer


router = APIRouter(
    prefix="/ask",
    tags=["RAG"],
)


@router.post(
    "/",
    response_model=AskResponse,
)
def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    documents = (
        db.query(Document)
        .filter(
            Document.owner_id == current_user.id
        )
        .all()
    )

    document_map = {
        document.id: document
        for document in documents
    }

    document_ids = list(document_map.keys())

    start = time.perf_counter()

    embedding_start = time.perf_counter()

    query_embedding = generate_embedding(
        request.question
    )

    embedding_time = time.perf_counter() - embedding_start

    
    search_start = time.perf_counter()

    results = search_similar_chunks(
        embedding=query_embedding,
        document_ids=document_ids,
        limit=3,
    )

    search_time = time.perf_counter() - search_start


    if not results["ids"][0]:
        return AskResponse(
            answer=(
                "I couldn't find relevant information "
                "in your documents to answer that question."
            ),
            sources=[],
        )

    context_parts = []
    sources = []

    for i, chunk_id in enumerate(
        results["ids"][0]
    ):
        metadata = results["metadatas"][0][i]

        document_id = metadata["document_id"]

        document = document_map.get(document_id)

        if not document:
            continue

        context_parts.append(
            results["documents"][0][i]
        )

        sources.append(
            AskSource(
                chunk_id=int(chunk_id),
                document_id=document_id,
                document_title=document.title,
                distance=results["distances"][0][i],
            )
        )

    # Check AFTER building the context
    if not context_parts:
        return AskResponse(
            answer=(
                "I couldn't find relevant information "
                "in your documents to answer that question."
            ),
            sources=[],
        )

    context = "\n\n---\n\n".join(
        context_parts
    )

    llm_start = time.perf_counter()

    answer = generate_answer(
        question=request.question,
        context=context,
    )

    llm_time = time.perf_counter() - llm_start

    total_time = time.perf_counter() - start

    print(
        f"Embedding: {embedding_time:.2f}s | "
        f"Search: {search_time:.2f}s | "
        f"LLM: {llm_time:.2f}s | "
        f"Total: {total_time:.2f}s"
    )

    return AskResponse(
        answer=answer,
        sources=sources,
    )