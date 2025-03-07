'''docstring'''
from typing import Final

QUESTION: Final[str] = "question"
YES: Final[str] = "yes"
MAYBE: Final[str] = "maybe"
NO: Final[str] = "no"
ROOT: Final[str] = "root"
WEAK: Final[str] = "weak"

# define distortion
NO_DISTORTION: Final[str] = "no_distortion"
FORTUNE_TELLING: Final[str] = "fortune_telling"
WHAT_IF_STATEMENTS: Final[str]  = "what_if_statements"
LABELING: Final[str]  = "labeling"
UNFAIR_COMPARISONS: Final[str]  = "unfair_comparisons"
MIND_READING: Final[str]  = "mind_reading"
SHOULD_STATEMENTS: Final[str]  = "should_statements"
OVERGENERALIZATION: Final[str]  = "overgeneralization"
ALL_OR_NOTHING_THINKING: Final[str] = "all_or_nothing_thinking"
BLAMING: Final[str] = "blaming"
EMOTIONAL_REASONING: Final[str] = "emotional_reasoning"
MENTAL_FILTER: Final[str] = "mental_filter"
DISCOUNTING_THE_POSITIVE: Final[str] = "discounting_the_positive"
MAGNIFICATION_MINIMIZATION: Final[str] = "magnification_minimization"
PERSONALIZATION: Final[str] = "personalization"
JUMPING_TO_CONCLUSIOS: Final[str] = "jumping_to_conclusions"

# define final distortion questions
FORTUNE_TELLING_QUESTION: Final[str] = "fortune_telling_question"
WHAT_IF_STATEMENTS_QUESTION: Final[str]  = "what_if_statements_question"
LABELING_QUESTION: Final[str]  = "labeling_question"
UNFAIR_COMPARISONS_QUESTION: Final[str]  = "unfair_comparisons_question"
MIND_READING_QUESTION: Final[str]  = "mind_reading_question"
SHOULD_STATEMENTS_QUESTION: Final[str]  = "should_statements_question"
OVERGENERALIZATION_QUESTION: Final[str]  = "overgeneralization_question"
ALL_OR_NOTHING_THINKING_QUESTION: Final[str] = "all_or_nothing_thinking_question"
BLAMING_QUESTION: Final[str] = "blaming_question"
EMOTIONAL_REASONING_QUESTION: Final[str] = "emotional_reasoning_question"
MENTAL_FILTER_QUESTION: Final[str] = "mental_filter_question"
DISCOUNTING_THE_POSITIVE_QUESTION: Final[str] = "discounting_the_positive_question"
MAGNIFICATION_MINIMIZATION_QUESTION: Final[str] = "magnification_minimization_question"
PERSONALIZATION_QUESTION: Final[str] = "personalization_question"
JUMPING_TO_CONCLUSIOS_QUESTION: Final[str] = "jumping_to_conclusions_question"

cognitive_forest: dict[str, dict[str, dict[str, str]]] = {
    "cognitive_rigidity": {
        ROOT: {
            QUESTION: "Does this text contain definite/absolute terms?",
            YES: ALL_OR_NOTHING_THINKING_QUESTION,
            NO: NO_DISTORTION,
        },
        ALL_OR_NOTHING_THINKING_QUESTION: {
            QUESTION: "Does this text indicate that the writer thinks there is no middle ground?",
            YES: ALL_OR_NOTHING_THINKING,
            NO: PERSONALIZATION_QUESTION,
        },
        PERSONALIZATION_QUESTION: {
            QUESTION: "Is this text subjective to one perspective but can have other explanations?",
            YES: PERSONALIZATION,
            NO: LABELING_QUESTION,
        },
        LABELING_QUESTION: {
            QUESTION: "Does this text indicate that the writer believes this event or action to define his traits?",
            YES: LABELING,
            NO: OVERGENERALIZATION_QUESTION,
        },
        OVERGENERALIZATION_QUESTION: {
            QUESTION: "Does the writer draw beliefs from limited experiences?",
            YES: OVERGENERALIZATION,
            NO: NO_DISTORTION,
        },
    },
    "predictions_and_misinterpretations": {
        ROOT: {
            QUESTION: "Does the sentence contain an assumption?",
            YES: FORTUNE_TELLING_QUESTION,
            NO: NO_DISTORTION,
        },
        FORTUNE_TELLING_QUESTION: {
            QUESTION: "Does the text indicate that the writer believes the worst case scenario is what's going to happen?",
            YES: FORTUNE_TELLING,
            NO: WHAT_IF_STATEMENTS_QUESTION,
        },
        WHAT_IF_STATEMENTS_QUESTION: {
            QUESTION: 'Is the text "what if" based?',
            YES: WHAT_IF_STATEMENTS,
            NO: MIND_READING_QUESTION,
        },
        MIND_READING_QUESTION: {
            QUESTION: "Is the writer assuming knowledge of others' texts with zero evidence?",
            YES: MIND_READING,
            NO: JUMPING_TO_CONCLUSIOS_QUESTION,
        },
        JUMPING_TO_CONCLUSIOS_QUESTION: {
            QUESTION: "Is the writer drawing conclusions on faulty or insufficient evidence?",
            YES: JUMPING_TO_CONCLUSIOS,
            NO: NO_DISTORTION,
        },
    },
    "negative_bias": {
        ROOT: {
            QUESTION: "Does this text acknowledge more negatives than positives?",
            YES: MENTAL_FILTER_QUESTION,
            NO: "expectation_question",
        },
        "expectation_question": {
            QUESTION: "Does the text project an expectation towards oneself or others?",
            YES: UNFAIR_COMPARISONS_QUESTION,
            NO: NO_DISTORTION,
        },
        UNFAIR_COMPARISONS_QUESTION: {
            QUESTION: "Does the text make an unfair comparison?",
            YES: UNFAIR_COMPARISONS,
            NO: SHOULD_STATEMENTS_QUESTION,
        },
        SHOULD_STATEMENTS_QUESTION: {
            QUESTION: "Does the text indicate that the writer feels the need to do or achieve something based on an expectation?",
            YES: SHOULD_STATEMENTS,
            NO: NO_DISTORTION,
        },
        "mental_filter_question": {
            QUESTION: "Does this text indicate pure focus on the negatives and is the writer not acknowledging any positives?",
            YES: MENTAL_FILTER,
            NO: "negative_positives",
        },
        "negative_positives": {
            QUESTION: "Does this text contain any positive acknowledgements?",
            YES: DISCOUNTING_THE_POSITIVE_QUESTION,
            NO: MAGNIFICATION_MINIMIZATION_QUESTION,
        },
        MAGNIFICATION_MINIMIZATION_QUESTION: {
            QUESTION: "Does the text indicate either downplaying or exaggeration of a situation, action, or environment?",
            YES: MAGNIFICATION_MINIMIZATION,
            NO: NO_DISTORTION,
        },
        "discounting_the_positives_question": {
            QUESTION: "Is the writer falsely attributing a positive to an external entity?",
            YES: DISCOUNTING_THE_POSITIVE,
            NO: NO_DISTORTION,
        },
    },
    "responsibility": {
        ROOT: {
            QUESTION: "Is the writer placing the responsibility on solely one party or entity?",
            YES: BLAMING,
            NO: NO_DISTORTION,
        }
    },
    "subjectivity_and_emotional_reasoning": {
        ROOT: {
            QUESTION: "Does the text stem from emotions?",
            YES: EMOTIONAL_REASONING_QUESTION,
            NO: NO_DISTORTION
        },
        EMOTIONAL_REASONING_QUESTION: {
            QUESTION: "Would the statement remain true without emotional words?",
            YES: NO_DISTORTION,
            NO: EMOTIONAL_REASONING
        }
    },
}
