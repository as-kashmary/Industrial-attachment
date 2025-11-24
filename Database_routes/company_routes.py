from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models # Assuming models.py is in the same directory or accessible via PYTHONPATH
from database import SessionLocal # Assuming database.py is accessible
from sqlalchemy.orm import Session

# Pydantic models specific to company or shared
class CompanyBase(BaseModel):
     company_name: str

# You might want a response model here too
class CompanyResponse(CompanyBase):
    id: int
    class Config:
        orm_mode = True

# Dependency to get DB session (can be defined in a shared utils.py or here)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/company",  # All routes in this router will start with /company
    tags=["company"],   # Groups routes in the OpenAPI docs
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CompanyResponse)
async def create_company(company: CompanyBase, db: db_dependency):
    # Add pre-creation check for uniqueness if needed
    existing_company = db.query(models.Company).filter(models.Company.company_name == company.company_name).first()
    if existing_company:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Company with this name already exists")
    db_company = models.Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company) # Good to refresh to get DB-generated values like ID
    return db_company

@router.get("/{company_id}", status_code=status.HTTP_200_OK, response_model=CompanyResponse) # Changed path to be more RESTful
async def read_company(company_id: int, db: db_dependency):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if company is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Company not found')
    return company

# Add other company-related routes here (e.g., update, delete, list all)
