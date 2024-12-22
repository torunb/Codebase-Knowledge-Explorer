from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

app = Flask(__name__)

# Load CodeBERT once to reuse
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Function to encode code snippet
def encode_code_snippet(snippet, tokenizer):
    return tokenizer(
        snippet,
        padding='max_length',
        max_length=512,  # CodeBERT's token limit
        truncation=True,
        return_tensors="pt"
    )

# Function to get embeddings
def get_embedding(snippet, tokenizer, model, device="cpu"):
    encoded = encode_code_snippet(snippet, tokenizer)
    encoded = {key: value.to(device) for key, value in encoded.items()}
    with torch.no_grad():
        embedding = model(**encoded).last_hidden_state.mean(dim=1)  # Mean pooling
    return embedding

# Function to calculate cosine similarity
def calculate_similarity(embedding1, embedding2):
    return F.cosine_similarity(embedding1, embedding2).item()

# API Route for similarity
@app.route('/similarity', methods=['POST'])
def similarity():
    try:
        # Parse JSON input
        data = request.get_json()
        code1 = data.get('original_code', None)
        code2 = data.get('generated_code', None)
        explanation = data.get('explanation', None)

        if not code1 or not code2:
            return jsonify({"error": "Both 'code1' and 'code2' fields are required."}), 400

        # Process embeddings
        embedding1 = get_embedding(code1, tokenizer, model, device)
        embedding2 = get_embedding(code2, tokenizer, model, device)

        # Calculate similarity
        similarity_score = calculate_similarity(embedding1, embedding2)
        similarity_score = round(similarity_score, 2)
        print(f"Similarity Score: {similarity_score}")
        return jsonify({
            "Confidence score": similarity_score,
            "Explanation": explanation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":  
    app.run(host="0.0.0.0", port=5001, debug=True)
