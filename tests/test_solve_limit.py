"""
Unit and integration tests for calculus limit solving and Khmer/English step generation.
Covers Cambodian Grade 12 BacII exam questions and general calculus limits.
"""
import pytest
from fastapi.testclient import TestClient

from app.core.engine.classifier import classify_problem
from app.core.engine.solver import solve
from app.core.parser.expression_parser import parse_math_text
from app.main import app
from app.services.math_service import process_question


@pytest.fixture
def client():
    return TestClient(app)


class TestLimitCalculusEngine:
    """Tests deterministic limit calculations and step-by-step narration."""

    def test_bacii_trigonometric_limit(self):
        """BacII Problem C: lim_{x->0} sin^2(x) / (1 - cos^4(x)) = 1/2"""
        expr_str = r"\lim_{x \to 0} \frac{\sin^2 x}{1 - \cos^4 x}"
        parsed = parse_math_text(expr_str)
        problem_type = classify_problem(parsed)
        assert problem_type == "calculus_limit"

        result = solve(parsed, problem_type)
        assert result.answer == "1/2"
        assert result.is_verified is True
        assert len(result.steps) >= 3

        # Check pedagogical steps
        step_descriptions = [s.description_km for s in result.steps]
        assert any("០/០" in d or "0/0" in d or "រាងមិនកំណត់" in d for d in step_descriptions)
        assert any("ត្រីកោណមាត្រ" in d for d in step_descriptions)

    def test_bacii_rational_polynomial_limit(self):
        """BacII Problem A: lim_{x->3} (x^3 - 5x - 12) / (2x^2 - 5x - 3) = 22/7"""
        expr_str = r"A = \lim_{x \to 3} \frac{x^3 - 5x - 12}{2x^2 - 5x - 3}"
        parsed = parse_math_text(expr_str)
        problem_type = classify_problem(parsed)
        assert problem_type == "calculus_limit"

        result = solve(parsed, problem_type)
        assert result.answer == "22/7"
        assert result.variable == "A"
        assert result.is_verified is True
        assert len(result.steps) >= 3

        # Check factoring step
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ផលគុណកត្តា" in d for d in step_descriptions)

    def test_bacii_radical_conjugate_limit(self):
        """BacII Problem B: lim_{x->0} (sqrt(1+x) - sqrt(1-x)) / sin(3x) = 1/3"""
        expr_str = r"B = \lim_{x \to 0} \frac{\sqrt{1+x} - \sqrt{1-x}}{\sin 3x}"
        parsed = parse_math_text(expr_str)
        problem_type = classify_problem(parsed)
        assert problem_type == "calculus_limit"

        result = solve(parsed, problem_type)
        assert result.answer == "1/3"
        assert result.variable == "B"
        assert result.is_verified is True

    def test_direct_substitution_limit(self):
        """Continuous rational function at x = 3: (x^2 + 13) / (x + 4) = 22/7"""
        expr_str = r"\lim_{x \to 3} \frac{x^2 + 13}{x + 4}"
        parsed = parse_math_text(expr_str)
        problem_type = classify_problem(parsed)
        assert problem_type == "calculus_limit"

        result = solve(parsed, problem_type)
        assert result.answer == "22/7"
        assert result.is_verified is True
        step_descriptions = [s.description_km for s in result.steps]
        assert any("ជាប់" in d or "ដោយផ្ទាល់" in d for d in step_descriptions)

    def test_standard_polynomial_factor_limit(self):
        """Standard limit: lim_{x->3} (x^2 - 9) / (x - 3) = 6"""
        expr_str = r"\lim_{x \to 3} \frac{x^2 - 9}{x - 3}"
        data = process_question(expr_str)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "6"
        assert data.is_verified is True


class TestLimitServiceAndAPI:
    """Tests the full API pipeline with Khmer natural language prompts."""

    def test_solve_khmer_prompt(self, client):
        payload = {
            "language": "km",
            "question": r"គណនាលីមីតខាងក្រោម៖ \lim_{x \to 0} \frac{\sin^2 x}{1 - \cos^4 x}",
        }
        response = client.post("/api/v1/math/solve", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["problem_type"] == "calculus_limit"
        assert body["data"]["answer"] == "1/2"
        assert len(body["data"]["steps"]) >= 3

    def test_solve_english_prompt(self, client):
        payload = {
            "language": "en",
            "question": r"Calculate the limit: \lim_{x \to 3} \frac{x^2 - 9}{x - 3}",
        }
        response = client.post("/api/v1/math/solve", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["answer"] == "6"

    def test_ocr_latex_artifact_cleaning(self):
        """Pix2tex raw OCR outputs with \operatorname*{lim}, spaced letters and trailing punctuation."""
        raw_ocr = r"c=\operatorname*{lim}_{x\to0}{\frac{s i n^{2}x}{1-c o s^{4}x}}\;."
        data = process_question(raw_ocr)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "1/2"
        assert data.variable == "c"

    def test_ocr_label_prefix_mathcal_q(self):
        """Khmer label 'ខ.' transcribed by OCR as '\mathcal{Q}.' before limit formula."""
        raw_ocr = r"\mathcal{Q}.\lim_{x\rightarrow3}\frac{x^{3}-3x^{2}+45x-135}{x^{3}-27}"
        data = process_question(raw_ocr)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "2"

    def test_khmer_label_and_instruction(self):
        """Khmer instruction with sub-exercise label 'ខ.' and limit formula."""
        raw = r"គណនាលីមីត ខ. \lim_{x \to 3} \frac{x^3 - 3x^2 + 45x - 135}{x^3 - 27}"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "2"

    def test_numeric_label_no_space(self):
        """Numeric label without space before limit."""
        raw = r"2.\lim_{x \to 3} \frac{x^3 - 3x^2 + 45x - 135}{x^3 - 27}"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "2"

    def test_ascii_limit_arrow(self):
        """ASCII limit arrow 'lim_{x->3}' parses and solves."""
        raw = r"lim_{x->3} (x^2 - 9)/(x - 3)"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "6"

    def test_bacii_header_instruction_and_label_with_trig(self):
        """Khmer BacII textbook format: 'លំហាត់ទី១ គណនាលីមីតខាងក្រោម៖ ក. \\lim_{x \\to 0} \\frac{\\sin(2x)}{x}'"""
        raw = r"លំហាត់ទី១ គណនាលីមីតខាងក្រោម៖ ក. \lim_{x \to 0} \frac{\sin(2x)}{x}"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "2"

    def test_instruction_with_parenthesized_letter_label(self):
        """Instruction with '(a)' item label and trig function argument '(2x)'."""
        raw = r"គណនាលីមីតខាងក្រោម៖ (a) lim_{x->0} sin(2x)/x"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "2"

    def test_instruction_with_parenthesized_number_label(self):
        """Instruction with '(1)' item label and cosine expression."""
        raw = r"គណនាលីមីតខាងក្រោម៖ (1) lim_{x->0} (1 - cos(x))/x^2"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "1/2"

    def test_trig_limit_multiple_arguments_not_corrupted(self):
        """Trigonometric arguments like (3x) and (5x) should never be treated as labels."""
        raw = r"គណនាលីមីត lim_{x->0} (sin(3x))/(sin(5x))"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "3/5"

    def test_english_phrase_find_the_following_limit(self):
        """English phrasing 'Find the following limit:'."""
        raw = r"Find the following limit: \lim_{x \to 1} \frac{x^2 - 1}{x - 1}"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "2"

    def test_ascii_sqrt_limit(self):
        """ASCII limit containing sqrt: 'A = lim_{x->0} (sqrt(1+x) - 1)/x'."""
        raw = r"A = lim_{x->0} (sqrt(1+x) - 1)/x"
        data = process_question(raw)
        assert data.problem_type == "calculus_limit"
        assert data.answer == "1/2"
