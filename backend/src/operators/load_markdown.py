import os

from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.schema.document import Document


def load_markdown() -> str:
    """Reads the provided markdown files and loads it all into a string

    Returns:
        str: All text of all markdown files.
    """
    all_text = ""
    DIRECTORY = "policies"
    for filename in os.listdir(DIRECTORY):
        with open(os.path.join(DIRECTORY, filename), "rt") as f:
            all_text += f.read() + '\n'

    # print("all_text:")
    # print(all_text)

    return all_text

def load_and_chunk_markdown() -> list[Document]:
    """Return chunks of the provided markdown for context.

    The markdown is split by heading.
    This makes sense as the context provided is very small and is neatly separated into headings for different categories.
    Because of this, no chunk overlap is used.
    If required this function can be modified to include document-name as metadata.

    Returns:
        list[Document]: Chunks of context
    """
    all_text = load_markdown()
    markdown_split_defintion = [("#", "heading1")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=markdown_split_defintion)
    docs = splitter.split_text(all_text)
    return docs

