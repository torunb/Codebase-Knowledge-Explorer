import requests
from flask import Flask, jsonify, request
from updated_integration import UpdatedAzureOpenAIIntegration

app = Flask(__name__)

@app.route('/process_code', methods=['POST'])
def process_code():
    """
    API endpoint to process code JSON, send a request to the similarity API, 
    and return original code, explanation, generated code, and similarity score.
    """
    try:
        # Get JSON payload from the request
        data = request.get_json()
        function_code = data.get("function_code")
        caller_functions_code = data.get("callers_functions_code", "")  # Optional
        callee_functions_code = data.get("calls_functions_code", "")  # Optional

        if not function_code:
            return jsonify({"error": "The 'function_code' field is required."}), 400

        # Initialize Azure OpenAI integration
        azure_integration = UpdatedAzureOpenAIIntegration()

        # Generate explanation
        explanation = azure_integration.get_explanation(function_code, caller_functions_code, callee_functions_code)

        # Generate new code based on the explanation
        generated_code = azure_integration.get_code(explanation)

        # Prepare payload for similarity API
        similarity_payload = {
            "original_code": function_code,
            "generated_code": generated_code,
            "explanation": explanation
        }

        # Send request to the similarity API
        similarity_api_url = "http://127.0.0.1:5001/similarity"
        similarity_response = requests.post(similarity_api_url, json=similarity_payload)

        if similarity_response.status_code != 200:
            return jsonify({"error": f"Similarity API error: {similarity_response.text}"}), 500

        # Create the final response
        response = {
            "original_code": function_code,
            "explanation": explanation,
            "generated_code": generated_code,
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
