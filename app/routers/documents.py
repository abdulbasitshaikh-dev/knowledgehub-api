import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi.responses import FileResponse
from enum import Enum
from ..database import get_db
from ..dependencies import get_current_user
from ..models import DocumentChunk, User, Document, DocumentFile
from ..services.document_processing import process_document
from ..tasks import process_document_task

from ..schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
    DocumentPatch,
    DocumentFileResponse,
    DocumentChunkResponse,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    status,
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def get_user_document(
    document_id: int,
    current_user: User,
    db: Session,
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.owner_id == current_user.id,
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_document = Document(
        title=document.title,
        content=document.content,
        owner_id=current_user.id,
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document

class DocumentSort(str, Enum):
    CREATED_AT = "created_at"
    CREATED_AT_DESC = "-created_at"
    TITLE = "title"
    TITLE_DESC = "-title"

@router.get("/", response_model=DocumentListResponse)
def get_documents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    sort: DocumentSort = Query(default=DocumentSort.CREATED_AT_DESC),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(Document)
        .filter(
            Document.owner_id == current_user.id
        )
    )

    if search:
        query = query.filter(
            or_(
                Document.title.ilike(f"%{search}%"),
                Document.content.ilike(f"%{search}%"),
            )
        )

    if sort == "created_at":
        query = query.order_by(Document.created_at.asc())

    elif sort == "-created_at":
        query = query.order_by(Document.created_at.desc())

    elif sort == "title":
        query = query.order_by(Document.title.asc())

    elif sort == "-title":
        query = query.order_by(Document.title.desc())

    total = query.count()

    has_next = skip + limit < total
    has_previous = skip > 0

    documents = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": has_next,
        "has_previous": has_previous,
        "items": documents,
    }

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
)

    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
)

    document.title = document_data.title
    document.content = document_data.content

    db.commit()
    db.refresh(document)

    return document
    
@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
)

    db.delete(document)
    db.commit()


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
def patch_document(
    document_id: int,
    document_data: DocumentPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
    )

    update_data = document_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)

    return document

@router.post(
    "/{document_id}/file",
    response_model=DocumentFileResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
    )

    if document.file:
        raise HTTPException(
            status_code=400,
            detail="Document already has a file",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed types: PDF, TXT, DOCX",
        )

    stored_filename = (
        f"{document.id}{file_extension}"
    )

    file_path = UPLOAD_DIR / stored_filename

    file_content = file.file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 10 MB limit",
        )

    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    new_file = DocumentFile(
        document_id=document.id,
        filename=file.filename,
        file_path=str(file_path),
        content_type=file.content_type or "application/octet-stream",
        file_size=len(file_content),
    )

    db.add(new_file)

    document.processing_status = "pending"

    db.commit()
    db.refresh(new_file)


    process_document_task.delay(
        document.id,
        str(file_path),
        file.content_type or "application/octet-stream",
    )

    return new_file

@router.get(
    "/{document_id}/file",
)
def get_document_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
    )

    if not document.file:
        raise HTTPException(
            status_code=404,
            detail="Document has no file",
        )

    file_path = Path(document.file.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found on server",
        )

    return FileResponse(
        path=file_path,
        filename=document.file.filename,
        media_type=document.file.content_type,
    )

@router.delete(
    "/{document_id}/file",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_file(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
    )

    if not document.file:
        raise HTTPException(
            status_code=404,
            detail="Document has no file",
        )

    file_path = Path(document.file.file_path)

    if file_path.exists():
        file_path.unlink()

    db.delete(document.file)
    db.commit()

@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkResponse],
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = get_user_document(
        document_id,
        current_user,
        db,
    )

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document.id
        )
        .order_by(
            DocumentChunk.chunk_index.asc()
        )
        .all()
    )

    return chunks