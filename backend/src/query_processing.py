from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from models.response_models import PolicyAnswer

QUESTION_TMPL = (
    "You are a policy assistant. Use ONLY the provided context to answer the question.\n"
    "If the answer isn't in the context, respond with 'insufficient context'.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Format Instructions:\n{format_instructions}"
)

def get_output_parser():
    """Get output parser for structured response"""
    return PydanticOutputParser(pydantic_object=PolicyAnswer)

def generate_response(question, context, openai_api_key):
    """Generate response using LLM"""
    output_parser = get_output_parser()
    format_instructions = output_parser.get_format_instructions()
    
    prompt = QUESTION_TMPL.format(
        context=context,
        question=question,
        format_instructions=format_instructions
    )
    
    llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
    return llm.invoke(prompt).content

def parse_response(response_content):
    """Parse LLM response into structured format"""
    output_parser = get_output_parser()
    return output_parser.parse(response_content)