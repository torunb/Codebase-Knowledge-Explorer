import pandas as pd
from scipy.stats import mannwhitneyu

# Load the CSV files
file1 = '/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/results/cke_scores_with_cg.csv'
file2 = '/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/results/cke_scores_without_cg.csv'
file3 = '/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/results/final_copilot_explanations_with_scores.csv'

try:
    # Load the data
    data1 = pd.read_csv(file1, header=None)  # No column headers in file
    data2 = pd.read_csv(file2, header=None)  # No column headers in file
    data3 = pd.read_csv(file3)  # Column headers available in file

    # Extract confidence scores from second column (index 1)
    scores_with_cg = pd.to_numeric(data1.iloc[:, 1], errors='coerce')
    scores_without_cg = pd.to_numeric(data2.iloc[:, 1], errors='coerce')

    # Extract 'BERT SCORE' column from the third file
    bert_scores = pd.to_numeric(data3['BERT SCORE'], errors='coerce')

    # Drop NaN values from the datasets
    scores_with_cg = scores_with_cg.dropna()
    scores_without_cg = scores_without_cg.dropna()
    bert_scores = bert_scores.dropna()

    # Perform Mann-Whitney U test between the first two sets of scores
    stat1, p_value1 = mannwhitneyu(scores_with_cg, scores_without_cg, alternative='two-sided')
    print("Mann-Whitney U test between 'CKE with CG' and 'CKE without CG':")
    print(f"U statistic: {stat1}, p-value: {p_value1}\n")

    # Perform Mann-Whitney U test between 'CKE with CG' and 'BERT SCORE'
    stat2, p_value2 = mannwhitneyu(scores_with_cg, bert_scores, alternative='two-sided')
    print("Mann-Whitney U test between 'CKE with CG' and 'BERT SCORE':")
    print(f"U statistic: {stat2}, p-value: {p_value2}\n")

    # Perform Mann-Whitney U test between 'CKE without CG' and 'BERT SCORE'
    stat3, p_value3 = mannwhitneyu(scores_without_cg, bert_scores, alternative='two-sided')
    print("Mann-Whitney U test between 'CKE without CG' and 'BERT SCORE':")
    print(f"U statistic: {stat3}, p-value: {p_value3}\n")

except KeyError as e:
    print(f"Error: Missing expected column in one of the files: {e}")
except Exception as ex:
    print(f"An error occurred: {ex}")
