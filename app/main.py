from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app import database
from app.database import get_db
from app.models import User, Document

from app.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    DocumentCreate,
    DocumentResponse,
)
from app.security import hash_password, verify_password
from app.routers.auth import create_access_token
from app.dependencies import get_current_user
from .routers.documents import router as document_router
from .routers.search import router as search_router
from .routers.ask import router as ask_router


from fastapi import (
    FastAPI,
    Depends,
    HTTPException
)

app = FastAPI(
    title="KnowledgeHub API",
)


@app.get("/")
def home():
    return {"message": "Welcome to the KnowledgeHub API!"}


@app.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        user_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT
    access_token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/me", response_model=UserResponse)
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user


app.include_router(document_router)
app.include_router(search_router)
app.include_router(ask_router)
