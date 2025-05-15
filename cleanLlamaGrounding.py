#!/usr/bin/env python3
"""
clean_modified_text_to_json.py

Reads a CSV with columns: text, source, modified_text, cognitive_distortion
Cleans the 'modified_text' column by extracting only the final
human-written snippet, sets every row's 'source' to "LlamaGrounding",
and writes the result out as a JSON array.
"""

import re
import pandas as pd

# ─── Configure your paths here ───────────────────────────────────────────────
INPUT_CSV  = "/home/g4/Desktop/fineGrounding/fine_grounded_dataset_LLama.csv"
OUTPUT_JSON = "/home/g4/Desktop/fineGrounding/finalLLamagrounding.json"
# ─────────────────────────────────────────────────────────────────────────────

def extract_snippet(raw: str) -> str:
    """
    1) Find 'Modified text:' (case-insensitive).
    2) Take everything after it up to the first blank line.
    3) Strip whitespace, then remove one pair of matching outer quotes.
    """
    m = re.search(r'modified text\s*:\s*', raw, flags=re.IGNORECASE)
    if not m:
        return raw.strip()

    tail = raw[m.end():]
    # split at first blank line
    snippet_block = re.split(r'\r?\n\s*\r?\n', tail, maxsplit=1)[0].strip()

    # strip matching outer quotes
    if (snippet_block.startswith("'") and snippet_block.endswith("'")) or \
       (snippet_block.startswith('"') and snippet_block.endswith('"')):
        snippet_block = snippet_block[1:-1].strip()

    return snippet_block

def clean_and_export(input_path: str, output_path: str) -> None:
    # load CSV
    df = pd.read_csv(input_path)

    # clean modified_text
    df['modified_text'] = df['modified_text'].fillna('').map(extract_snippet)

    # override source
    df['source'] = "LlamaGrounding"

    # export to JSON array
    df.to_json(output_path, orient='records', indent=2, force_ascii=False)
    print(f"Cleaned JSON written to: {output_path}")

if __name__ == "__main__":
    clean_and_export(INPUT_CSV, OUTPUT_JSON)
