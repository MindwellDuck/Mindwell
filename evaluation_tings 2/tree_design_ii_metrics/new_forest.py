"""docstring"""
import ollama
import re
import time
from typing import Dict, Any
import pandas as pd
import os
from collections import Counter, defaultdict
import numpy as np

from forest_vars import *


class CognitiveDistortionDetector:

    """Detect cognitive distortions"""
    def __init__(self, tree: dict[str, dict[str, str]], thought: str, tree_name: str) -> None:
        self.tree: dict[str, dict[str, str]] = tree
        self.thought: str = thought
        self.tree_name: str = tree_name
    def answer(self, question: str) -> str:
        '''docstring'''
        # print(question, end=' ')
        response: str = ollama.chat(
            model='deepseek-r1:14b',
            messages=[{
                'role': 'system',
                'content': """Answer ONLY 'yes', 'no', or 'maybe' to this question. Use the following definitions to be able to reason with them.
All or Nothing Thinking/Polarized Thinking: I view a situation, a person or an event in “either-or” terms, fitting them into only two extreme categories instead of on a continuum.
Fortune telling (also called catastrophizing): I predict the future in negative terms and believe that what will happen will be so awful that I will not be able to stand it.
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
Unfair comparisons: I compare myself with others who seem to do better than I do and place myself in a disadvantageous position."""
            }, {
                'role': 'user',
                'content': f"Thought: {self.thought}\nQuestion: {question}"
            }],
            options={'temperature': 0}
        )['message']['content'].split("</think>\n\n", 1)[1].lower()
        # print(response)
        if (NO in response):
            return NO
        elif (YES in response):
            return YES
        elif (MAYBE in response):
            return MAYBE
        else:
            return "WRONG"
    def traverse_tree(self, node: str, paths: dict[str, str]) -> list[str]:
        if self.tree_name not in paths:
            paths[self.tree_name] = []
        
        while node in self.tree:
            # Step 1: Add the current question to the path
            paths[self.tree_name].append(self.tree[node][QUESTION])
            print(f"Question: {self.tree[node][QUESTION]}")
            
            # Step 2: Get the answer and add it to the path
            answer = self.answer(self.tree[node][QUESTION])
            paths[self.tree_name].append(answer)
            print(f"Answer: {answer}")

            # Step 3: Based on the answer, continue to the next node
            match answer:
                case maybe if maybe == MAYBE:
                    # Recursively traverse YES and NO branches and collect distortions
                    distortions = [
                        f'{WEAK} {distortion}' for distortion in self.traverse_tree(self.tree[node][YES], paths)
                    ] + self.traverse_tree(self.tree[node][NO], paths)
                    paths[self.tree_name].append(distortions)
                    print(f"Distortion: {distortions}")
                    return distortions  # Only return distortion labels
                case yes if yes == YES:
                    paths[self.tree_name].append(self.tree[node][YES])
                    print(f"Distortion: {self.tree[node][YES]}")
                    return self.traverse_tree(self.tree[node][YES], paths)  # Recursively traverse the YES branch
                case no if no == NO:
                    paths[self.tree_name].append(self.tree[node][NO])
                    print(f"Distortion: {self.tree[node][NO]}")
                    return self.traverse_tree(self.tree[node][NO], paths)  # Recursively traverse the NO branch
                case _:
                    return ["WRONG"]  # If the answer is something unexpected, return "WRONG" label
        
        # If no match was found, return the distortion label (i.e., the node itself)
        return [node]



    def get_distortions(self) -> tuple:
        """get_distortion"""
        paths = {}
        current_distortions = self.traverse_tree(ROOT, paths)
        # print(current_distortions)
        return current_distortions, paths
    
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

def separate_by_weak(final_prediction):
    weak_list = []  # List to hold elements starting with 'weak'
    not_weak_list = []  # List to hold elements not starting with 'weak'
    
    for element in final_prediction:
        if element.lower().startswith('weak'):  # Check if element starts with 'weak' (case-insensitive)
            # Remove the 'weak ' prefix before appending to the weak_list
            weak_list.append(element[len("weak "):])  # Remove 'weak ' from the start of the string
        else:
            not_weak_list.append(element)
    
    return weak_list, not_weak_list


if __name__=="__main__":
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
        "He was looking at me, so I concluded immediately he thought I was responsible for the accident."
    ]
    debug_thoughts = [ "If I can't get a good mark, then I'm talentless.",
        "Bonus does not mean that I do a good job.",]
    
    ground_truth = {
       "If I can't get a good mark, then I'm talentless.": ALL_OR_NOTHING_THINKING,
        "My excitement will not allow me to perform on stage.": FORTUNE_TELLING,
        "My luck still allows me to hold this position.": DISCOUNTING_THE_POSITIVE,
        "I feel that the event will be boring.": EMOTIONAL_REASONING,
        "My friend is short-sighted.": LABELING,
        "My mistake at the meeting suggests that I do not know how to behave in society.": OVERGENERALIZATION,
        "Bonus does not mean that I do a good job.": MAGNIFICATION_MINIMIZATION,
        "Despite the fact that I fulfilled the plan, my mistake in the report indicates that I am stupid.": MENTAL_FILTER,
        "He or she thinks I'm not attractive / handsome.": MIND_READING,
        "She / he talks to me rudely because I cannot explain my request.": PERSONALIZATION,
        "I have to get married before twenty-five because that's the way it is.": SHOULD_STATEMENTS,
        "It is you who made me feel bad.": BLAMING,
        "My father always preferred my elder brother because he is much smarter than I am.": UNFAIR_COMPARISONS,
        "What if my husband leaves me?": WHAT_IF_STATEMENTS,
        "He was looking at me, so I concluded immediately he thought I was responsible for the accident.": JUMPING_TO_CONCLUSIOS
   }
    debug_ground_truth = {
       "If I can't get a good mark, then I'm talentless.": ALL_OR_NOTHING_THINKING,
        "Bonus does not mean that I do a good job.": MAGNIFICATION_MINIMIZATION,

   }
    true_labels = [  # Expected correct distortions for evaluation
        [ALL_OR_NOTHING_THINKING],
        [FORTUNE_TELLING],
        [DISCOUNTING_THE_POSITIVE],
        [EMOTIONAL_REASONING],
        [LABELING],
        [OVERGENERALIZATION],
        [MAGNIFICATION_MINIMIZATION],
        [MENTAL_FILTER],
        [MIND_READING],
        [PERSONALIZATION],
        [SHOULD_STATEMENTS],
        [BLAMING],
        [UNFAIR_COMPARISONS],
        [WHAT_IF_STATEMENTS],
        [JUMPING_TO_CONCLUSIOS]
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
    weak_final_predictions = {}
    runs_per_thought = 3

    print("Running the forest...")
    # Metrics for testing
    correct_predictions = 0
    weak_correct_predictions = 0
    for i, thought in enumerate(test_thoughts):
        print("=============================================================")
        print(f"Thought {i+1} of {len(test_thoughts)}")
        print(f"Thought: {thought}")
        print("=============================================================")
        
        latencies = []
        predictions_runs = []
        distortions: list[str] = []
        paths_runs= defaultdict(list)
        for run in range(runs_per_thought):
            print("---------------------------------------")
            print(f"Run {run+1} of {runs_per_thought}")
            print("---------------------------------------")
            start = time.time()
            for current_tree in cognitive_forest.items():
                detector = CognitiveDistortionDetector(current_tree[1], thought, current_tree[0])
                current_distortions, current_paths = detector.get_distortions()
                distortions += current_distortions
                paths_runs[current_tree[0]].append(current_paths)
            end = time.time()
    
            latencies.append(end - start)
            print(distortions)
            pred_set = set(distortions)
            predictions_runs.append(frozenset(pred_set))
        
        # Ensure the output directory exists.
        if not os.path.exists("output_paths"):
            os.makedirs("output_paths")

        # Write paths for all runs for each tree.
        with open(os.path.join("output_paths", f"thought_{i}_path.txt"), "w") as f:
            f.write(f"Thought: {thought}\n")
            
            # Loop through all trees in the forest.
            for tree in cognitive_forest.keys():
                # Check if we have recorded at least one run for this tree.
                if paths_runs[tree]:
                    f.write(f"\nTree: {tree}\n")
                    # Iterate over each run's results for this tree.
                    for run_idx, run_dict in enumerate(paths_runs[tree], start=1):
                        f.write(f"  Run {run_idx}:\n")
                        # run_dict is a dictionary where the key is the tree name
                        # and its value is a list of steps.
                        for line in run_dict[tree]:
                            f.write("    " + str(line) + "\n")


        avg_latency =np.mean(latencies)
        all_latencies.append(avg_latency)

        all_predictions = [prediction for run in predictions_runs for prediction in run]  # List[]


        self_consistency, final_prediction = average_jaccard_percentage_and_flattened_intersections(predictions_runs)
        all_self_consistencies.append(self_consistency)


        weak_final_predictions[thought], final_predictions[thought] = separate_by_weak(final_prediction)

        gt = ground_truth[thought]

        correct_predictions += 1 if gt in final_predictions[thought] else 0
        weak_correct_predictions += 1 if gt in weak_final_predictions[thought] else 0

       
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

    w_tp, w_fp, w_tn, w_fn = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    w_precision, w_recall, w_f1_score = defaultdict(float), defaultdict(float), defaultdict(float)


    for dist in distortions_all:  # looping over all unique distortions
        for thought in ground_truth:  # looping over examples
            gt_dist = ground_truth[thought]
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print({
                "Distortion": dist,
                "Ground Truth": gt_dist,
                "Final Prediction": final_predictions[thought],
                "Weak Prediction": weak_final_predictions[thought]
            })
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            if dist == gt_dist:
                if dist in final_predictions[thought]:
                    tp[dist] += 1
                else:
                    fp[dist] += 1
                
                if dist in weak_final_predictions[thought]:
                    w_tp[dist] += 1
                else:
                    w_fp[dist] += 1
            else:
                if dist in final_predictions[thought]:
                    fn[dist] += 1
                else:
                    tn[dist] += 1

                if dist in weak_final_predictions[thought]:
                    w_fn[dist] += 1
                else:
                    w_tn[dist] += 1

        precision[dist] = tp[dist] / (tp[dist] + fp[dist]) if (tp[dist] + fp[dist]) > 0 else 0
        recall[dist] = tp[dist] / (tp[dist] + fn[dist]) if (tp[dist] + fn[dist]) > 0 else 0
        f1_score[dist] = 2 * precision[dist] * recall[dist] / (precision[dist] + recall[dist]) if (precision[dist] + recall[dist]) > 0 else 0
       
        w_precision[dist] = w_tp[dist] / (w_tp[dist] + w_fp[dist]) if (w_tp[dist] + w_fp[dist]) > 0 else 0
        w_recall[dist] = w_tp[dist] / (w_tp[dist] + w_fn[dist]) if (w_tp[dist] + w_fn[dist]) > 0 else 0
        w_f1_score[dist] = 2 * w_precision[dist] * w_recall[dist] / (w_precision[dist] + w_recall[dist]) if (w_precision[dist] + w_recall[dist]) > 0 else 0


        dist_results.append({
            "Distortion": dist,
            "TP": tp[dist],
            "FP": fp[dist],
            "TN": tn[dist],
            "FN": fn[dist],
            "Precision": precision[dist],
            "Recall": recall[dist],
            "F1 Score": f1_score[dist],
            "Weak TP": w_tp[dist],
            "Weak FP": w_fp[dist],
            "Weak TN": w_tn[dist],
            "Weak FN": w_fn[dist],
            "Weak Precision": w_precision[dist],
            "Weak Recall": w_recall[dist],
            "Weak F1 Score": w_f1_score[dist],
        })

    # Append the accuracy as a new row in the DataFrame
    accuracy = correct_predictions / len(test_thoughts)
    weak_accuracy = weak_correct_predictions / len(test_thoughts)

    results.append({
        "Thought": "Overall Accuracy",
        "Latency (s)": "",
        "Self Consistency (%)": "",
        "Predicted Distortions": "",
        "Ground Truth": accuracy,
    })
    results.append({
        "Thought": "Weak Overall Accuracy",
        "Latency (s)": "",
        "Self Consistency (%)": "",
        "Predicted Distortions": "",
        "Ground Truth": weak_accuracy,
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
