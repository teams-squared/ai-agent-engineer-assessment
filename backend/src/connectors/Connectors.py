import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

from src.operators import load_markdown


class Connectors:

    llm_client = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0 # for factuality
    )

    context = load_markdown.load_markdown()

    embeddings_client = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        api_key=os.getenv('OPENAI_API_KEY')
    )

    __vectorstore_client = None

    @classmethod
    def get_vectorstore_client(cls):
        """Singleton method to get the vectorstore client.

        If the vectorstore has been persisted, it's loaded from the directory.
        Otherwise the vectorstore is created by embedding the document chunks created from the provided markdown files.

        Returns:
            _type_: The vectorstore client (Chroma)
        """
        if cls.__vectorstore_client == None:
            print('Creating vectorstore client')
            cls.__vectorstore_client = Chroma(
                embedding_function=cls.embeddings_client,
                persist_directory='vectorstore/'
            )
            if len(cls.__vectorstore_client.get()['documents']) == 0:
                print("Creating vectorstore from markdown.")
                cls.__vectorstore_client = Chroma.from_documents(
                    documents=load_markdown.load_and_chunk_markdown(),
                    embedding=cls.embeddings_client,
                    persist_directory='vectorstore/'
                )

        return cls.__vectorstore_client