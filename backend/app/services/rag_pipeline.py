import os
import logging
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipelineService:
    """
    A service class for managing a Retrieval-Augmented Generation (RAG) pipeline.
    This class handles document loading, splitting, and vector store management for RAG tasks.
    """

    def __init__(self, policies_dir: str = "./policies", persist_directory: str = "./chroma_db_prod"):
        """
        Initializes the RAGPipelineService with directories for policies and vector store persistence.

        Args:
            policies_dir (str): Directory containing policy documents. Defaults to "./policies".
            persist_directory (str): Directory to persist the vector store. Defaults to "./chroma_db_prod".
        """
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable not set.")
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. Cannot initialize OpenAIEmbeddings."
            )

        self.policies_dir = policies_dir
        self.persist_directory = persist_directory
        self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vectorstore = self._load_or_create_vectorstore()
        logger.info("RAGPipelineService initialized successfully.")

    def _load_documents(self) -> List[Document]:
        """
        Loads documents from the specified directory.

        Returns:
            List[Document]: A list of loaded documents.
        """
        logger.info(f"Loading documents from directory: {self.policies_dir}")
        loader = DirectoryLoader(
            self.policies_dir,
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader,
            show_progress=True,
            use_multithreading=True,
            silent_errors=False
        )
        try:
            documents = loader.load()
            if not documents:
                logger.warning(f"No documents found in {self.policies_dir}.")
            else:
                # Add source filename as metadata to each document
                for doc in documents:
                    doc.metadata["source"] = os.path.basename(doc.metadata.get("source", ""))
                logger.info(f"Successfully loaded {len(documents)} document(s).")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents from {self.policies_dir}: {e}", exc_info=True)
            raise

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits documents into smaller chunks for processing.

        Args:
            documents (List[Document]): List of documents to split.

        Returns:
            List[Document]: List of document chunks.
        """
        if not documents:
            return []
        logger.info(f"Splitting {len(documents)} documents into chunks.")
        text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=150)
        split_docs = text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(split_docs)} chunks.")
        return split_docs

    def _create_vectorstore(self) -> Chroma:
        """
        Creates a new vector store from documents.

        Returns:
            Chroma: An instance of the Chroma vector store.
        """
        documents = self._load_documents()
        if not documents:
            logger.warning("No documents loaded, creating an empty vector store.")
            return Chroma(
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory
            )

        docs_chunks = self._split_documents(documents)
        if not docs_chunks:
            logger.warning("No document chunks to embed after splitting. Creating an empty vector store.")
            return Chroma(
                embedding_function=self.embedding_function,
                persist_directory=self.persist_directory
            )

        logger.info(f"Creating new vector store with {len(docs_chunks)} chunks and persisting to {self.persist_directory}.")
        try:
            vectorstore = Chroma.from_documents(
                documents=docs_chunks,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory
            )
            logger.info("Vector store created and persisted successfully.")
            return vectorstore
        except Exception as e:
            logger.error(f"Failed to create and persist vector store: {e}", exc_info=True)
            raise

    def _load_or_create_vectorstore(self) -> Chroma:
        """
        Loads an existing vector store or creates a new one if it doesn't exist.

        Returns:
            Chroma: An instance of the Chroma vector store.
        """
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            logger.info(f"Loading existing vector store from: {self.persist_directory}")
            try:
                return Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_function)
            except Exception as e:
                logger.warning(
                    f"Failed to load existing vector store from {self.persist_directory}: {e}. Attempting to recreate.",
                    exc_info=True
                )
                return self._create_vectorstore()
        else:
            logger.info(f"No existing vector store found at {self.persist_directory} or directory is empty. Creating a new one.")
            return self._create_vectorstore()

    def get_retriever(self, search_type: str = "similarity", search_kwargs: dict = None):
        """
        Creates and returns a retriever from the vector store.

        Args:
            search_type (str): Type of search to perform. Defaults to "similarity".
            search_kwargs (dict): Additional keyword arguments for the search. Defaults to {"k": 3}.

        Returns:
            Retriever: A retriever instance configured with the specified search parameters.
        """
        if search_kwargs is None:
            search_kwargs = {"k": 3}
        logger.info(f"Creating retriever with search_type='{search_type}' and search_kwargs={search_kwargs}")
        return self.vectorstore.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

    def add_documents(self, new_documents: List[Document], split_them: bool = True):
        """
        Adds new documents to the vector store.

        Args:
            new_documents (List[Document]): List of new documents to add.
            split_them (bool): Whether to split the documents into chunks before adding. Defaults to True.
        """
        if not new_documents:
            logger.info("No new documents provided to add.")
            return

        logger.info(f"Adding {len(new_documents)} new documents to the vector store.")
        doc_chunks_to_add = new_documents
        if split_them:
            doc_chunks_to_add = self._split_documents(new_documents)

        if doc_chunks_to_add:
            self.vectorstore.add_documents(doc_chunks_to_add)
            logger.info(f"Successfully added {len(doc_chunks_to_add)} chunks from new documents to the vector store.")
        else:
            logger.info("No chunks to add after processing new documents.")

try:
    rag_pipeline_service_instance = RAGPipelineService()
except ValueError as e:
    logger.critical(f"Failed to initialize RAGPipelineService: {e}. The application might not function correctly.")
    rag_pipeline_service_instance = None
except Exception as e:
    logger.critical(f"An unexpected error occurred during RAGPipelineService initialization: {e}", exc_info=True)
    rag_pipeline_service_instance = None


