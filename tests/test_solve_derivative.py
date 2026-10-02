"""
Tests for calculus derivative solver, lesson-aware step generation, and Khmer BacII curriculum alignment.
"""

from __future__ import annotations

import pytest
import sympy
from sympy import Symbol

from app.classifier.context_aware_classifier import ContextAwareClassifier
from app.models.document import Instruction, InstructionType
from app.parser.exercise_parser.exercise_parser import parse_exercise
from app.parser.instruction_parser.instruction_detector import InstructionDetector
from app.parser.math_parser.expression_parser import parse_math_text
from app.reasoning.steps.registry import get_step_generator
from app.solvers.registry import get_solver


def test_derivative_solver_radical_chain():
    r"""Test image.png: y = \sqrt{x^2 - 1} -> y' = x / \sqrt{x^2 - 1}."""
    parsed = parse_math_text(r"y = \sqrt{x^2 - 1}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check pedagogical steps
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តប្រមាណវិធីដេរីវេ" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃកន្សោមខាងក្នុង" in result.steps[2].title_km
    assert "សម្រួលកន្សោម" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_radical_chain"
    assert "ជំពូកទី៣" in result.lesson_info["chapter_km"]


def test_derivative_solver_exponential_quotient_explain():
    """Test image1.png + explain.png: f(x) = e^x + 3 - e^x/(e^x + 3)."""
    parsed = parse_math_text(r"f(x) = e^x + 3 - \frac{e^x}{e^x + 3}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness against ground truth explain.png
    x = Symbol("x")
    expected = (sympy.exp(2 * x) + 6 * sympy.exp(x) + 6) * sympy.exp(x) / (sympy.exp(x) + 3) ** 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_exponential"
    assert "វិធានដេរីវេអិចស្បូណង់ស្យែល" in result.lesson_info["method_km"]


def test_derivative_solver_reciprocal_power():
    """Test telegram photo: y = 1 / (x^2 + 3x + 1)^2 -> y' = -2(2x + 3)/(x^2 + 3x + 1)^3."""
    parsed = parse_math_text(r"y = \frac{1}{(x^2 + 3x + 1)^2}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = -2 * (2 * x + 3) / (x**2 + 3 * x + 1) ** 3
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_reciprocal_power"
    assert "វិធានដេរីវេចម្រាសស្វ័យគុណ" in result.lesson_info["method_km"]


def test_end_to_end_telegram_exercise_pipeline():
    """Test full parsing and context classification on Telegram exercise text."""
    raw_text = r"គណនាដេរីវេនៃអនុគមន៍ខាងក្រោម ៈ ឃ. y = \frac{1}{(x^2 + 3x + 1)^2}"
    parsed_ex = parse_exercise(raw_text)
    assert parsed_ex.instruction is not None
    assert "គណនាដេរីវេ" in parsed_ex.instruction

    det = InstructionDetector()
    inst = det.detect(parsed_ex.instruction)
    assert inst is not None
    assert inst.action.value == "derive"

    inst_model = inst.to_instruction()
    assert inst_model.instruction_type == InstructionType.DERIVATIVE

    parsed_math = parse_math_text(parsed_ex.primary_expression)
    cac = ContextAwareClassifier()
    c_res = cac.classify(parsed_math, instruction=inst_model)
    assert c_res.problem_type == "calculus_derivative"

    solver = get_solver(c_res.problem_type)
    sol = solver.solve(parsed_math, c_res.problem_type)
    assert sol.answer is not None
    assert len(sol.steps) == 5


def test_function_definition_classified_as_derivative():
    """Test f(x) = ... is recognized as calculus_derivative."""
    parsed = parse_math_text(r"f(x) = x^3 - 3x + 2")
    cac = ContextAwareClassifier()
    c_res = cac.classify(parsed)
    assert c_res.problem_type == "calculus_derivative"

    solver = get_solver("calculus_derivative")
    sol = solver.solve(parsed, "calculus_derivative")
    assert sol.answer == "3*(x - 1)*(x + 1)" or sol.answer == "3*x**2 - 3"


def test_derivative_solver_image2_quotient_log():
    r"""Test image2.png: f(x) = \frac{x\ln x}{x+1} -> f'(x) = \frac{x + \ln x + 1}{(x+1)^2}."""
    parsed = parse_math_text(r"f(x) = \frac{x \ln x}{x + 1}")
    solver = get_solver("calculus_derivative")
    assert solver is not None

    result = solver.solve(parsed, "calculus_derivative")
    assert result.answer is not None
    assert len(result.steps) == 5

    # Check mathematical correctness
    x = Symbol("x")
    expected = (x + sympy.log(x) + 1) / (x + 1) ** 2
    ans_expr = sympy.sympify(result.answer)
    assert sympy.simplify(ans_expr - expected) == 0

    # Lesson awareness: quotient rule
    assert result.lesson_info is not None
    assert result.lesson_info["method_id"] == "method_derivative_quotient_rule"
    assert "ផលចែក" in result.lesson_info["method_km"]

    # Pedagogical steps in Khmer BacII format
    assert "កំណត់អនុគមន៍ដើម" in result.steps[0].title_km
    assert "អនុវត្តវិធានផលចែក" in result.steps[1].title_km
    assert "គណនាដេរីវេនៃភាគយក និងភាគបែង" in result.steps[2].title_km
    assert "ពង្រាយ និងសម្រួលភាគយក" in result.steps[3].title_km
    assert "សន្និដ្ឋានចម្លើយដេរីវេចុងក្រោយ" in result.steps[4].title_km

    # Verify \ln is used instead of \log in student steps
    for step in result.steps:
        assert r"\log" not in step.expression
        assert r"\log" not in step.description_km

