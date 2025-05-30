import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from config import VECTORSTORE_DIR
from .document_processing import load_and_split_documents

def get_vector_store(openai_api_key):
    """Get or create vector store"""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    if os.path.exists(VECTORSTORE_DIR):
        return FAISS.load_local(
            folder_path=VECTORSTORE_DIR,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    
    splitted_docs = load_and_split_documents()
    vectorstore = FAISS.from_documents(splitted_docs, embeddings)
    
    os.makedirs(os.path.dirname(VECTORSTORE_DIR), exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)
    return vectorstore