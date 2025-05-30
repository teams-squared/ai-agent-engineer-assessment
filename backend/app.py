# WRITE YOUR PYTHON CODE BELOW
# --------------------------------------------------------------------------------------------------------------------

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/query', methods=['POST'])
def query_policy():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400

    try:
        parsed = {
                    "summary": "Refunds for digital products are not allowed once the license is activated.",
                    "bullets": [
                        "Refund requests must be made within 14 days.",
                        "Product must be unused and license unactivated.",
                        "Partial refunds are possible after 14 days."
                    ]
                }
        return jsonify(parsed)
    except Exception as e:
        return jsonify({
            "summary": "Error processing query",
            "bullets": [
                f"Error: {str(e)}"
            ]
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)