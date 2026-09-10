import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Document, DocumentChunk
from app.services.document_service import extract_text
from app.services.chunking import chunk_text
from app.services.embedding_service import generate_embedding
from app.services.vector_store import (
    store_chunk_embedding,
    delete_document_embeddings,
)

logger = logging.getLogger(__name__)


def process_document(
    document_id: int,
    file_path: str,
    content_type: str,
):
    logger.info(
        "Document processing started: document_id=%s",
        document_id,
    )

    db: Session = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            logger.warning(
                "Document not found: document_id=%s",
                document_id,
            )
            return

        delete_document_embeddings(document_id)

        document.processing_status = "processing"
        db.commit()

        text = extract_text(
            file_path,
            content_type,
        )

        document.extracted_text = text

        chunks = chunk_text(text)

        logger.info(
            "Document chunked: document_id=%s chunks=%s",
            document_id,
            len(chunks),
        )

        for index, chunk in enumerate(chunks):
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
            )

            db.add(document_chunk)
            db.flush()

            embedding = generate_embedding(chunk)

            store_chunk_embedding(
                chunk_id=document_chunk.id,
                document_id=document.id,
                content=chunk,
                embedding=embedding,
            )

        document.processing_status = "completed"

        db.commit()

        logger.info(
            "Document processing completed: document_id=%s chunks=%s",
            document_id,
            len(chunks),
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Document processing failed: document_id=%s",
            document_id,
        )

        raise

    finally:
        db.close()