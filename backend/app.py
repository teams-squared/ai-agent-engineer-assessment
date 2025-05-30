# WRITE YOUR PYTHON CODE BELOW
# --------------------------------------------------------------------------------------------------------------------

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from src.vectore_store_processing import get_vector_store
from src.query_processing import generate_response, parse_response
from flask_cors import CORS

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

vectorstore = get_vector_store(OPENAI_API_KEY)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

@app.route('/query', methods=['POST'])
def query_policy():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400

    relevant_docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    try:
        response_content = generate_response(question, context, OPENAI_API_KEY)
        parsed = parse_response(response_content)
        return jsonify(parsed.model_dump())
    except Exception as e:
        return jsonify({
            "summary": "Error processing query",
            "bullets": [
                f"Error: {str(e)}",
                f"Context: {context[:200]}..." if context else "No context"
            ]
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)