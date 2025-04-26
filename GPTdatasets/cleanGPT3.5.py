import pandas as pd

# File paths (update as needed)
input_csv = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingGPT3.5/cleanPilotGroundGPT.csv'
output_json = '/Users/ahmedgouda/Desktop/groundingdrive/SamplesForTestingModels/TestGroundingGPT3.5/groundedGPT3.5.json'

# Read the CSV file
df = pd.read_csv(input_csv)


# Remove any rows where 'modified_text' contains square brackets [ or ]
# The regex \[|\] matches either an opening or closing square bracket.
df_clean = df[~df['modified_text'].str.contains(r"\[|\]", na=False)]

# Convert the cleaned DataFrame to JSON format (records orientation)
json_output = df_clean.to_json(orient='records', indent=2)

# Write the JSON output to a file
with open(output_json, 'w', encoding='utf-8') as f:
    f.write(json_output)

print(f"Cleaned JSON file saved as: {output_json}")
