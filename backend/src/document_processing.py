from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import POLICY_DIR

def load_and_split_documents():
    """Load and split policy documents"""
    loader = DirectoryLoader(
        POLICY_DIR, 
        glob="*.md", 
        loader_cls=UnstructuredMarkdownLoader, 
        show_progress=True
    )
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    return splitter.split_documents(docs)