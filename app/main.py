from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app import database
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.security import hash_password

app = FastAPI(
    title = "KnowledgeHub API",
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
