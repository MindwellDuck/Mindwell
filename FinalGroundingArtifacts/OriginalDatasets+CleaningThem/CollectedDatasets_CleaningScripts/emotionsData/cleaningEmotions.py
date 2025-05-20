import pandas as pd

# Load CSV
df = pd.read_csv("/Users/ahmedgouda/Desktop/Mindwell/emotionsData/emotionsDirty.csv", encoding="ISO-8859-1", skipinitialspace=True)

# Remove rows where 'label' is 1, 2, or 5 as these are the positive emotions
df = df[~df["label"].isin([1, 2, 5])]

# Remove rows with fewer than 30 words in the 'text' column
df = df[df["text"].str.split().apply(len) >= 30]

# Remove rows that contain explicit words and words dealing with more serious issues outside of the scope of the dataset
banned_words = ["suicide", "depression", "depressed", "OCD", "rape", "raped", "PTSD", 
                "post traumatic", "sex", "sexual", "schizophrenia", "sexually", "abuse", "abused",
                "antidepressant", "fox", "BPD", "disorder", "diagnosed"]

df = df[~df["text"].str.contains(r'\b(' + '|'.join(banned_words) + r')\b', case=False, na=False)]

# Keep only 'text' column and add a new 'source' column with value 4
df = df[["text"]]
df["source"] = 4

# Save the cleaned dataset
df.to_csv("cleanedEmotions.csv", index=False, encoding="utf-8")

# Preview results
print(df.shape)
df.head()
