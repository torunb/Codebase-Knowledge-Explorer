from flask import Flask, jsonify, request
from integration import generate_explanation_and_code

app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate():
    """
    API endpoint to generate explanation and code.
    """
    try:
        explanation_data, code_data, original_code = generate_explanation_and_code()

        # Combine all outputs into a single response
        response = {
            "original_code": original_code,
            "explanation": explanation_data,
            "generated_code": code_data
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/original_code', methods=['GET'])
def get_original_code():
    """
    API endpoint to get the original code.
    """
    try:
        _, _, original_code = generate_explanation_and_code()
        return jsonify({"original_code": original_code}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/explanation', methods=['GET'])
def get_explanation():
    """
    API endpoint to get the explanation for the code.
    """
    try:
        explanation_data, _, _ = generate_explanation_and_code()
        return jsonify({"explanation": explanation_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generated_code', methods=['GET'])
def get_generated_code():
    """
    API endpoint to get the generated code.
    """
    try:
        _, code_data, _ = generate_explanation_and_code()
        return jsonify({"generated_code": code_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
