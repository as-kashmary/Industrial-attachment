from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models # Assuming models.py is in the same directory or accessible via PYTHONPATH
from database import SessionLocal # Assuming database.py is accessible
from sqlalchemy.orm import Session

# Pydantic models specific to company or shared
class UserBase(BaseModel):
     user_name: str
     product_id: int

# Dependency to get DB session (can be defined in a shared utils.py or here)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/user",  # All routes in this router will start with /company
    tags=["user"],   # Groups routes in the OpenAPI docs
)

@router.post("/test", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user= models.User(**user.dict())
    db.add(db_user)
    db.commit()

@router.get("/test", status_code=status.HTTP_200_OK)
async def read_user(user_id: int, db: db_dependency):
    user= db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
         raise HTTPException(status_code=404, detail='User not found')
    return user