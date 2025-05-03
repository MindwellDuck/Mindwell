import ollama
from tqdm import tqdm
import json

prompts = ["""Understand the following definitions:
    All or Nothing Thinking: I view a situation, a person or an event in “either-or” terms, fitting them into only two extreme categories instead of on a continuum.
    Fortune telling: I predict the future in negative terms and believe that what will happen will be so awful that I will not be able to stand it.
    Emotional reasoning:  I believe my emotions reflect reality and let them guide my attitudes and judgments.
    Labeling/Global Labeling: I put a fixed, global label, usually negative, on myself or others.
    Mental Filter: I pay attention to one or a few details and fail to see the whole picture.
    Mind reading: I believe that I know the thoughts or intentions of others (or that they know my thoughts or intentions) without having sufficient evidence
    Overgeneralization: I take isolated negative cases and generalize them, transforming them in a never-ending pattern, by repeatedly using words such as “always”, “never”, “ever”, “whole”, “entire”, etc
    Personalization: I assume that others’ behaviors and external events concern (or are directed to) myself without considering other plausible explanations.
    Should statements (also “musts”, “oughts”, “have tos”): I tell myself that events, people’s behaviors, and my own attitudes “should” be the way I expected them to be and not as they really are.
    Blaming (others or oneself): I direct my attention to others as sources of my negative feelings and experiences, failing to consider my own responsibility; or, conversely, I take responsibility for others’ behaviors and attitudes.
    What if?: I keep asking myself questions such as “what if something happens?”
    Discounting the positive: I disqualify positive experiences or events insisting that they do not count.
    Magnification/minimization: I evaluate myself, others, and situations placing greater importance on the negatives and/or placing much less importance on the positives.
    Jumping to conclusions (also called arbitrary inference): I draw conclusions (negative or positive) from little or no confirmatory evidence.
    Unfair comparisons: I compare myself with others who seem to do better than I do and place myself in a disadvantageous position.""",
"", # left empty for the text to be analyzed.
"What is this person thinking or imagining?",
"Which thoughts or opinions are subjective and which are objective?",
"What makes this person think the thought his thought is true?",
"Is there cognitive distortion in the speech?",
"What cognitive distortions are present in the speech? Please answer with a maximum of two cognitive distortions in lower case letters seperated by a comma like such [DISTORTION1, DISTORTION2].",
]

def analyze_text_with_ollama(text: str) -> str:
    prompts[1] = "Given the following text, answer the questions in my following messages.\n\n" + text
    messages=[
            {"role": "system", "content": "You are a therpaist specializing in cognitive behavioural therapy."},
    ]
    for prompt in tqdm(prompts):
        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(model="deepseek-r1:14b", messages=messages, options={'temperature': 0, 'max_tokens': 512})
        messages.append({"role": "assistant", "content": response['message']['content']})
    return response['message']['content']

#do we need to open every file for social media, a loop maybe
#and mark the filtered file?
with open("test.json","r") as file:
    data = json.load(file)

Distortions = [
    "All or Nothing Thinking",
    "Fortune telling",
    "Emotional reasoning",
    "Labeling",
    "Mental Filter",
    "Mind reading",
    "Overgeneralization",
    "Personalization",
    "Should statements",
    "Blaming",
    "What if",
    "Discounting the positive",
    "Magnification",
    "Minimization",
    "Jumping to conclusions",
    "Unfair comparisons",
    "Catastrophizing",
]

variations = []
original = {}

for name in Distortions:
    base = name.lower()
    base_no_space = base.replace(' ', '')
    base_hyphen = base.replace(' ', '-')
    base_underscore = base.replace(' ', '_')
    base_title = name.title()

    variations.append(name)
    variations.append(base)
    variations.append(base_no_space)
    variations.append(base_hyphen)
    variations.append(base_underscore)
    variations.append(base_title)

    original[name] = name
    original[base] = name
    original[base_no_space] = name
    original[base_hyphen] = name
    original[base_underscore] = name
    original[base_title] = name

for entry in data:
    if entry.get("state") == "unfiltered":
        labels = analyze_text_with_ollama(entry["text"]).split("</think>\n\n", 1)[1].strip()
        print(labels)
        final_labels = ""
        sep = ""
        for distortion in variations:
            labels = labels.lower()
            if distortion in labels:
                final_labels += sep + distortion
                sep = ", "
                break
                
        entry["labels"] = final_labels
        print(final_labels)
        entry["state"] = "filtered"
        
        
with open("test.json", "w") as file:
    json.dump(data, file, indent=4)


