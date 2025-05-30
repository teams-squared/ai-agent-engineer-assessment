# WRITE YOUR PYTHON CODE BELOW
# --------------------------------------------------------------------------------------------------------------------

from flask import Flask, request, jsonify
from src.document_processing import load_and_split_documents

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
        return jsonify({"Message": "splitting completed"})
    except Exception as e:
        return jsonify({
            "summary": "Error processing query",
            "bullets": [
                f"Error: {str(e)}"
            ]
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)