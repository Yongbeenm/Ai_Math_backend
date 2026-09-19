"""
The full pipeline for POST /api/v1/math/solve, matching the architecture
diagram in the handoff doc:

  Khmer text -> normalize -> detect intent -> extract expression
             -> parse (SymPy) -> classify problem type -> solve + verify
             -> step-by-step (Khmer) -> SolveData
"""
from __future__ import annotations

from app.core.engine.classifier import classify_problem
from app.core.engine.solver import solve
from app.core.khmer.extractor import extract_expression
from app.core.khmer.intent import MathIntent, RuleBasedIntentClassifier
from app.core.khmer.normalizer import normalize_khmer_text
from app.core.parser.expression_parser import ExpressionParseError, parse_math_text
from app.models.schemas import SolveData

_intent_classifier = RuleBasedIntentClassifier()


class MathProcessingError(Exception):
    """Raised for any failure that should become `{"success": false, "error": ...}`
    rather than an HTTP 500 — bad/ambiguous input, not a server bug."""


def process_question(question: str) -> SolveData:
    normalized_text = normalize_khmer_text(question)
    intent = _intent_classifier.classify(normalized_text)

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
