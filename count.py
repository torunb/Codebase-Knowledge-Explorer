import os

def count_files_in_folder(folder_path):
    try:
        # List all entries in the directory
        entries = os.listdir(folder_path)
        
        # Count only files (not directories)
        file_count = sum(1 for entry in entries if os.path.isfile(os.path.join(folder_path, entry)))
        
        return file_count
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
folder_path = "/Users/borantorun/Documents/GitHub/Codebase-Knowledge-Explorer/test_jsons"
file_count = count_files_in_folder(folder_path)

if file_count is not None:
    print(f"The folder contains {file_count} files.")
