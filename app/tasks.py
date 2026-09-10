import logging
from celery import Task

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Document
from app.services.document_processing import process_document

logger = logging.getLogger(__name__)

class DocumentProcessingTask(Task):

    def on_failure(
        self,
        exc,
        task_id,
        args,
        kwargs,
        einfo,
    ):
        document_id = args[0]

        db = SessionLocal()

        try:
            document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            if document:
                document.processing_status = "failed"
                db.commit()

        finally:
            db.close()

        logger.error(
            "Celery document task permanently failed: document_id=%s task_id=%s",
            document_id,
            task_id,
        )


@celery_app.task(
    bind=True,
    base=DocumentProcessingTask,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def process_document_task(
    self: Task,
    document_id: int,
    file_path: str,
    content_type: str,
):
    logger.info(
        "Celery document task started: document_id=%s",
        document_id,
    )

    process_document(
        document_id=document_id,
        file_path=file_path,
        content_type=content_type,
    )

    logger.info(
        "Celery document task completed: document_id=%s",
        document_id,
    )