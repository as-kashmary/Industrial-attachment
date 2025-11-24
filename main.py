from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile,  Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Annotated
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import os, shutil

from models import File as FileModel


import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

from user import process_query
import admin
# import LLm_model
from user import process_query 

from Database_routes.company_routes import router as company_router
from Database_routes.product_routes import router as product_router, _get_all_product_ids_from_db
from Database_routes.admin_routes import router as admin_router
from Database_routes.user_routes import router as user_router
from Database_routes.file_routes import router as file_router, _get_all_files_name_from_db, collect_file_by_id

from langchain.embeddings import HuggingFaceEmbeddings
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse


app= FastAPI()

UPLOAD_DIR = "files"

#for not storing cache files

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response
app.mount("/static", NoCacheStaticFiles(directory="admin"), name="static")
# app.mount("/static", StaticFiles(directory="User_demo"), name="static")


all_product_ids= []
all_product_names= []
embedding_model= None



@app.on_event("startup")
async def startup_event():

    global all_product_ids, all_product_names, embedding_model

    persist_directory = "my_chroma_db"
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    embedding_model = HuggingFaceEmbeddings(
        model_name="./models/multilingual-e5-large-instruct"
    )
    print("Startup event triggered.")

    db= SessionLocal()
    try:
        all_product_ids, all_product_names = await _get_all_product_ids_from_db(db)
        if all_product_ids:
            print(f"Found product IDs: {all_product_ids}")
            # for product_id_val in all_product_ids:
            for i in range(0,len(all_product_ids)):
                product_id_val = all_product_ids[i]
                product_name_val = all_product_names[i]
                print(f"Processing product ID: {product_id_val} (Name: {product_name_val})")
                file_names_for_product = await _get_all_files_name_from_db(db, product_id_val)
                
                if file_names_for_product:
                    admin.init_system(file_names_for_product,product_name=product_name_val, embedding_model=embedding_model) 
                    # print(f"Found file IDs for product {product_id_val}: {file_names_for_product}")
                    # for single_file_id in file_names_for_product:
                    #     print(f"Processing file ID: {single_file_id} (Product ID: {product_id_val})")
                        
                else:
                    print(f"No files found for product ID: {product_id_val}")
        else:
            print("No product IDs found in the system during startup.")
        
        # LLm_model.init_model()
    except Exception as e:
        print(f"Error during startup: {e}")
    finally:
        db.close()
        print("Database session closed. Startup complete.")

@app.get("/ask")
async def ask(query: str):
    answer = process_query(query)
    return {"answer": answer}


models.Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]

app.include_router(product_router) 
app.include_router(company_router) 
app.include_router(admin_router) 
app.include_router(user_router) 
app.include_router(file_router) 

@app.get("/", status_code=status.HTTP_200_OK)
async def read_query(query: str, product_id: int):
    pos= all_product_ids.index(product_id)
    product_name= all_product_names[pos]
    answer = process_query(query,embedding_model = embedding_model,product_name=product_name)
    return {"answer": answer, "product_id_received": product_id}


@app.get("/process-product-query", status_code=status.HTTP_200_OK)
async def process_product_query_endpoint(query: str, product_name: str):
    print(product_name)
    answer = process_query(query, embedding_model=embedding_model, product_name=product_name)
    return {"answer": answer, "product_name_processed": product_name}




@app.get("/admin", status_code=status.HTTP_200_OK)
async def get_admin_page():
    admin_path = Path("admin/admin.html")
    return HTMLResponse(content=admin_path.read_text(), status_code=200) 


@app.get("/user", status_code=status.HTTP_200_OK)
async def get_admin_page():
    user_path = Path("admin/user.html")
    return HTMLResponse(content=user_path.read_text(), status_code=200)



 
@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools():
    return JSONResponse(content={}, status_code=200)



