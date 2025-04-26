import pandas as pd
import re

# Define file paths
input_csv = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingLLama/grounded_dataset_LLama.csv'
output_csv = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingLLama/cleaned_grounded_dataset_LLama.csv'
output_json = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingLLama/cleaned_grounded_dataset_LLama.json'

def extract_modified_text(text):
    """
    Extracts and returns the text that appears after "Modified text:" 
    between the first pair of single quotation marks.
    If no match is found, the original text is returned.
    """
    if not isinstance(text, str):
        return text
    # Pattern: look for "Modified text:" followed by optional whitespace,
    # then a single quote, and capture everything until the next single quote.
    pattern = r"Modified text:\s*'(.*?)'"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

# Read the CSV file into a DataFrame
df = pd.read_csv(input_csv)

# Apply the extraction function to the 'modified_text' column
df['modified_text'] = df['modified_text'].apply(extract_modified_text)

# Save the cleaned DataFrame to a new CSV file
df.to_csv(output_csv, index=False)
print(f"Cleaned CSV file saved as: {output_csv}")

# Convert the cleaned DataFrame to JSON in records orientation and save to a file
json_output = df.to_json(orient='records', indent=2)
with open(output_json, 'w', encoding='utf-8') as f:
    f.write(json_output)
    
print(f"Cleaned JSON file saved as: {output_json}")
