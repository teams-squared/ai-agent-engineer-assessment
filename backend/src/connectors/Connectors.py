import os

from langchain_openai import ChatOpenAI

from src.operators import load_markdown


class Connectors:

    llm_client = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0 # for factuality
    )

    context = load_markdown.load_markdown()