import ollama
from tqdm import tqdm
import json
from sys import argv

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
"What cognitive distortions are present in the speech? Please answer with a maximum of two cognitive distortions from the following list: Distortion.",
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
filename = argv[1]
with open(filename,"r") as file:
    data = json.load(file)

Distortions = [
    "All-or-Nothing Thinking",
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
    "Discounting the positive",
    "What if",
    "Magnification",
    "Minimization",
    "Jumping to conclusions",
    "Unfair comparisons",
    "Catastrophizing",
]

variations = []
original = {}

for name in Distortions:
    current_variations = []
    base = name.lower()
    base_no_space = base.replace(' ', '')
    base_hyphen = base.replace(' ', '-')
    base_underscore = base.replace(' ', '_')
    base_title = name.title()

    current_variations.append(name)
    current_variations.append(base)
    current_variations.append(base_no_space)
    current_variations.append(base_hyphen)
    current_variations.append(base_underscore)
    current_variations.append(base_title)

    variations.append(current_variations)

for entry in data:
    if entry.get("state") == "unfiltered":
        labels = analyze_text_with_ollama(entry["text"]).split("</think>\n\n", 1)[1].strip()
        print(labels)
        final_labels = ""
        sep = ""
        labels = labels.lower()

        for distortion in variations:
            for variation in distortion:
              if variation in labels:
                    final_labels += sep + distortion[0]
                    sep = ", "
                    break

        entry["labels"] = final_labels
        print(final_labels)
        entry["state"] = "filtered"

with open(filename, "w") as file:
    json.dump(data, file, indent=4)
