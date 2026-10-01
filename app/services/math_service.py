"""
Math service orchestrating the math solving pipeline:
  Khmer text -> normalize -> detect intent -> extract expression
             -> parse (SymPy) -> classify problem type -> solve + verify
             -> step-by-step (Khmer) -> SolveData
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.core.engine.classifier import classify_problem
from app.core.engine.solver import solve
from app.core.exceptions import MathProcessingError
from app.core.khmer.extractor import extract_expression
from app.core.khmer.intent import MathIntent, RuleBasedIntentClassifier
from app.core.khmer.normalizer import normalize_khmer_text
from app.core.parser.expression_parser import ExpressionParseError, parse_math_text
from app.models.schemas import SolveData

# Re-export MathProcessingError for backward compatibility
__all__ = ["MathProcessingError", "MathService", "get_math_service", "process_question"]


class MathService:
    """Service encapsulating math parsing, classification, and solving logic."""

    def __init__(self, intent_classifier: RuleBasedIntentClassifier | None = None) -> None:
        self.intent_classifier = intent_classifier or RuleBasedIntentClassifier()

    def parse_question(self, question: str) -> dict[str, Any]:
        """
        Parses question text, detects intent, extracts raw and normalized math expressions,
        and classifies the problem type without solving.
        """
        normalized_text = normalize_khmer_text(question)
        intent = self.intent_classifier.classify(normalized_text)
        raw_expression = extract_expression(normalized_text)

        if raw_expression is None:
            raise MathProcessingError("No math expression detected.")

        try:
            parsed = parse_math_text(raw_expression)
        except ExpressionParseError as exc:
            raise MathProcessingError(str(exc)) from exc

        problem_type = classify_problem(parsed)

        return {
            "detected_intent": intent.value,
            "raw_expression": raw_expression,
            "normalized_expression": str(parsed.sympy_expr),
            "problem_type": problem_type,
        }

    def process_question(self, question: str) -> SolveData:
        """
        Runs the full end-to-end math pipeline to solve and produce step-by-step output.
        """
        normalized_text = normalize_khmer_text(question)
        intent = self.intent_classifier.classify(normalized_text)

        if intent == MathIntent.UNKNOWN:
            raise MathProcessingError("Could not detect a math request in the given text.")

        raw_expression = extract_expression(normalized_text)
        if raw_expression is None:
            raise MathProcessingError("Could not find a mathematical expression in the given text.")

        try:
            parsed = parse_math_text(raw_expression)
        except ExpressionParseError as exc:
            raise MathProcessingError(str(exc)) from exc

        problem_type = classify_problem(parsed)
        result = solve(parsed, problem_type)

        return SolveData(
            problem_type=problem_type,
            original_question=question,
            detected_intent=intent.value,
            normalized_expression=str(parsed.sympy_expr),
            variable=result.variable,
            answer=result.answer,
            is_verified=result.is_verified,
            steps=result.steps,
        )


@lru_cache
def get_math_service() -> MathService:
    """FastAPI dependency yielding a singleton MathService instance."""
    return MathService()


# Backward compatibility standalone function
def process_question(question: str) -> SolveData:
    return get_math_service().process_question(question)
