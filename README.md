# KnowledgeHub API

KnowledgeHub is a backend learning project built with **FastAPI** that combines document management, asynchronous processing, vector search, and Retrieval-Augmented Generation (RAG).

The project was built to learn and apply modern backend, AI, Docker, and CI/CD concepts in one system.

## ✨ Features

- JWT authentication
- User authorization and document ownership isolation
- Document CRUD operations
- File uploads with type and size validation
- Background document processing with Celery
- PostgreSQL database with SQLAlchemy
- Database migrations with Alembic
- Text embeddings with SentenceTransformers
- Vector storage and similarity search with ChromaDB
- Retrieval-Augmented Generation (RAG)
- Gemini-powered answers
- Redis as Celery broker/backend
- Docker and Docker Compose
- Automated tests with pytest
- GitHub Actions CI
- Docker image publishing to GitHub Container Registry (GHCR)

## 🏗️ Architecture

```text
                         KnowledgeHub API
                                │
                    ┌───────────┴───────────┐
                    │                       │
                 FastAPI                 PostgreSQL
                    │                       │
          ┌─────────┼─────────┐             │
          │         │         │             │
       Auth/JWT  Documents    Ask            │
                              │              │
                              ▼              │
                         Embeddings          │
                              │              │
                              ▼              │
                           ChromaDB          │
                              │              │
                              ▼              │
                            Gemini           │
                                             │
          File processing ── Celery ── Redis
```

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| API | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT |
| Password hashing | Argon2 |
| Task queue | Celery |
| Message broker | Redis |
| Vector database | ChromaDB |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| LLM | Google Gemini |
| Containers | Docker / Docker Compose |
| Testing | pytest |
| CI/CD | GitHub Actions + GHCR |

## 🔄 RAG Pipeline

The `/ask/` endpoint follows this general flow:

```text
User question
     ↓
Generate query embedding
     ↓
Search relevant document chunks in ChromaDB
     ↓
Build context from retrieved chunks
     ↓
Send context + question to Gemini
     ↓
Return answer + source chunks
```

Documents are processed asynchronously:

```text
Upload document
      ↓
Create processing task
      ↓
Celery + Redis
      ↓
Extract text
      ↓
Split into chunks
      ↓
Generate embeddings
      ↓
Store chunks in PostgreSQL + ChromaDB
```

## 🚀 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/abdulbasitshaikh-dev/knowledgehub-api.git
cd knowledgehub-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on the project's environment configuration. Do not commit `.env` or API keys to Git.

Typical configuration includes:

```env
DATABASE_URL=...
REDIS_URL=...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GEMINI_API_KEY=...
CHROMA_HOST=...
CHROMA_PORT=...
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

API documentation is available through FastAPI's Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

## 🐳 Docker

The project includes Docker Compose configurations for development, Codespaces, and production-oriented deployment.

The main application image is built from the included `Dockerfile` and is used by the API, Celery worker, and migration service.

Example:

```bash
docker compose up -d
```

## 🧪 Testing

The project includes automated tests covering authentication, authorization, document ownership, and upload validation.

Run the test suite with:

```bash
pytest
```

Current test coverage includes:

- User registration
- Login and JWT authentication
- Protected `/me` endpoint
- Cross-user document access prevention
- Per-user document listing
- Unsupported upload type rejection
- Files larger than 10 MB rejection

## ⚙️ CI Pipeline

Every push to `master` and pull request targeting `master` triggers GitHub Actions.

```text
Git push
   ↓
GitHub Actions
   ↓
PostgreSQL service
   ↓
Run pytest
   ↓
Tests pass
   ↓
Build Docker image
   ↓
Push image to GHCR
```

The test environment uses a lightweight dependency set so CI does not need to install the complete ML runtime just to execute the API tests.

## 📦 Container Registry

Successful CI runs build the application Docker image and publish it to **GitHub Container Registry (GHCR)**.

Images are tagged with both:

- `latest`
- the Git commit SHA

This makes it possible to identify the exact application version represented by an image.

## 🔐 Security Notes

- Environment files are excluded from Git.
- API keys and application secrets should never be committed.
- JWT-protected endpoints validate the authenticated user.
- Documents are scoped to their owners.
- Uploads are restricted by extension and file size.
- Invalid JWT payloads are rejected cleanly.

## 📚 Project Purpose

KnowledgeHub was primarily built as a **learning project** to gain practical experience with:

- FastAPI backend development
- PostgreSQL and SQLAlchemy
- JWT authentication and authorization
- Redis and Celery
- Asynchronous document processing
- Embeddings and vector databases
- RAG architecture
- LLM integration
- Docker and containerization
- Automated testing
- GitHub Actions and CI/CD

The project is considered complete as a learning milestone and is intentionally not expanded into a large production platform.

## 📄 License

This project is provided for educational and portfolio purposes.
