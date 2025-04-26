import pandas as pd
import re

# File paths (adjust if necessary)
input_csv = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingDeepSeek/final_cleaned_grounded_dataset_DeepSeek.csv'
output_csv = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingDeepSeek/fffinal_final_cleaned_grounded_dataset_DeepSeek.csv'
output_json = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingDeepSeek/fffinal_final_cleaned_grounded_dataset_DeepSeek.json'

def clean_modified_text(text):
    if not isinstance(text, str):
        return text
    
    # Remove anything including and between <think> and </think>
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Remove all square brackets [ and ]
    text = text.replace('[', '').replace(']', '')
    
    # Remove all double quotation marks
    text = text.replace('"', '')
    
    # Remove any empty new lines (i.e., multiple newlines become a single newline)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    # Return the cleaned text, stripping leading/trailing whitespace
    return text.strip()

# Read the CSV file
df = pd.read_csv(input_csv)

# Apply the cleaning function to the 'modified_text' column
df['modified_text'] = df['modified_text'].apply(clean_modified_text)

# Save the cleaned DataFrame to a new CSV file
df.to_csv(output_csv, index=False)
print(f"Cleaned CSV file saved as: {output_csv}")

# Convert the cleaned DataFrame to JSON (records orientation) and save
json_output = df.to_json(orient='records', indent=2)
with open(output_json, 'w', encoding='utf-8') as f:
    f.write(json_output)
    
print(f"Cleaned JSON file saved as: {output_json}")
