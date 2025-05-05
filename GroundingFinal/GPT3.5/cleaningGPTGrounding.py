#!/usr/bin/env python3
# clean_modified_text_simple.py

import pandas as pd
import re

# === EDIT THESE PATHS ===
INPUT_CSV   = '/Users/ahmedgouda/Desktop/groundingLLM/FinalGPTMac/grounded_dataset_GPT.csv'
OUTPUT_CSV  = 'finalGPTGroundingDataset.csv'
OUTPUT_JSON = 'finalGPTGroundingDataset.json'
# ============================

def clean_modified_text(s: str) -> str:
    """
    Strip out any trailing '[[' blocks and remove wrapping quotes/whitespace.
    """
    if pd.isna(s):
        return s
    # drop anything from '[[' onward
    cleaned = re.sub(r"\[\[.*", "", s, flags=re.DOTALL)
    # strip wrapping quotes/whitespace
    return cleaned.strip().strip("'\"").strip()


def ensure_prefix(row) -> str:
    """
    For each row:
    - If text and modified_text start with the same first 5 words, keep modified_text.
    - Otherwise prepend the original text to modified_text.
    """
    orig = row['text']
    mod  = row['modified_text']

    if pd.isna(orig) or pd.isna(mod):
        return mod

    orig_words = orig.split()
    mod_words  = mod.split()
    # Compare first 5 words
    if orig_words[:5] == mod_words[:5]:
        return mod

    # They differ: prepend original text
    return orig.strip() + ' ' + mod.strip()


def main():
    # Load the dataset
    df = pd.read_csv(INPUT_CSV)

    # 1) Clean modified_text column
    df['modified_text'] = df['modified_text'].apply(clean_modified_text)

    # 2) Ensure prefix logic comparing first 5 words
    df['modified_text'] = df.apply(ensure_prefix, axis=1)

    # 3) Overwrite source column
    df['source'] = 'GPT3.5Grounding'

    # 4) Write out CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Done — cleaned CSV written to {OUTPUT_CSV}")

    # 5) Write out JSON
    df.to_json(OUTPUT_JSON, orient='records', indent=2, force_ascii=False)
    print(f"✅ Done — cleaned JSON written to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
