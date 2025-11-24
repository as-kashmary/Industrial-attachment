from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models 
from database import SessionLocal 
from sqlalchemy.orm import Session 

class ProductBase(BaseModel):
     product_title: str
     company_id: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/product",  
    tags=["product"],   
)

async def _get_all_product_ids_from_db(db: Session) -> list[int]:
    product_ids_tuples = db.query(models.Product.id).all()
    product_ids = [pid[0] for pid in product_ids_tuples]
    product_names_tuples=db.query(models.Product.product_title).all()
    product_names=[pname[0] for pname in product_names_tuples]
    return product_ids, product_names


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductBase, db: db_dependency):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()

@router.get("/ids", status_code=status.HTTP_200_OK, response_model=list[int])
async def get_all_product_ids(db: db_dependency):
    product_ids = await _get_all_product_ids_from_db(db)
    if product_ids:
        print(f"Found product IDs: {product_ids}")
    else:
        print("No product IDs found in the database.")
    return product_ids
