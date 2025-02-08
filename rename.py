import os

def rename_files_with_patent(directory):
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):  # Only process .txt files
            # Create new filename with 'patent_' prefix
            new_filename = f"patent_{filename}"
            
            # Create full file paths
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, new_filename)
            
            # Rename the file
            os.rename(old_filepath, new_filepath)
            print(f"Renamed: {filename} → {new_filename}")

# Run the function
directory = "/Users/joshuafield/Documents/Ultra/responses/20241115_113830"
rename_files_with_patent(directory)