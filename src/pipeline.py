#!/usr/bin/env python3
"""
pipeline implementation
JSON file format:
{
    text,
    distorted_part,
    state: labelled | unlabelled | filtered | unfiltered,
    label: label1, label2
    source: llm[kind] | ground | sm
}
"""

import json
import csv
import os
import new_dot
from sys import argv

# JSON file constants
TEXT = 'text'
DISTORTED_PART = 'distorted_part'
STATE = 'state'
# states
LABELLED = 'labelled'
UNLABELLED = 'unlabelled'
FILTERED = 'filtered'
UNFILTERED = 'unfiltered'

LABEL = 'label'
SOURCE = 'source'
# SOURCES
SM = 'SM'
LLM = 'LLM'
GROUND = 'ground'
# Where data is stored, taken as an argument
if len(argv) == 1:
    # print error in red
    print("\033[91mError: No data directory provided.\033[0m")
    exit(1)

DATA_DIR = argv[1]

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

def run_sm_collection():
    if os.system('bash ./get_social_media_data.sh') == 0:
        print("Social media data collection script executed successfully.")
    else:
        print("Social media data collection script execution failed.")

def ensure_length(data: list[dict[str, str]], min_len: int, max_len: int):
    return [d for d in data if min_len <= len(d[TEXT]) <= max_len]

def filter_list(data: list[dict[str, str]], key: str, value: str) -> list[dict[str, str]]:
    return [d for d in ensure_length(data, 4, 250) if d[key] == value]

labelled = filter_list(data, STATE, LABELLED)
unlabelled = filter_list(data, STATE, UNLABELLED)
filtered = filter_list(data, STATE, FILTERED)
unfiltered = filter_list(data, STATE, UNFILTERED)

filtered.extend(new_dot.diagnose_text(unfiltered))
