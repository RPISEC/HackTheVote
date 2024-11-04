from flask import Flask, render_template, request, jsonify, send_from_directory
from llm_interface import IterativeAIHandler
import hashlib
import time

app = Flask(__name__)

# Also tune this in index.html
EXPECTED_COMPLEXITY = 4

recently_answered = set()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

def verify_proof_of_work(user_input, timestamp, nonce, complexity):
    """Verify the proof of work by checking if the hash meets the complexity requirement."""
    hash_input = f"{user_input}{timestamp}{nonce}"
    hash_output = hashlib.sha256(hash_input.encode()).hexdigest()
    return hash_output.startswith('0' * complexity)


@app.route('/predict', methods=['POST'])
def predict():
    # Extract data from the JSON request
    data = request.get_json()

    # Extract proof-of-work related fields
    req = data.get('question')
    nonce = data.get('nonce')
    timestamp = data.get('timestamp')
    complexity = data.get('complexity')

    # Check if all required fields are provided
    if not req or nonce is None or timestamp is None or complexity is None:
        return jsonify({"error": "Incomplete proof-of-work data"}), 400

    # If complexity is lower than expected, reject the request
    if complexity < EXPECTED_COMPLEXITY:
        return jsonify({"error": "Invalid complexity. Reload the app"}), 400

    # Validate timestamp (ensure it is within an acceptable time window)
    current_time = int(time.time())
    if current_time - timestamp > 30:
        return jsonify({"error": "Proof of work expired"}), 400

    if f"{nonce}_{timestamp}" in recently_answered:
        return jsonify({"error": "Duplicate request"}), 400

    recently_answered.add(f"{nonce}_{timestamp}")

    # Validate proof-of-work
    if not verify_proof_of_work(req, timestamp, nonce, complexity):
        return jsonify({"error": "Invalid proof of work"}), 400

    # All checks passed, proceed with the request
    try:
        response = IterativeAIHandler().handle_request(req)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
