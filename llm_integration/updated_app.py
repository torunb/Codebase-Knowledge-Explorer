from flask import Flask, jsonify, request
from updated_integration import UpdatedAzureOpenAIIntegration

app = Flask(__name__)

@app.route('/process_code', methods=['POST'])
def process_code():
    """
    API endpoint to process code JSON and return original code, explanation, and generated code.
    """
    try:
        # Get JSON payload from the request
        data = request.get_json()
        function_code = data.get("function_code")
        caller_functions_code = data.get("callers_functions_code")
        callee_functions_code = data.get("calls_functions_code")

        if not function_code or not caller_functions_code or not callee_functions_code:
            return jsonify({"error": "Missing one or more required fields: function_code, caller_functions_code, callee_functions_code"}), 400

        # Initialize Azure OpenAI integration
        azure_integration = UpdatedAzureOpenAIIntegration()

        # Generate explanation
        explanation = azure_integration.get_explanation(function_code, caller_functions_code, callee_functions_code)

        # Generate new code based on the explanation
        generated_code = azure_integration.get_code(explanation)

        # Create the response
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
