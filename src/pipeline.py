"""
pipeline implementation
JSON file format:
{
    text,
    distorted_part,
    state: labelled | unlabelled | filtered,
    label: [label1, label2],
    source: llm[kind] | ground | sm
}
"""

import json
import csv
import os
import new_dot

# JSON file constants
TEXT = 'text'
DISTORTED_PART = 'distorted_part'
STATE = 'state'
# states
LABELLED = 'labelled'
UNLABELLED = 'unlabelled'
FILTERED = 'filtered'

LABEL = 'label'
SOURCE = 'source'
# SOURCES
SM = 'SM'
LLM = 'LLM'
GROUND = 'ground'
# Where data is stored
DATA_DIR = '../data'

def convert_csv_to_json(csv_file: str, json_file: str):
    """
    Convert a CSV file to a JSON file.
    Args:
        csv_file (str): Path to the input CSV file.
        json_file (str): Path to the output JSON file.
    """
    data: list[dict[str, str]] = []
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    with open(json_file, mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_data() -> list[dict[str, str]]:
    """
    read data from the data directory
    """
    for file in os.listdir(DATA_DIR):
        if file.endswith('.csv'):
            csv_file = os.path.join(DATA_DIR, file)
            json_file = os.path.join(DATA_DIR, file.replace('.csv', '.json'))
            convert_csv_to_json(csv_file, json_file)
            os.remove(csv_file)
            print(f"Converted {csv_file} to {json_file}")
    data: list[dict[str,str]] = []
    for file in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, file), 'r', encoding='utf-8') as f:
            data.extend(json.load(f))
    return data

data = read_data()
def filter_list(data: list[dict[str, str]], key: str, value: str) -> list[dict[str, str]]:
    """Filter list based on key and value"""
    return [d for d in data if d[key] == value]

labelled = filter_list(data, STATE, LABELLED)
unlabelled = filter_list(data, STATE, UNLABELLED)
filtered = filter_list(data, STATE, FILTERED)

filtered.extend(new_dot.diagnose_text(unlabelled))
