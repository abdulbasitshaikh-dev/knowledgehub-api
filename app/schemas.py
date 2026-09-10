from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str 

class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    created_at: datetime
    updated_at: datetime

    processing_status: str

    extracted_text: str | None

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool
    items: list[DocumentResponse]

class DocumentUpdate(BaseModel):
    title: str 
    content: str 

class DocumentPatch(BaseModel):
    title: str | None = None
    content: str | None = None

class DocumentFileResponse(BaseModel):
    id: int
    document_id: int
    filename: str
    file_path: str
    content_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class SemanticSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    content: str
    distance: float

class AskRequest(BaseModel):
    question: str


class AskSource(BaseModel):
    chunk_id: int
    document_id: int
    document_title: str
    distance: float


class AskResponse(BaseModel):
    answer: str
    sources: list[AskSource]