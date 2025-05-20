import pandas as pd
import re
import unicodedata
import csv

# Load CSV properly, handling encoding & quotes
df = pd.read_csv("/Users/ahmedgouda/Desktop/Mindwell/psychData/PsychDirty.csv", encoding="ISO-8859-1", skipinitialspace=True, quoting=csv.QUOTE_ALL)

# Ensure correct column name (remove spaces from headers)
df.columns = df.columns.str.strip()

# Drop the first column if it's an index column
if df.columns[0].lower() in ["unnamed: 0", "index"]:
    df = df.drop(columns=[df.columns[0]])

# Fix garbled characters
def fix_unicode(text):
    if isinstance(text, str):
        text = unicodedata.normalize("NFKD", text)  # Normalize Unicode
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    return text

df["Question"] = df["Question"].astype(str).apply(fix_unicode)  # Convert NaN to empty string & clean text

# Remove everything before the first colon `:`
df["Question"] = df["Question"].apply(lambda x: x.split(":", 1)[1].strip() if ":" in x else x)

# Remove rows that contain banned words
banned_words = ["suicide", "depression", "depressed", "OCD", "rape", "raped", "PTSD", 
                "post traumatic", "sex", "sexual", "schizophrenia", "sexually", "abuse", "abused",
                "antidepressant", "fox", "BPD", "disorder", "diagnosed"]

df = df[~df["Question"].str.contains(r'\b(' + '|'.join(banned_words) + r')\b', case=False, na=False)]

# Remove rows with fewer than 15 words or more than 200 words
df = df[df["Question"].str.split().apply(len).between(15, 200)]

# Rename column 'Question' to 'text'
df = df.rename(columns={"Question": "text"})

# Add a new column 'source' with value 1
df["source"] = 1

# Keep only 'text' and 'source' columns
df = df[["text", "source"]]

# Save cleaned dataset
df.to_csv("cleanedPsych.csv", index=False, encoding="utf-8")

# Preview results
print(df.shape)
df.head()
