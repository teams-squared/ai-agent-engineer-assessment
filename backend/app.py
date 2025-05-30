# WRITE YOUR PYTHON CODE BELOW
# --------------------------------------------------------------------------------------------------------------------

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from src.document_processing import load_and_split_documents
from src.vectore_store_processing import get_vector_store

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)


@app.route('/query', methods=['POST'])
def query_policy():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400

    try:
        splitted_docs = load_and_split_documents()
        print(splitted_docs)
        vectorstore = get_vector_store(OPENAI_API_KEY)
        return jsonify({"Message": "vector store created"})
    except Exception as e:
        return jsonify({
            "summary": "Error processing query",
            "bullets": [
                f"Error: {str(e)}"
            ]
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)