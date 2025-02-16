import ollama
import re
from typing import Dict, Any

cognitive_forest = {
    # Tree 1: Self-Perception
    "self_perception_tree": {
        "root": {
            "question": "Does the thought involve a judgment about oneself?",
            "yes": "global_check",
            "no": "others_check"
        },
        "global_check": {
            "question": "Is it a sweeping, global statement about one's character or abilities?",
            "yes": "labeling",
            "no": "specific_check"
        },
        "specific_check": {
            "question": "Does it overgeneralize from a specific instance to an overall pattern?",
            "yes": "overgeneralization",
            "no": "no_distortion"
        },
        "others_check": {
            "question": "Does it assume knowledge of others' thoughts without evidence?",
            "yes": "mind_reading",
            "no": "no_distortion"
        },
        # Terminal nodes
        "labeling": {},
        "overgeneralization": {},
        "mind_reading": {},
        "no_distortion": {}
    },

    # Tree 2: Emotional Reasoning
    "emotional_reasoning_tree": {
        "root": {
            "question": "Is the thought based primarily on emotions rather than facts?",
            "yes": "emotional_reasoning",
            "no": "evidence_check"
        },
        "evidence_check": {
            "question": "Does it draw a conclusion without sufficient evidence?",
            "yes": "jumping_to_conclusions",
            "no": "no_distortion"
        },
        # Terminal nodes
        "emotional_reasoning": {},
        "jumping_to_conclusions": {},
        "no_distortion": {}
    },

    # Tree 3: Future Thinking
    "future_thinking_tree": {
        "root": {
            "question": "Does the thought predict future outcomes?",
            "yes": "catastrophic_check",
            "no": "no_distortion"
        },
        "catastrophic_check": {
            "question": "Does it assume the worst possible outcome will happen?",
            "yes": "catastrophizing",
            "no": "what_if_check"
        },
        "what_if_check": {
            "question": "Does it excessively focus on 'what if' scenarios?",
            "yes": "what_if_statements",
            "no": "no_distortion"
        },
        # Terminal nodes
        "catastrophizing": {},
        "what_if_statements": {},
        "no_distortion": {}
    },

    # Tree 4: Attention Bias
    "attention_bias_tree": {
        "root": {
            "question": "Does the thought focus selectively on certain aspects of a situation?",
            "yes": "negative_focus_check",
            "no": "no_distortion"
        },
        "negative_focus_check": {
            "question": "Does it focus exclusively on negative aspects while ignoring positives?",
            "yes": "mental_filter",
            "no": "magnification_check"
        },
        "magnification_check": {
            "question": "Does it exaggerate negatives or minimize positives?",
            "yes": "magnification_minimization",
            "no": "no_distortion"
        },
        # Terminal nodes
        "mental_filter": {},
        "magnification_minimization": {},
        "no_distortion": {}
    },

    "old_tree": {
    "root": {
        "question": "Is the thought pattern about future events?",
        "yes": "future_check",
        "no": "evidence_check"
    },

    # Future-related branch
    "future_check": {
        "question": "Does it predict unbearable outcomes?",
        "yes": "fortune_telling",
        "no": "what_if_check"
    },
    "what_if_check": {
        "question": "Repeated hypothetical 'what if' questions?",
        "yes": "what_if",
        "no": "no_distortion"
    },

    # Evidence evaluation branch
    "evidence_check": {
        "question": "Conclusion without sufficient evidence?",
        "yes": "jumping_check",
        "no": "evaluation_check"
    },
    "jumping_check": {
        "question": "Assumes knowledge of others' thoughts?",
        "yes": "mind_reading",
        "no": "emotional_check"
    },
    "emotional_check": {
        "question": "Uses emotions as primary evidence?",
        "yes": "emotional_reasoning",
        "no": "jumping_to_conclusions"
    },

    # Evaluation branch
    "evaluation_check": {
        "question": "Involves evaluation/judgment?",
        "yes": "absolutism_check",
        "no": "attention_check"
    },
    "absolutism_check": {
        "question": "Uses absolute terms (always/never)?",
        "yes": "all_or_nothing",
        "no": "obligation_check"
    },
    "obligation_check": {
        "question": "Contains 'should'/'must' statements?",
        "yes": "should_statements",
        "no": "label_check"
    },
    "label_check": {
        "question": "Applies fixed negative labels?",
        "yes": "labeling",
        "no": "responsibility_check"
    },
    "responsibility_check": {
        "question": "Disproportionate responsibility assignment?",
        "yes": "blaming",
        "no": "comparison_check"
    },
    "comparison_check": {
        "question": "Unfavorable social comparison?",
        "yes": "unfair_comparisons",
        "no": "no_distortion"
    },

    # Attention branch
    "attention_check": {
        "question": "Selective focus on specifics?",
        "yes": "filter_check",
        "no": "pattern_check"
    },
    "filter_check": {
        "question": "Exclusively negative focus?",
        "yes": "mental_filter",
        "no": "positivity_check"
    },
    "positivity_check": {
        "question": "Positives being dismissed?",
        "yes": "discounting_positive",
        "no": "magnification_check"
    },
    "magnification_check": {
        "question": "Negatives amplified/positives minimized?",
        "yes": "magnification_minimization",
        "no": "no_distortion"
    },

    # Pattern recognition branch
    "pattern_check": {
        "question": "Single event seen as endless pattern?",
        "yes": "overgeneralization",
        "no": "personalization_check"
    },
    "personalization_check": {
        "question": "External events taken personally?",
        "yes": "personalization",
        "no": "no_distortion"
    },

    # Terminal nodes (15 distortions + no_distortion)
    "all_or_nothing": {},
    "fortune_telling": {},
    "emotional_reasoning": {},
    "labeling": {},
    "mental_filter": {},
    "mind_reading": {},
    "overgeneralization": {},
    "personalization": {},
    "should_statements": {},
    "blaming": {},
    "what_if": {},
    "discounting_positive": {},
    "magnification_minimization": {},
    "jumping_to_conclusions": {},
    "unfair_comparisons": {},
    "no_distortion": {}
    }
}

def analyze_thought(thought: str, current_node: Dict[str, Any]) -> str:
    """Query DeepSeek-R1 using Ollama with strict yes/no formatting"""
    response = ollama.chat(
        model='deepseek-r1:14b',
        messages=[{
            'role': 'system',
            'content': f"Answer ONLY 'yes' or 'no' to this question about thought patterns."
        }, {
            'role': 'user',
            'content': f"Thought: {thought}\nQuestion: {current_node['question']}"
        }],
        options={'temperature': 0}
    )
    return parse_response(response['message']['content'].split("</think>\n\n", 1)[1])

def parse_response(response: str) -> str:
    """Extract yes/no from model response"""
    clean_res = response.strip().lower()
    match = re.search(r'\b(yes|no)\b', clean_res)
    return match.group(0) if match else 'no'

def traverse_tree(thought: str, node: str, decision_tree) -> str:
    """Recursive decision tree traversal"""
    if 'yes' not in decision_tree[node]:  # Leaf node
        print(node)
        return node

    answer = analyze_thought(thought, decision_tree[node])
    print(decision_tree[node]['question'], answer)
    next_node_key = decision_tree[node]['yes'] if answer == 'yes' else decision_tree[node]['no']

    return traverse_tree(thought, next_node_key, decision_tree)

def identify_distortion(thought: str) -> str:
    return [tree + ":\t" + traverse_tree(thought, "root", cognitive_forest[tree]) for tree in cognitive_forest.keys()]

if __name__ == "__main__":
    test_thought = "I am an idiot"
    print(f"Thought: {test_thought}")
    print("Identified distortions:", *identify_distortion(test_thought), sep="\n\t")
