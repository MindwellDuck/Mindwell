import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import time
import re
import os

# File paths
input_file = '/home/g4/Desktop/groundingLLM/FinalLLAMA/smoll10k.csv'
output_folder = '/home/g4/Desktop/groundingLLM/FinalLLAMA'
output_file = os.path.join(output_folder, 'grounded_dataset_LLama.csv')

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load existing progress if available
try:
    df_existing = pd.read_csv(output_file)
    processed_texts = set(df_existing["text"].tolist())  # Store processed texts
except FileNotFoundError:
    df_existing = None
    processed_texts = set()

# Load the full dataset
df = pd.read_csv(input_file)

# Cognitive distortions list
cognitive_distortions = [
    "All or Nothing Thinking/Polarized Thinking",
    "Fortune Telling",
    "Emotional Reasoning",
    "Labeling/Global Labeling",
    "Mental Filter",
    "Mind Reading",
    "Overgeneralization",
    "Personalization",
    "Should Statements",
    "Blaming",
    "What if?",
    "Discounting the Positive",
    "Magnification/Minimization",
    "Jumping to Conclusions",
    "Unfair Comparisons"
]

# Dictionary of cognitive distortions and their definitions
cognitive_distortion_definitions = {
    "All or Nothing Thinking/Polarized Thinking": "view a situation, a person or an event in 'either-or' terms, fitting them into only two extreme categories.",
    "Fortune Telling": "predict the future in negative terms and believe that what will happen will be unbearable.",
    "Emotional Reasoning": "believe their emotions reflect reality and let them guide their attitudes and judgments.",
    "Labeling/Global Labeling": "put a fixed negative label on themselves or others.",
    "Mental Filter": "pay attention to one or a few details and fail to see the whole picture.",
    "Mind Reading": "believe that they know the thoughts or intentions of others without sufficient evidence.",
    "Overgeneralization": "take isolated negative cases and generalize them, using words like 'always,' 'never,' 'whole,' 'entire,' etc.",
    "Personalization": "believe that others’ behaviors and external events concern themselves without considering other explanations.",
    "Should Statements": "tell themselves that events, people’s behaviors, and their own attitudes 'should' be the way they expected, not as they are.",
    "Blaming": "assign responsibility for negative experiences solely to others or themselves.",
    "What if?": "continuously ask hypothetical questions focusing on potential negative outcomes.",
    "Discounting the Positive": "disqualify positive experiences or events as unimportant or irrelevant.",
    "Magnification/Minimization": "overemphasize the negatives and downplay positives in evaluations.",
    "Jumping to Conclusions": "draw negative conclusions from insufficient evidence.",
    "Unfair Comparisons": "compare themselves unfavorably with others who seem better off."
}

# Updated system instructions for rewriting text
system_message = """
You are an expert at rewriting text to subtly introduce a cognitive distortion while keeping the original writing style and tone.
Your task is to take an existing human-written thought and make minimal, subtle modifications so that it exhibits the given cognitive distortion.
Ensure that:
- The tone, style, and flow of the original text remain unchanged.
- The distortion is added in a way that feels natural and not forced.
- The modification is subtle and does not completely alter the original meaning.
- The person in the text must not realize they are thinking in a distorted way.
"""

# ----- Load your local LLaMA model -----
model_name = "/home/g4/Llama-3.2-3B-Instruct"  # Use your working model directory
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
# -----------------------------------------

# Function to modify the original text using the LLaMA model
def modify_text(original_text, distortion):
    if pd.isna(original_text) or not isinstance(original_text, str) or original_text.strip() == "":
        return original_text  # Skip empty rows

    distortion_definition = cognitive_distortion_definitions[distortion]
    user_message = (
        f"Modify the following human-written text so that it clearly and naturally exhibits the cognitive distortion '{distortion}'. "
        f"Expand the context to make the text align with this distortion while preserving the original tone and style. DO NOT USE BIG FANCY WORDS. BE AS HUMAN AND AS CLOSE TO THE ORIGINAL AS POSSIBLE. DO NOT FIX THE ORIGINAL TEXT'S GRAMMAR.\n"
        f"You should add 1 to 3 sentences at the end in the same style as the original to very subtly display the distortion and add context, but the core writing should feel unaltered.\n\n"
        f"Remember, if a person has the cognitive distortion of '{distortion}', that means they '{distortion_definition}'.\n\n"
        f"Do not include the name of the cognitive distortion or its definition in the final text.\n"
        f"Here is the text to modify:\n"
        f"'{original_text}'\n\n"
        f"Modified text:"
    )
    # Combine system and user instructions into one prompt
    prompt = system_message + "\n" + user_message

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    try:
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.7
        )
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Use the entire generated text as the modified text.
        modified_text = generated.strip()
        return modified_text
    except Exception as e:
        print(f"Error generating text for distortion {distortion}: {e}")
        return original_text  # Return original text if there's an error

# Function to save dataset incrementally
def save_dataset(dataframe, output_file):
    dataframe.to_csv(output_file, index=False, encoding="utf-8")

# Initialize new columns for modified text and cognitive distortion
df["modified_text"] = ""
df["cognitive_distortion"] = ""

for index, row in df.iterrows():
    original_text = row["text"]
    # Skip if already processed
    if original_text in processed_texts:
        continue

    # Cycle through the distortions in order
    distortion = cognitive_distortions[index % len(cognitive_distortions)]
    modified_text = modify_text(original_text, distortion)

    # Store the modified data in the DataFrame
    df.at[index, "modified_text"] = modified_text
    df.at[index, "cognitive_distortion"] = distortion

    # Save progress every 5 rows
    if index % 5 == 0:
        if df_existing is not None:
            df_combined = pd.concat([df_existing, df.iloc[:index+1]], ignore_index=True)
        else:
            df_combined = df.iloc[:index+1]
        save_dataset(df_combined, output_file)

    print(f"Processed {index + 1}/{len(df)}: {distortion}")
    time.sleep(1)  # Pause between requests

# Final save: merge any previously saved data with the current run
if df_existing is not None:
    df_combined = pd.concat([df_existing, df], ignore_index=True)
else:
    df_combined = df

save_dataset(df_combined, output_file)
print(f"Processing completed. Dataset saved to {output_file}")
