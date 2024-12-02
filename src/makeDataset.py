import json
import os
from typing import Dict, List, Any
from pathlib import Path

decision_tree = {
    "root": {
        "question": "Is the thought pattern about future events or predictions?",
        "yes": "future",
        "no": "evidence_check"
    },
    "evidence_check": {
        "question": "Is the thought pattern about making conclusions or assumptions?",
        "yes": "evidence",
        "no": "evaluation_check"
    },
    "evaluation_check": {
        "question": "Is the thought pattern about evaluating or judging self/others/situations?",
        "yes": "evaluation",
        "no": "attention_check"
    },
    "attention_check": {
        "question": "Is the thought pattern about focusing attention on specific aspects?",
        "yes": "attention",
        "no": "responsibility_check"
    },
    "responsibility_check": {
        "question": "Is the thought pattern about assigning responsibility or causation?",
        "yes": "responsibility",
        "no": "no_distortion"
    },
    "future": {
        "question": "Are the predictions catastrophic or unbearable?",
        "yes": "fortune_telling",
        "no": "what_if"
    },
    "what_if": {
        "question": "Are there repeated 'what if' questions?",
        "yes": "what_if_statements",
        "no": "no_distortion"
    },
    "evidence": {
        "question": "Are conclusions drawn without sufficient evidence?",
        "yes": "jumping_to_conclusions",
        "no": "evidence_type"
    },
    "evidence_type": {
        "question": "Are emotions used as the primary evidence?",
        "yes": "emotional_reasoning",
        "no": "assumed_thoughts"
    },
    "assumed_thoughts": {
        "question": "Are others' thoughts/intentions assumed without evidence?",
        "yes": "mind_reading",
        "no": "no_distortion"
    },
    "evaluation": {
        "question": "Does the evaluation involve extreme categories?",
        "yes": "extremes",
        "no": "standards_check"
    },
    "extremes": {
        "question": "Does it use words like 'always', 'never', 'every time'?",
        "yes": "overgeneralization",
        "no": "two_options"
    },
    "two_options": {
        "question": "Is everything sorted into only two categories?",
        "yes": "all_or_nothing",
        "no": "no_distortion"
    },
    "standards_check": {
        "question": "Is it about how things 'should' be?",
        "yes": "should_statements",
        "no": "comparison_check"
    },
    "comparison_check": {
        "question": "Is it about comparing to others?",
        "yes": "unfair_comparisons",
        "no": "labels_check"
    },
    "labels_check": {
        "question": "Is it about applying fixed, global labels?",
        "yes": "labeling",
        "no": "no_distortion"
    },
    "attention": {
        "question": "Is there selective focus on specific aspects?",
        "yes": "mental_filter",
        "no": "positive_negative_check"
    },
    "positive_negative_check": {
        "question": "Is it about weighing positives versus negatives?",
        "yes": "weighing_check",
        "no": "no_distortion"
    },
    "weighing_check": {
        "question": "Is it exclusively focusing on negatives?",
        "yes": "magnification_minimization",
        "no": "positive_dismiss"
    },
    "positive_dismiss": {
        "question": "Are positive experiences being dismissed?",
        "yes": "discounting_the_positive",
        "no": "no_distortion"
    },
    "responsibility": {
        "question": "Is external behavior seen as personally directed?",
        "yes": "personalization",
        "no": "blame_check"
    },
    "blame_check": {
        "question": "Is there complete attribution of responsibility to self or others?",
        "yes": "blaming",
        "no": "no_distortion"
    }
}

def find_distortion_paths(tree: Dict[str, Any]) -> Dict[str, Dict[str, List[str]]]:
    """Find all paths through the decision tree for each cognitive distortion."""
    distortion_paths = {}
    
    def traverse(node_key: str, current_path: List[str], question_path: List[str]):
        # If we've reached a leaf node (a distortion)
        if isinstance(tree.get(node_key), str) or tree.get(node_key) is None:
            if node_key != 'no_distortion':
                distortion_paths[node_key] = {
                    'answers': current_path,
                    'questions': question_path
                }
            return
        
        node = tree[node_key]
        question = node['question']
        
        # Traverse yes path
        traverse(node.get('yes'), current_path + ['Yes'], question_path + [question])
        # Traverse no path
        traverse(node.get('no'), current_path + ['No'], question_path + [question])
    
    traverse('root', [], [])
    return distortion_paths

def process_json_file(file_path: Path, paths: Dict[str, Dict[str, List[str]]], 
                     name_to_node: Dict[str, str]) -> List[Dict[str, str]]:
    """Process a single JSON file and return its training examples."""
    dataset = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Handle both list and dictionary formats
        if isinstance(json_data, dict):
            json_data = [json_data]
        
        for item in json_data:
            text = item.get('generated_text')
            distortion_name = item.get('cognitive_distortion')
            
            if not text or not distortion_name:
                print(f"Warning: Skipping incomplete entry in {file_path}")
                continue
                
            distortion_key = name_to_node.get(distortion_name)
            if not distortion_key:
                print(f"Warning: Unknown distortion '{distortion_name}' in {file_path}")
                continue
            
            if distortion_key in paths:
                path_data = paths[distortion_key]
                questions = path_data['questions']
                answers = path_data['answers']
                
                for question, answer in zip(questions, answers):
                    dataset.append({
                        'text': text,
                        'question': question,
                        'answer': answer,
                        'source_file': file_path.name,
                        'cognitive_distortion': distortion_name
                    })
                    
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON file: {file_path}")
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        
    return dataset

def create_training_dataset(input_dir: str, name_to_node: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Create a training dataset from all JSON files in the specified directory.
    
    Args:
        input_dir: Directory containing JSON files with cognitive distortion examples
        name_to_node: Mapping from distortion names to node keys
    
    Returns:
        List of dictionaries containing text, questions, and their correct answers
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")
    
    # Get all paths through the decision tree
    paths = find_distortion_paths(decision_tree)
    
    # Initialize empty dataset
    complete_dataset = []
    
    # Process all JSON files in the directory
    for file_path in input_path.glob('*.json'):
        print(f"Processing file: {file_path.name}")
        file_dataset = process_json_file(file_path, paths, name_to_node)
        complete_dataset.extend(file_dataset)
        print(f"Added {len(file_dataset)} examples from {file_path.name}")
    
    return complete_dataset

if __name__ == "__main__":
    name_to_node = {
        "Fortune Telling": "fortune_telling",
        "What if?": "what_if_statements",
        "Labeling/Global Labeling": "labeling",
        "Unfair Comparisons": "unfair_comparisons",
        "Mind Reading": "mind_reading_conclusion",
        "Should Statements": "should_statements_conclusion",
        "Overgeneralization": "overgeneralization",
        "All or Nothing Thinking": "all_or_nothing_thinking",
        "Blaming": "blaming_conclusion",
        "Emotional Reasoning": "emotional_reasoning",
        "Mental Filter": "mental_filter",
        "Discounting the Positive": "discounting_the_positive",
        "Magnification/Minimization": "magnification_minimization",
        "Personalization": "personalization_conclusion",
        "Jumping to Conclusions": "jumping_to_conclusions",
        "No Distortion": "no_distortion"
    }
    
    # Directory containing JSON files
    input_directory = '../data/'
    
    try:
        # Generate the dataset
        dataset = create_training_dataset(input_directory, name_to_node)
        
        # Print statistics
        print(f"\nGenerated {len(dataset)} total training examples")
        
        # Count examples per source file
        file_counts = {}
        for entry in dataset:
            source = entry['source_file']
            file_counts[source] = file_counts.get(source, 0) + 1
        
        print("\nExamples per file:")
        for file_name, count in file_counts.items():
            print(f"{file_name}: {count} examples")
        
        # Save the combined dataset
        output_file = '../data/combined_decision_tree_training_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"\nCombined dataset saved to {output_file}")
        
        # Print a sample entry
        if dataset:
            print("\nSample entry:")
            print(json.dumps(dataset[0], indent=2))
            
    except Exception as e:
        print(f"Error: {str(e)}")