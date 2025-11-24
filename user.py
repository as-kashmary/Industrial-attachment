from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
# from llama_cpp import Llama
import admin
# import LLm_model
from ollama import Client

def process_query(query:str, product_name: str, embedding_model ) ->str:
    

    vector_store = Chroma(
        collection_name=product_name,
        embedding_function=embedding_model,
        persist_directory="my_chroma_db"                  
    )

    # search documents
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    results = retriever.invoke(query)    

    print(f"The top result:{results[0].page_content}")
    prompt = (
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        "Act as a diligent and helpful virtual assistant.\n"
        "When a user asks a question, carefully read and use the provided context to craft your response.\n"
        "Answer each question thoroughly and efficiently, using a clear and informative paragraph.\n"
        "Prioritize accuracy, professionalism, and relevance in every response.\n"
        "This task is important—please take it seriously.\n"
        "<|start_header_id|>user<|end_header_id|>\n"
        f"Based on the following context:\n\n{results[0].page_content}\n\n"
        f"Answer the question: {query}\n"
        "<|start_header_id|>assistant<|end_header_id|>\n"
    )

    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer 7efd7a1ff40e4dc5b8d19692d5f65af6.9WjyQeyPv2gcmkChoa-MQjxe' }
    )
    prompt_dept=f""" """
    messages = [
    {
        'role': 'user',
        'content': prompt,
    },
    ]
    response = ""
    for part in client.chat('deepseek-v3.1:671b-cloud', messages=messages, stream=True):
        # Get the latest content chunk
        chunk = part['message']['content']
        print(chunk, end='', flush=True)  # Print as it streams
        response += chunk  # Accumulate

    # Strip at the end
    response = response.strip()

    print(response)

    return response

    
    