import logging
import json
from typing import List, Dict, Optional, Generator, Union
from langchain.chains import RetrievalQA
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from ..models.pydantic_models import PolicyResponse
from ..services.rag_pipeline import rag_pipeline_service_instance

logger = logging.getLogger(__name__)

class LLMService:
    """
    A service class for handling interactions with a language model, specifically designed for policy-related queries.
    This class manages the retrieval of relevant documents and the generation of responses based on those documents.
    """

    def __init__(self):
        """
        Initializes the LLMService with a retriever and a language model.
        """
        if not rag_pipeline_service_instance:
            raise RuntimeError("RAG Pipeline Service is not initialized.")

        self.retriever = rag_pipeline_service_instance.get_retriever()
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.2)

    def _build_prompt(self, context_docs: List[Document], question: str, chat_history: List[Dict[str, str]]) -> str:
        """
        Constructs a prompt for the language model based on the provided context documents, question, and chat history.

        Args:
            context_docs (List[Document]): List of documents providing context for the question.
            question (str): The question to be answered.
            chat_history (List[Dict[str, str]]): History of the chat conversation.

        Returns:
            str: The constructed prompt.
        """
        context_texts = []

        for i, doc in enumerate(context_docs):
            logger.debug(f"Retrieved doc metadata: {doc.metadata}")
            logger.debug(f"Document content snippet: {doc.page_content[:200]}")
            source = doc.metadata.get("source", "unknown.md").replace(".md", "").capitalize()
            snippet = f"[{i + 1}] Source: {source}_Policy.md\n---\n{doc.page_content.strip()}"
            context_texts.append(snippet)

        context = "\n\n".join(context_texts)

        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                You are a strict policy-answering assistant. You must answer questions using ONLY the provided context
                (which consists of policy documents). You are not allowed to guess, merge, or combine data across different
                documents unless they clearly agree.

                ### INSTRUCTIONS (MUST FOLLOW):

                1. Use ONLY the context. No outside knowledge.
                2. If different documents provide different answers, DO NOT merge them.
                3. If conflicting information is found, STOP and ask the user which policy (e.g., Refund or Return) they are referring to.
                4. NEVER mention file names, document titles, or technical metadata.
                5. If the answer isn't clearly in the context, respond with: "insufficient context".
                6. You must respond in this exact JSON format:

                EXAMPLE SCENARIO:

                Context: [1] "Refund Policy: Customer support is available via email and live chat " [2]
                "Return Policy: Customer support is available 24/7 via chatbot." Question: At what times is customer support
                available? Correct Answer: "summary": "Customer support availability depends on the specific policy. Please
                specify whether you're referring to the Refund or Return policy.", "bullets": []

                END OF EXAMPLE SCENARIO
                """
            ),
            HumanMessagePromptTemplate.from_template(
                "{recent_history}\n\nContext:\n{context}\n\nQuestion:\n{question}\n\n"
                "Think step-by-step. Extract only facts from the context above. Do NOT guess. "
                "Respond in this JSON format:\n"
                "{{\"summary\": \"...\", \"bullets\": [\"...\", \"...\"]}}"
            )
        ])

        formatted_prompt = prompt_template.format(
            context=context,
            question=question,
            recent_history=chat_history
        )

        return formatted_prompt

    def _get_filtered_documents(
        self,
        question: str,
        chat_history: List[Dict[str, str]],
        filter_on_metadata: Optional[Dict[str, str]] = None
    ) -> List[Document]:
        """
        Retrieves documents relevant to the question, optionally filtering based on metadata.

        Args:
            question (str): The question for which relevant documents are to be retrieved.
            chat_history (List[Dict[str, str]]): History of the chat conversation.
            filter_on_metadata (Optional[Dict[str, str]]): Optional metadata to filter documents.

        Returns:
            List[Document]: List of relevant documents.
        """
        retriever = self.retriever
        if filter_on_metadata:
            retriever = rag_pipeline_service_instance.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3, "filter": filter_on_metadata}
            )
        logger.info(f"Retrieving documents for: '{question}' with filter: {filter_on_metadata}")
        return retriever.get_relevant_documents(question)

    def stream_query_response(
        self,
        question: str,
        chat_history: List[Dict[str, str]],
        filter_on_metadata: Optional[Dict[str, str]] = None
    ) -> Generator[Union[PolicyResponse], None, None]:
        """
        Streams the response to a query by generating a prompt and invoking the language model.

        Args:
            question (str): The question to be answered.
            chat_history (List[Dict[str, str]]): History of the chat conversation.
            filter_on_metadata (Optional[Dict[str, str]]): Optional metadata to filter documents.

        Yields:
            PolicyResponse: The response from the language model.
        """
        try:
            docs = self._get_filtered_documents(question, chat_history, filter_on_metadata)

            if not docs:
                yield PolicyResponse(summary="insufficient context", bullets=[])
                return

            prompt = self._build_prompt(docs, question, chat_history)
            logger.info("Sending prompt to LLM.")
            logger.debug("Full prompt being sent to LLM:")
            response = self.llm.invoke(prompt)
            logger.info("LLM returned response.")

            try:
                parsed = PolicyResponse.model_validate_json(response.content)
                yield parsed
            except Exception as e:
                logger.warning(f"Failed to parse LLM response as PolicyResponse. Error: {e}")
                yield PolicyResponse(summary="Error parsing model response.", bullets=[str(e)])

        except Exception as e:
            logger.error(f"Exception in LLMService: {e}", exc_info=True)
            yield PolicyResponse(summary="Error generating response", bullets=[str(e)])

try:
    llm_service_instance = LLMService()
except Exception as e:
    logger.critical(f"Failed to initialize LLMService: {e}")
    llm_service_instance = None




