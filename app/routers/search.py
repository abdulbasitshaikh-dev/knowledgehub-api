from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Document
from ..schemas import SemanticSearchResult
from ..services.embedding_service import generate_embedding
from ..services.vector_store import search_similar_chunks


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get(
    "/",
    response_model=list[SemanticSearchResult],
)
def semantic_search(
    q: str = Query(
        min_length=1,
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
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

    document_ids = [
        document.id
        for document in documents
    ]

    query_embedding = generate_embedding(q)

    results = search_similar_chunks(
        embedding=query_embedding,
        document_ids=document_ids,
        limit=limit,
    )

    search_results = []

    for i, chunk_id in enumerate(
        results["ids"][0]
    ):
        metadata = results["metadatas"][0][i]

        document_id = metadata["document_id"]

        document = document_map.get(document_id)

        if not document:
            continue

        search_results.append(
            SemanticSearchResult(
                chunk_id=int(chunk_id),
                document_id=document_id,
                document_title=document.title,
                content=results["documents"][0][i],
                distance=results["distances"][0][i],
            )
        )
        
    return search_results