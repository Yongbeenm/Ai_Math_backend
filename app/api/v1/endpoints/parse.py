"""
POST /api/v1/math/parse — returns just the detected intent and normalized
expression without solving. Useful for the mobile app to show "Detected
equation: 2x + 5 = 15" and let the user confirm/edit before solving, per
the 'Display detected equation' feature in the handoff doc.
"""
from fastapi import APIRouter

from app.core.engine.classifier import classify_problem
from app.core.khmer.extractor import extract_expression
from app.core.khmer.intent import RuleBasedIntentClassifier
from app.core.khmer.normalizer import normalize_khmer_text
from app.core.parser.expression_parser import ExpressionParseError, parse_math_text
from app.models.schemas import APIResponse, SolveRequest

router = APIRouter()
_intent_classifier = RuleBasedIntentClassifier()


@router.post("/math/parse", response_model=APIResponse, tags=["math"])
def parse_math(payload: SolveRequest) -> APIResponse:
    normalized_text = normalize_khmer_text(payload.question)
    intent = _intent_classifier.classify(normalized_text)
    raw_expression = extract_expression(normalized_text)

    if raw_expression is None:
        return APIResponse(success=False, error="No math expression detected.")

    try:
        parsed = parse_math_text(raw_expression)
    except ExpressionParseError as exc:
        return APIResponse(success=False, error=str(exc))

    problem_type = classify_problem(parsed)
    return APIResponse(
        success=True,
        data={
            "detected_intent": intent.value,
            "raw_expression": raw_expression,
            "normalized_expression": str(parsed.sympy_expr),
            "problem_type": problem_type,
        },
    )
