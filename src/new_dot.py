import ollama
from tqdm import tqdm
import json

prompts = ["""Understand the following definitions:
    All or Nothing Thinking/Polarized Thinking: I view a situation, a person or an event in “either-or” terms, fitting them into only two extreme categories instead of on a continuum.
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
"What cognitive distortions are present in the speech? Please answer with a maximum of two cognitive distortions separated by a comma and stick to the ones defined earlier.", ]

def analyze_text_with_ollama(text: str) -> str:
    prompts[1] = "Given the following text, answer the questions in my following messages.\n\n" + text
    messages=[
            {"role": "system", "content": "You are a therpaist specializing in cognitive behavioural therapy."},
    ]
    for prompt in tqdm(prompts):
        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(model="deepseek-r1:14b", messages=messages, options={'temperature': 0, 'max_tokens': 1024})
        messages.append({"role": "assistant", "content": response['message']['content']})
    return response['message']['content']

def diagnose_text(data: list[dict[str, str]]):
    for i, d in enumerate(tqdm(data)):
        wc = len(d['text'].split())
        if (wc > 250 or wc < 4):
            continue
        parts = analyze_text_with_ollama(d['text']).split("</think>\n\n", 1)
        think = parts[0].replace("<think>\n", "").strip()
        labels = parts[1].strip()
        data[i]['thinking'] = think
        data[i]['output'] = labels
        data[i]['state'] = 'filtered'
    return data
