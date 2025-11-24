from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models 
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile,  Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import io,os, shutil
from fastapi.responses import JSONResponse


UPLOAD_DIR = "files"


class FileSchema(BaseModel):
    id: int
    file_name: str
    product_id: int
    file_type: str
    class Config:
        orm_mode = True

class FileBase(BaseModel):
     file_name: str
     product_id: int
     file_type: str
     file_data: bytes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/file",  
    tags=["file"],
)


async def _get_all_files_name_from_db(db: Session, product_id: int) -> list[int]:
    files_name_tuples = db.query(models.File.file_name).filter(models.File.product_id == product_id).all()
    files_name = [pid[0] for pid in files_name_tuples]
    return files_name


async def collect_file_by_id(file_id: int, db: db_dependency):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if db_file is None:
         raise HTTPException(status_code=404, detail='File not found')
    file_data_stream = io.BytesIO(db_file.file_data)
    return StreamingResponse(
        file_data_stream,
        media_type=db_file.file_type,
        headers={"Content-Disposition": f"attachment; filename={db_file.file_name}"}
    )
    


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FileSchema)
async def create_file(db: db_dependency, product_id: int = Form(...), file: UploadFile = File(...)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")

    existing_file = db.query(models.File).filter(models.File.file_name == file.filename).first()
    if existing_file:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"File with name '{file.filename}' already exists")

    file_data_bytes = await file.read()

    db_file = models.File(
        file_name=file.filename,
        file_type=file.content_type,
        file_data=file_data_bytes,
        product_id=product_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

@router.get("/{file_id}", status_code=status.HTTP_200_OK)
async def read_file(file_id: int, db: db_dependency):
    return await collect_file_by_id(file_id, db)

@router.post("/upload")
async def upload_file(
    db: db_dependency ,
    admin_name: str = Form(...),
    product_name: str = Form(...),
    file_type: str = Form(...),
    uploaded_file: UploadFile = File(...),
    file_name: str = Form(...),
    
):
    # Save file to local directory
    # Look up product by name
    db_admin = db.query(models.Admin).filter(models.Admin.admin_name == admin_name).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail=f"Admin with name '{admin_name}' not assigned to product '{product_name}'.")

    product = db.query(models.Product).filter(models.Product.product_title == product_name).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with name '{product_name}' not found.")

    # Check for duplicate file name for the same product
    existing_file = db.query(models.File).filter(
        models.File.file_name == uploaded_file.filename,
        models.File.product_id == product.id
    ).first()
    if existing_file:
        raise HTTPException(status_code=409, detail=f"File '{uploaded_file.filename}' already exists for this product.")

    # Save file to disk (optional)
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    # Save file to database
    file_bytes = open(file_path, "rb").read()
    db_file = models.File(
        file_name=uploaded_file.filename,
        file_type=file_type,
        file_data=file_bytes,
        product_id=product.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return JSONResponse(content={
        "message": "File uploaded successfully.",
        "file_id": db_file.id,
        "product_id": product.id,
        "file_path": file_path
    })