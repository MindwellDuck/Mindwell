import pandas as pd

# Load CSV
df = pd.read_csv("/Users/ahmedgouda/Desktop/Mindwell/fbData/fb_unclean.csv", encoding="ISO-8859-1", skipinitialspace=True)

# Define emotions to remove from that dataset, which are the positive ones as these are not the focus of the dataset
emotions_to_remove = [
    "joyful", "proud", "caring", "content", "hopeful", "prepared", "anticipating", 
    "grateful", "surprised", "impressed", "confident", "excited", "nostalgic", 
    "sentimental", "faithful"
]

# Remove rows where the 'emotion' column contains any of the specified values
df = df[~df["emotion"].isin(emotions_to_remove)]

# Remove rows with fewer than 15 words in the 'situation' column
df = df[df["Situation"].str.split().apply(len) >= 15]

# Remove duplicate rows based on 'situation' column
df = df.drop_duplicates(subset=["Situation"], keep="first")

# Keep only 'situation' column and add a new 'source' column with value 3
df = df[["Situation"]].rename(columns={"Situation": "situation"})
df["source"] = 3

# Save the cleaned dataset
df.to_csv("cleanedFB.csv", index=False, encoding="utf-8")

# Preview results
print(df.shape)
df.head()
