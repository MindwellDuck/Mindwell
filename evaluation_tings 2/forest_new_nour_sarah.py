import ollama
import re
import time
from typing import Dict, Any
import pandas as pd
import os
from collections import Counter, defaultdict
import numpy as np


cognitive_forest = {
    "personal_problems_tree": {
        "root": {
            "question": "Is the text about oneself, one's self-worth, abilities, or identity?",
            "yes": "all_or_nothing_question",
            "no": "interpersonal_tree.root"
        },
        "all_or_nothing_question": {
            "question": "Does the text view situations as either 'perfect' or 'complete failures' with no middle ground?",
            "yes": "all_or_nothing_thinking",
            "no": "emotional_reasoning_question"
        },
        "emotional_reasoning_question": {
            "question": "Does the text indicate that emotions are perceptions of reality?",
            "yes": "emotional_reasoning",
            "no": "discounting_positive_question"
        },
        "discounting_positive_question": {
            "question": "Does the text dismiss positive events or achievements as insignificant or undeserved?",
            "yes": "discounting_positive",
            "no": "mental_filter_question"
        },
        "mental_filter_question": {
            "question": "Does the text focus only on negative details while ignoring the bigger picture?",
            "yes": "mental_filter",
            "no": "magnification_question"
        },
        "magnification_question": {
            "question": "Does the text exaggerate negative aspects of situations or minimizes positive ones?",
            "yes": "magnification_minimization",
            "no": "no_distortion"
        },
        "all_or_nothing_thinking": {},
        "emotional_reasoning": {},
        "discounting_positive": {},
        "mental_filter":{},
        "magnification_minimization":{},
        "no_distortion":{},
    },
    "interpersonal_tree": {
        "root": {
            "question": "Does the text primarily involve a situation with your relationships with others (e.g., friends, colleagues, family)?",
            "yes": "mind_reading_question",
            "no": "life_challenges_tree.root"
        },
        "mind_reading_question": {
            "question": "Does the text indicate assumptions of knowing what others think about oneself without evidence?",
            "yes": "mind_reading",
            "no": "blaming_question"
        },
        "blaming_question": {
            "question": "Does the text contain blaming others for ones negative feelings or experiences?",
            "yes": "blaming",
            "no": "personalization_question"
        },
        "personalization_question": {
            "question": "Does the text view people's actions or words to be directed at oneself personally?",
            "yes": "personalization",
            "no": "labeling_question"
        },
        "labeling_question": {
            "question": "Does the text assign fixed, global labels to oneself or others based on specific behaviors (e.g., \"lazy,\" \"failure\")?",
            "yes": "labeling",
            "no": "unfair_comparisons_question"
        },
        "unfair_comparisons_question": {
            "question": "Does the text compare oneself unfavorably to others, assuming they are better than them in every way?",
            "yes": "unfair_comparisons",
            "no": "no_distortion"
        },
        "mind_reading": {},
        "blaming": {},
        "personalization": {},
        "labeling":{},
        "unfair_comparisons":{},
        "no_distortion":{},
    },
    "life_challenges_tree": {
        "root": {
            "question": "Does the text revolve around life challenges, such as future worries or general stress?",
            "yes": "fortune_telling_question",
            "no": "parent_child_tree.root"
        },
        "fortune_telling_question": {
            "question": "Does the text frequently imagine worst-case scenarios and indicate the one believes they will happen?",
            "yes": "fortune_telling",
            "no": "overgeneralization_question"
        },
        "overgeneralization_question": {
            "question": "Does the text isolate negative events making one think 'This always happens' or 'It will never change'?",
            "yes": "overgeneralization",
            "no": "what_if_question"
        },
        "what_if_question": {
            "question": "Do hypothetical questions like 'What if something bad happens?' dominate the text?",
            "yes": "what_if",
            "no": "magnification_minimization_question"
        },
        "magnification_minimization_question": {
            "question":"Does the text exaggerate negative aspects of situations or minimize positive ones?",
            "yes": "magnification_minimization",
            "no": "mental_filter_question"
        },
        "mental_filter_question": {
            "question":"Does the text focus only on negative details while ignoring the bigger picture?",
            "yes": "mental_filter",
            "no": "jumping_to_conclusions_question"
        },
        "jumping_to_conclusions_question": {
            "question": "Does the text indicate drawing a conclusion based on little or no actual evidence?",
            "yes": "jumping_to_conclusions",
            "no": "no_distortion"
        },
        "fortune_telling": {},
        "overgeneralization": {},
        "what_if": {},
        "magnification_minimization":{},
        "mental_filter":{},
        "jumping_to_conclusions":{},
        "no_distortion":{},
    },
    "parent_child_tree": {
        "root": {
            "question": "Does the issue revolve around parental or childhood concerns?",
            "yes": "should_statements_question",
            "no": "no_distortion"
        },
        "should_statements_question": {
            "question": "Do the text include phrases like 'You must...' or 'You should...' excessively?",
            "yes": "should_statements",
            "no": "labeling_question"
        },
        "labeling_question": {
            "question": "Are fixed labels like 'lazy,' 'irresponsible,' or 'failure' used to describe behaviors?",
            "yes": "labeling",
            "no": "jumping_to_conclusions_question"
        },
        "jumping_to_conclusions_question": {
            "question": "Are decisions made based on assumptions rather than evidence or dialogue?",
            "yes": "jumping_to_conclusions",
            "no": "unfair_comparisons_question"
        },
        "unfair_comparisons_question": {
            "question": "Does the text compare oneself unfavorably to others, assuming they are better than them in every way?",
            "yes": "unfair_comparisons",
            "no": "magnification_minimization_question"
        },
        "magnification_minimization_question": {
            "question": "Does the text exaggerate negative aspects of situations or minimize positive ones?",
            "yes": "magnification_minimization",
            "no": "no_distortion"
        },
        "should_statements": {},
        "labeling": {},
        "jumping_to_conclusions": {},
        "unfair_comparisons": {},
        "magnification_minimization": {},
        "no_distortion": {}
    }
}


# ---------------------------------------------------
# Modified helper functions to capture decision paths
# ---------------------------------------------------
def analyze_thought(thought: str, current_node: Dict[str, Any]) -> str:
    """Query DeepSeek-R1 using Ollama with strict yes/no formatting"""
    response = ollama.chat(
        model='deepseek-r1:14b',
        messages=[{
            'role': 'system',
            'content': (
                "Answer ONLY 'yes' or 'no' to this question about thought patterns. "
                "Use the following definitions to be able to reason with them: All or Nothing Thinking/Polarized Thinking, "
                "Fortune telling (catastrophizing), Emotional reasoning, Labeling/Global Labeling, Mental Filter, Mind reading, "
                "Overgeneralization, Personalization, Should statements, Blaming, What if?, Discounting the positive, "
                "Magnification/minimization, and Jumping to conclusions."
            )
        }, {
            'role': 'user',
            'content': f"Thought: {thought}\nQuestion: {current_node['question']}"
        }],
        options={'temperature': 0}
    )
    # extract the yes/no answer
    return parse_response(response['message']['content'].split("</think>\n\n", 1)[1])


def extract_mapping(mapping: str) -> tuple:
    """
   Extract the left-hand and right-hand side of a mapping string formatted as
   "key -> x.y" or "x.y" or "x".
   """
    parts = mapping.split(" -> ")
    if len(parts) == 2:
        value_parts = parts[1].split(".")
        if len(value_parts) == 2:
            return value_parts[0], value_parts[1]
    else:
        parts = mapping.split(".")
        if len(parts) == 2:
            return parts[0], parts[1]
        else:
            return parts[0], ""
    return "", ""


def parse_response(response: str) -> str:
    """Extract yes/no from model response"""
    clean_res = response.strip().lower()
    match = re.search(r'\b(yes|no)\b', clean_res)
    return match.group(0) if match else 'no'


def traverse_tree(thought: str, node: str, decision_tree, tree: str, path=None) -> tuple:
    """Recursive decision tree traversal that also captures the decision path."""
    if path is None:
        path = []
    if 'question' in decision_tree[node]:
        print(f"Q ({tree}.{node}): {decision_tree[node]['question']}")
        path.append(f"Q: {decision_tree[node]['question']}")
    # Leaf node reached
    if 'yes' not in decision_tree[node]:
        print(f"Leaf: {node}")
        path.append(f"Leaf: {node}")
        return node, path
    answer = analyze_thought(thought, decision_tree[node])
    print(f"A: {answer}")
    path.append(f"A: {answer}")
    next_node_key = decision_tree[node]['yes'] if answer == 'yes' else decision_tree[node]['no']
    x = extract_mapping(next_node_key)
    if x[1] != "":
        decision_tree = cognitive_forest[x[0]]
        tree = x[0]
        next_node_key = x[1]
    else:
        next_node_key = x[0]
    return traverse_tree(thought, next_node_key, decision_tree, tree, path)


def identify_distortion(thought: str) -> tuple:
    """For each tree in the forest, traverse it and capture the predicted distortion and the decision path."""
    distortions = {}
    paths = {}
    for tree in cognitive_forest.keys():
        print("--------------------------")
        print(f"Q ({tree}.root): {cognitive_forest[tree]["root"]['question']}")
        answer = analyze_thought(thought, cognitive_forest[tree]["root"])
        print(f"A: {answer}")

        if answer == "yes":
            print(f"Traversing the tree ...")
            distortion, path = traverse_tree(thought, cognitive_forest[tree]["root"]["yes"], cognitive_forest[tree], tree)
            distortions[tree] = distortion
            paths[tree] = path
        else:
            print(f"Skipping the tree ...")
            distortions[tree] = "no_distortion"  
            paths[tree] = [f"Tree skipped: {tree}"]  # Track that tree was skipped
        
        print("--------------------------")

    return distortions, paths

def jaccard_similarity(set1, set2):
    # Calculate Jaccard similarity between two sets
    intersection = set1 & set2  # Intersection of sets
    union = set1 | set2         # Union of sets
    similarity_percentage = (len(intersection) / len(union)) * 100 if len(union) != 0 else 0  # Return as percentage
    return similarity_percentage, intersection

def average_jaccard_percentage_and_flattened_intersections(predictions_runs):
    n = len(predictions_runs)
    total_similarity = 0
    comparisons = 0
    all_intersections = set()  # Use a set to collect unique elements across all intersections

    # Compare every pair of sets in the list
    for i in range(n):
        for j in range(i + 1, n):
            similarity_percentage, intersection = jaccard_similarity(predictions_runs[i], predictions_runs[j])
            total_similarity += similarity_percentage
            all_intersections.update(intersection)  # Add intersection to the set (unique elements)
            comparisons += 1

    # Calculate average similarity as a percentage
    average_similarity = total_similarity / comparisons if comparisons > 0 else 0

    return average_similarity, list(all_intersections)

# --------------------------------------
# Evaluation and saving of metrics
# --------------------------------------
if __name__ == "__main__":
    # Create an output directory for the txt files if it doesn't exist
    os.makedirs("output_paths", exist_ok=True)

    # Dummy ground truth mapping for demonstration (each thought maps to a set of distortions)
    ground_truth = {
        "If I can't get a good mark, then I'm talentless.": "all_or_nothing_thinking",
        "My excitement will not allow me to perform on stage.": "fortune_telling",
        "My luck still allows me to hold this position.": "discounting_positive",
        "I feel that the event will be boring.": "emotional_reasoning",
        "My friend is short-sighted.": "labeling",
        "My mistake at the meeting suggests that I do not know how to behave in society.": "overgeneralization",
        "Bonus does not mean that I do a good job.": "magnification_minimization",
        "Despite the fact that I fulfilled the plan, my mistake in the report indicates that I am stupid.": "mental_filter",
        "He or she thinks I'm not attractive / handsome.": "mind_reading",
        "She / he talks to me rudely because I cannot explain my request.": "personalization",
        "I have to get married before twenty-five because that's the way it is.": "should_statements",
        "It is you who made me feel bad.": "blaming",
        "My father always preferred my elder brother because he is much smarter than I am.": "unfair_comparisons",
        "What if my husband leaves me?": "what_if",
        "He was looking at me, so I concluded immediately he thought I was responsible for the accident.": "jumping_to_conclusions"
    }

    test_thoughts = [
        "If I can't get a good mark, then I'm talentless.",
        "My excitement will not allow me to perform on stage.",
        "My luck still allows me to hold this position.",
        "I feel that the event will be boring.",
        "My friend is short-sighted.",
        "My mistake at the meeting suggests that I do not know how to behave in society.",
        "Bonus does not mean that I do a good job.",
        "Despite the fact that I fulfilled the plan, my mistake in the report indicates that I am stupid.",
        "He or she thinks I'm not attractive / handsome.",
        "She / he talks to me rudely because I cannot explain my request.",
        "I have to get married before twenty-five because that's the way it is.",
        "It is you who made me feel bad.",
        "My father always preferred my elder brother because he is much smarter than I am.",
        "What if my husband leaves me?",
        "He was looking at me, so I concluded immediately he thought I was responsible for the accident.",
    ]

    # Lists to collect overall latencies and self consistency scores for separate averaging
    all_latencies = []
    all_self_consistencies = []

    # List for recording each thought's evaluation data for Excel export
    results = []

    # List for recording each distortion's evaluation data for Excel export
    dist_results = []

    # Dict for recording each thought's final predictions
    final_predictions = {}

    # Number of runs per thought to assess self-consistency
    runs_per_thought = 3

    print("Running the forest...")

    # Metrics for testing
    correct_predictions = 0

    for i, thought in enumerate(test_thoughts, start=1):
        print("=============================================================")
        print(f"Thought {i} of {len(test_thoughts)}")
        print(f"Thought: {thought}")
        print("=============================================================")

        latencies = []
        predictions_runs = []
        paths_runs = []
        for run in range(runs_per_thought):
            print("---------------------------------------")
            print(f"Run {run + 1} of {runs_per_thought}")
            print("---------------------------------------")

            start = time.time()
            distortions, paths = identify_distortion(thought)  # Dict{str : str}
            end = time.time()
            latencies.append(end - start)
            # Aggregate predictions across trees (here using the union of the leaf nodes)
            pred_set = set(distortions.values())  # set()
            predictions_runs.append(frozenset(pred_set))  # List[frozenset()]
            paths_runs.append(paths)

        avg_latency = np.mean(latencies)
        all_latencies.append(avg_latency)
        # Compute self-consistency: percentage of runs matching the mode prediction
        self_consistency, final_prediction = average_jaccard_percentage_and_flattened_intersections(predictions_runs) # float, List[]
        all_self_consistencies.append(self_consistency)

        # Add the thought's final prediction to a list of final predictions
        final_predictions[thought] = final_prediction  # Dict{str : List[]}
        gt = ground_truth[thought]

        correct_predictions += 1 if gt in final_prediction else 0

        # Save decision tree paths (using the first run's paths) to a txt file for this thought.
        with open(os.path.join("output_paths", f"thought_{i}_path.txt"), "w") as f:
            f.write(f"Thought: {thought}\n")
            for tree, path in paths_runs[0].items():
                f.write(f"\nTree: {tree}\n")
                for line in path:
                    f.write(line + "\n")

        results.append({
            "Thought": thought,
            "Latency (s)": avg_latency,
            "Self Consistency (%)": self_consistency,
            "Predicted Distortions": ", ".join((map(str, final_prediction))),
            "Ground Truth": gt
        })

        print("=============================================================")
        print(f"Results {i} of {len(test_thoughts)}")
        print("=============================================================")

        print({
            "Thought": thought,
            "Latency (s)": avg_latency,
            "Self Consistency (%)": self_consistency,
            "Predicted Distortions": ", ".join((map(str, final_prediction))),
            "Ground Truth": gt
        })
        print("weeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        print("=============================================================")

    # Get all unique distortions from the ground truth
    distortions_all = set(ground_truth.values())
    tp, fp, tn, fn = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    precision, recall, f1_score = defaultdict(float), defaultdict(float), defaultdict(float)

    for dist in distortions_all:  # looping over all unique distortions
        for thought in ground_truth:  # looping over examples
            gt_dist = ground_truth[thought]
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print({
                "Distortion": dist,
                "Ground Truth": gt_dist,
                "Final Prediction": final_predictions[thought]
            })
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            if dist == gt_dist:
                if dist in final_predictions[thought]:
                    tp[dist] += 1
                else:
                    fp[dist] += 1
            else:
                if dist in final_predictions[thought]:
                    fn[dist] += 1
                else:
                    tn[dist] += 1

        precision[dist] = tp[dist] / (tp[dist] + fp[dist]) if (tp[dist] + fp[dist]) > 0 else 0
        recall[dist] = tp[dist] / (tp[dist] + fn[dist]) if (tp[dist] + fn[dist]) > 0 else 0
        f1_score[dist] = 2 * precision[dist] * recall[dist] / (precision[dist] + recall[dist]) if (precision[dist] + recall[dist]) > 0 else 0
       

        dist_results.append({
            "Distortion": dist,
            "TP": tp[dist],
            "FP": fp[dist],
            "TN": tn[dist],
            "FN": fn[dist],
            "Precision": precision[dist],
            "Recall": recall[dist],
            "F1 Score": f1_score[dist],
        })

    # Append the accuracy as a new row in the DataFrame
    accuracy = correct_predictions / len(test_thoughts)
    results.append({
        "Thought": "Overall Accuracy",
        "Latency (s)": "",
        "Self Consistency (%)": "",
        "Predicted Distortions": "",
        "Ground Truth": accuracy
    })

    # Save all evaluation metrics to an Excel file
    df = pd.DataFrame(results)
    df.to_excel("evaluation_metrics.xlsx", index=False)

    # Save all distortions evaluation metrics to an Excel file
    dist_df = pd.DataFrame(dist_results)
    dist_df.to_excel("distortions_evaluation_metrics.xlsx", index=False)

    # Save individual latency and self consistency values and their averages to separate txt files
    with open("latency.txt", "w") as f:
        for i, lat in enumerate(all_latencies, start=1):
            f.write(f"Thought {i} latency: {lat:.4f} s\n")
        f.write(f"\nAverage latency: {np.mean(all_latencies):.4f} s\n")

    with open("self_consistency.txt", "w") as f:
        for i, sc in enumerate(all_self_consistencies, start=1):
            f.write(f"Thought {i} self consistency: {sc:.2f}%\n")
        f.write(f"\nAverage self consistency: {np.mean(all_self_consistencies):.2f}%\n")

    print("Evaluation complete. Metrics saved to 'evaluation_metrics.xlsx', and decision paths in 'output_paths/' ""folder.")
