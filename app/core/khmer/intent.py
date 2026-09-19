"""
Intent classification for Khmer math requests.

`IntentClassifier` is an abstract interface on purpose: phase 1 ships a
rule-based implementation (fast, deterministic, zero dependencies), and a
later phase can add an ML/LLM-based classifier that implements the same
interface. Nothing else in the codebase needs to change when that happens.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum


class MathIntent(str, Enum):
    SOLVE_EQUATION = "solve_equation"
    EVALUATE_EXPRESSION = "evaluate_expression"
    SIMPLIFY_EXPRESSION = "simplify_expression"
    UNKNOWN = "unknown"


class IntentClassifier(ABC):
    @abstractmethod
    def classify(self, normalized_text: str) -> MathIntent: ...


# Common Khmer phrasings for "solve for x" / "find the value of x".
_SOLVE_KEYWORDS = [
    "ដោះស្រាយ",           # solve
    "ជួយខ្ញុំដោះស្រាយ",      # help me solve
    "ជួយដោះស្រាយ",         # help solve
    "រកតម្លៃ",             # find the value
    "រក x",
    "រក",                  # find
    "ស្វែងរក",            # search/find
    "តម្លៃប៉ុន្មាន",         # what is the value / how much
    "តម្លៃ",               # value
    "ណា",                  # what (in questions)
    "គណនា",                # calculate/compute
    "គិត",                 # calculate
    "ស្វែងយក",            # seek/find
    "ដោះ",                # solve (short form)
]

_SIMPLIFY_KEYWORDS = [
    "ធ្វើឲ្យសាមញ្ញ",      # simplify
    "កាត់បន្ថយ",          # reduce
    "សាមញ្ញ",             # simple
    "បង្រួម",              # condense/reduce
    "កាត់",                # cut/reduce
]

_EVALUATE_KEYWORDS = [
    "គណនា",                # calculate
    "គិត",                 # think/calculate
    "ផ្ដល់ជូន",           # provide/give
    "លទ្ធផល",             # result
    "ចម្លើយ",              # answer
]

_FRACTION_KEYWORDS = [
    "ប្រភាគ",              # fraction
    "ប្រភាគទសភាគ",         # decimal fraction
    "ប្រភាគធម្មតា",         # common fraction
]

_PERCENTAGE_KEYWORDS = [
    "ភាគរយ",               # percentage
    "%",
    "ភាគ",                 # percent (short)
    "ចំនួនភាគរយ",          # percentage amount
]

_WORD_PROBLEM_KEYWORDS = [
    "បញ្ហា",               # problem
    "សំណួរ",               # question
    "លំហាត់",              # exercise
    "តើ",                  # question marker
]


class RuleBasedIntentClassifier(IntentClassifier):
    def classify(self, normalized_text: str) -> MathIntent:
        # Priority 0: Fraction or percentage keywords override general keywords
        # (e.g., "គណនាប្រភាគ" should be evaluate, not solve)
        has_fraction = any(keyword in normalized_text for keyword in _FRACTION_KEYWORDS)
        has_percentage = any(keyword in normalized_text for keyword in _PERCENTAGE_KEYWORDS)
        
        if has_fraction or has_percentage:
            return MathIntent.EVALUATE_EXPRESSION
        
        # Priority 1: Explicit simplify keywords
        if any(keyword in normalized_text for keyword in _SIMPLIFY_KEYWORDS):
            return MathIntent.SIMPLIFY_EXPRESSION
        
        # Priority 2: Equations (contains equals sign)
        if "=" in normalized_text:
            # A bare equation with no explicit verb ("2x+5=15") is still an
            # implicit request to solve it.
            return MathIntent.SOLVE_EQUATION
        
        # Priority 3: Explicit solve keywords
        if any(keyword in normalized_text for keyword in _SOLVE_KEYWORDS):
            return MathIntent.SOLVE_EQUATION
        
        # Priority 4: Evaluate keywords suggest computation
        if any(keyword in normalized_text for keyword in _EVALUATE_KEYWORDS):
            return MathIntent.EVALUATE_EXPRESSION
        
        # Priority 5: Word problem markers with numbers suggest evaluation
        has_word_problem = any(keyword in normalized_text for keyword in _WORD_PROBLEM_KEYWORDS)
        has_numbers = re.search(r"\d", normalized_text)
        
        if has_word_problem and has_numbers:
            return MathIntent.EVALUATE_EXPRESSION
        
        # Priority 6: Any expression with numbers (fallback)
        if has_numbers:
            return MathIntent.EVALUATE_EXPRESSION
        
        return MathIntent.UNKNOWN
