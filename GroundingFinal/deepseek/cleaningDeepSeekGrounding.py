import re
import json
import pandas as pd

def clean_modified_text(text: str) -> str:
    """
    Remove any <think>...</think> blocks and outer square brackets from the text,
    then collapse newlines and extra spaces into single spaces.
    """
    if pd.isna(text):
        return text

    # 1. Remove <think>...</think> and everything between (including newlines)
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

    # 2. Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    # 3. If wrapped in [ ... ], unwrap it
    if cleaned.startswith('[') and cleaned.endswith(']'):
        cleaned = cleaned[1:-1].strip()

    # 4. Collapse any sequence of whitespace into a single space
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return cleaned

def main(input_csv: str, output_json: str):
    # 1) Load and clean
    df = pd.read_csv(input_csv)
    df['modified_text'] = df['modified_text'].apply(clean_modified_text)

    # 2) Force all sources
    df['source'] = 'groundingDeepSeek'

    # 3) Convert to list of dicts
    records = df.to_dict(orient='records')

    # 4) Write pretty JSON with utf-8 encoding and real unicode
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned and wrote pretty JSON to {output_json}")

if __name__ == "__main__":
    main("/Users/ahmedgouda/Desktop/deepseekFR/final_dataset_groundedDeepSeek.csv", "finalDeepseek_grounding.json")
