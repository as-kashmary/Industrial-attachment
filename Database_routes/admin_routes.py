from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models # Assuming models.py is in the same directory or accessible via PYTHONPATH
from database import SessionLocal # Assuming database.py is accessible
from sqlalchemy.orm import Session

# Pydantic models specific to company or shared
class AdminBase(BaseModel):
     admin_name: str
     company_id: int
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
    prefix="/admin",  # All routes in this router will start with /company
    tags=["admin"],   # Groups routes in the OpenAPI docs
)

@router.post("/test", status_code=status.HTTP_201_CREATED)
async def create_admin(admin: AdminBase, db: db_dependency):
    db_admin= models.Admin(**admin.dict())
    db.add(db_admin)
    db.commit()

@router.get("/test", status_code=status.HTTP_200_OK)
async def read_admin(admin_id: int, db: db_dependency):
    admin= db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if admin is None:
         raise HTTPException(status_code=404, detail='Admin not found')
    return admin