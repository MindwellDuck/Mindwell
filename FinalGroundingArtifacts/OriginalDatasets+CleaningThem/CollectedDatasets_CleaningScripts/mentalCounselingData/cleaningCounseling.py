import pandas as pd
import re
import unicodedata

# Load CSV properly using 'ISO-8859-1' to fix encoding issues
df = pd.read_csv("/Users/ahmedgouda/Desktop/Mindwell/mentalCounselingData/counselingDataDirty.csv", encoding="ISO-8859-1", skipinitialspace=True)

# Ensure correct column name by removing spaces
df.columns = df.columns.str.strip()

# 3. Fix garbled characters (like Äô turning into normal characters)
def fix_unicode(text):
    if isinstance(text, str):
        text = text.encode("utf-8", "ignore").decode("utf-8")  # Convert to UTF-8 properly
        text = unicodedata.normalize("NFKD", text)  # Normalize Unicode
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove any remaining non-ASCII characters
    return text

df["Context"] = df["Context"].apply(fix_unicode)

# Remove duplicate paragraphs
df = df.drop_duplicates(subset=["Context"], keep="first").reset_index(drop=True)

# Function to remove questions
def remove_questions(text):
    sentences = re.split(r'(?<=[.!?])\s+', str(text))  # Split by punctuation
    cleaned_sentences = [s for s in sentences if not s.strip().endswith("?")]  # Remove ? endings
    return " ".join(cleaned_sentences)  # Reassemble paragraph

df["Context"] = df["Context"].apply(remove_questions)

# Remove rows with fewer than 15 words
df = df[df["Context"].str.split().apply(len) >= 15]

# Remove rows with more than 200 words
df = df[df["Context"].str.split().apply(len) <= 200]

# Remove rows that contain banned words
banned_words = ["suicide", "depression", "depressed", "OCD", "rape", "raped", "PTSD", "post traumatic",  "sex", 
                "sexual", "schizophrenia", "sexually", "abuse", "abused"]

# Use case-insensitive filtering
df = df[~df["Context"].str.contains(r'\b(' + '|'.join(banned_words) + r')\b', case=False, na=False)]

# Add a new column 'label' with value 0 for this source
df["label"] = 0

# Save cleaned dataset
df.to_csv("cleanedCounsel.csv", index=False, encoding="utf-8")

# Preview results
print(df.shape)
df.head()
