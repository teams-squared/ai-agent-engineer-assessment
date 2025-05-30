# WRITE YOUR PYTHON CODE BELOW
# --------------------------------------------------------------------------------------------------------------------
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv()) # read local .env file

from flask import Flask, request, jsonify

from src.operators.chat_with_data import chat_with_data


app = Flask(__name__)

@app.route('/', methods=['POST'])
def query():
    """Use this endpoint to ask the bot questions.
    
    Requires json input with field 'question'.
    Returns output json with fields 'summary' (string) and 'bullets' (list of strings)
    """
    input = request.get_json()
    
    # Basic validation
    if not input or 'question' not in input:
        return jsonify({'error': 'Missing question'}), 400
    
    question = input['question']
    result = chat_with_data(question)
    
    return jsonify(result.model_dump())


app.run()
