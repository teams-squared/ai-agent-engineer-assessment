from pydantic import BaseModel, Field

class LLMAnswer(BaseModel):
    """Pydantic class to enforce the structured output of the LLM
    """
    summary: str = Field(
        description="A one-sentence direct answer to the user's question, based on the context. It should be factual, concise, and avoid generalizations or extra commentary."
    ) 
    bullets: list[str] = Field(
        description="""A list of 2–5 concise bullet points that support or elaborate on the summary.
            Each point should reflect specific clauses, rules, or conditions extracted from the given policy. 
            Use clear, factual language."""
    ) 