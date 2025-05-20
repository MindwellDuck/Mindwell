import pandas as pd

# Read the CSV
df = pd.read_csv("/Users/ahmedgouda/Desktop/Mindwell/JournalData/journalDirty.csv")

# Filter: keep only rows where the specified columns are all False
df_filtered = df[
    (df["Answer.f1.excited.raw"] == False) &
    (df["Answer.f1.happy.raw"] == False) &
    (df["Answer.f1.calm.raw"] == False) &
    (df["Answer.f1.proud.raw"] == False) &
    (df["Answer.t1.god.raw"] == False) &
    (df["Answer.f1.satisfied.raw"] == False)
].reset_index(drop=True)

# Rename the main text column to 'text' 
df_filtered = df_filtered.rename(columns={"Answer": "text"})  # Change 'your_text_column' accordingly

# Add a new column 'source' with value 2
df_filtered["source"] = 2

# Keep only 'text' and 'source' columns
df_filtered = df_filtered[["text", "source"]]

# Save to a new CSV
df_filtered.to_csv("/Users/ahmedgouda/Desktop/Mindwell/JournalData/journalClean.csv", index=False)

# Checks how many rows after filtering
print(df_filtered.shape)
df_filtered.head()
