import pandas as pd

def calculate_average(file_path, column_index=None, column_name=None):
    # Load the CSV file
    data = pd.read_csv(file_path)
    
    # Determine the column to compute average for
    if column_index is not None:
        target_column = data.iloc[:, column_index]
    elif column_name is not None:
        target_column = data[column_name]
    else:
        raise ValueError("Either column_index or column_name must be provided.")
    
    # Compute and return the average
    return target_column.mean()

# Example usage:
file_path = '/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/results/cke_scores_without_cg.csv'
average = calculate_average(file_path, column_index=1)  # Replace with your desired column index
print("Average:", average)
