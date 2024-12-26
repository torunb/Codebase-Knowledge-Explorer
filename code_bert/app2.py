import pandas as pd
import os
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

# Load CodeBERT model and tokenizer
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

# Process the CSV file
def process_csv(input_csv, output_csv):
    # Read the input CSV
    df = pd.read_csv(input_csv)

    # Iterate over each row and calculate similarity
    bert_scores = []
    for index, row in df.iterrows():
        original_code = row.get("ORIGINAL CODE")
        generated_code = row.get("GENERATED CODE")

        if pd.notna(original_code) and pd.notna(generated_code):
            embedding1 = get_embedding(original_code, tokenizer, model, device)
            embedding2 = get_embedding(generated_code, tokenizer, model, device)
            similarity_score = calculate_similarity(embedding1, embedding2)
            bert_scores.append(round(similarity_score, 2))
        else:
            bert_scores.append(None)  # Handle missing data

    # Add the BERT SCORE column
    df["BERT SCORE"] = bert_scores

    # Save the updated DataFrame to the output CSV
    df.to_csv(output_csv, index=False)
    print(f"Processed file saved to: {output_csv}")

# Input and output file paths
input_csv_path = './code_fetch/final copilot explanations.csv'
output_csv_path = './code_fetch/final_copilot_explanations_with_scores.csv'

# Process the file
process_csv(input_csv_path, output_csv_path)
