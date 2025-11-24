from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os, shutil
# from llama_cpp import Llama

vector_store = None
# llm_model = None

def init_system(file_names,product_name, embedding_model):
    print(f'Recieved files: {file_names} and product name: {product_name}')

    global vector_store

    all_loaded_documents = []
    # 1) Load PDFs
    # Ensure 'file_names' contains full, accessible paths to the PDF files.
    for file_path in file_names:
        # Construct the full path assuming 'files' is a subdirectory
        actual_file_path = os.path.join("files", file_path)
        try:
            # print(f"Loading PDF: {actual_file_path}")
            loader = PyPDFLoader(actual_file_path)
            # loader.load() returns a list of Document objects (one per page)
            documents_from_single_pdf = loader.load()
            all_loaded_documents.extend(documents_from_single_pdf)
            # print(f"Successfully loaded {len(documents_from_single_pdf)} pages from {actual_file_path}.")
        except Exception as e:
            print(f"Error loading PDF {actual_file_path}: {e}. Skipping this file.")

    if not all_loaded_documents:
        print("No documents were successfully loaded. Halting initialization for this product.")
        return

    print(f"Total pages loaded from all PDFs: {len(all_loaded_documents)}")
    # print(all_loaded_documents)
    print('-------------------------')



    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=80, 
        length_function=len
    )
    splits = text_splitter.split_documents(all_loaded_documents)
    

    # for i in splits:
    #     print(f'chunk: {i.page_content}')
    #     print('-------------------------')

    # print('-------------------------')
    print(f"Total chunks: {len(splits)}")

    vector_store = Chroma(
        embedding_function=embedding_model,
        persist_directory="my_chroma_db",
        collection_name=product_name
    )
    vector_store.add_documents(splits)
    print(f'the collection name is:{vector_store._collection.name}')
