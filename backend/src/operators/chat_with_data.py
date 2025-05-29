from langchain.prompts import PromptTemplate

from src.connectors.Connectors import Connectors
from src.models.LLMAnswer import LLMAnswer


prompt_template = PromptTemplate(
    input_variables=["question", "context"],
    template="""You are a polite QnA bot.
    You must answer the user's question using ONLY the provided context.
    If you cannot figure out the answer using the provided context, respond with 'insufficient context'.
    Context: ```
    {context}
    ```

    Question: ```
    {question}
    ```
    """
)

structured_llm = Connectors.llm_client.with_structured_output(LLMAnswer)

def chat_with_data(question: str) -> LLMAnswer:
    """Pass in a question and get the answer from the bot.

    Args:
        question (str): The user's question.

    Returns:
        LLMAnswer: The generated answer.
    """
    result = structured_llm.invoke(
        prompt_template.format(
            question= question,
            context = Connectors.context
        )
    )
    
    return result