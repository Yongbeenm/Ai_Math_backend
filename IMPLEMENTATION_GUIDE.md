# Implementation Guide for Remaining Tasks

This document provides detailed guidance for completing the remaining upgrade tasks (5-10).

## Task #5: Build Multi-Exercise Support

### What to Do:
Integrate the existing `exercise_parser.py` into the main pipeline to handle images with multiple problems (e.g., "Exercise 1: a) 2x+5=15, b) x²-4=0").

### Implementation Steps:

1. **Update `vision_service.py`** to detect multi-exercise scenarios:
```python
from app.models.problem import MultiProblemSet
from app.core.khmer.exercise_parser import parse_exercise

def process_image(self, image_bytes: bytes) -> dict | MultiProblemSet:
    vision_result = self.vision_engine.detect(image_bytes)
    
    # Parse exercise structure
    parsed_exercise = parse_exercise(vision_result.detected_text)
    
    # If multiple sub-exercises found, create MultiProblemSet
    if len(parsed_exercise.sub_exercises) > 1:
        problem_set = MultiProblemSet(
            exercise_title=parsed_exercise.exercise_title,
            instruction=parsed_exercise.instruction,
        )
        
        # Build each sub-problem
        for sub in parsed_exercise.sub_exercises:
            problem = build_problem(
                text=sub.expression,
                source=ProblemSource.OCR,
                ocr_confidence=vision_result.confidence,
            )
            problem.metadata["label"] = sub.label
            problem_set.add_problem(problem)
        
        return problem_set.to_dict()
    else:
        # Single problem - existing flow
        return self.process_single_problem(...)
```

2. **Create new API endpoint** `POST /math/vision/batch`:
```python
@router.post("/vision/batch")
async def solve_vision_batch(image: UploadFile):
    result = vision_service.process_image(image_bytes)
    
    if isinstance(result, MultiProblemSet):
        # Solve all problems in batch
        solutions = []
        for problem in result.problems:
            solution = math_service.solve(problem)
            solutions.append(solution)
        
        return {
            "exercise_title": result.exercise_title,
            "solutions": solutions
        }
```

3. **Test with multi-problem images** from `training/sample_data/images/`

---

## Task #6: Create Comprehensive Khmer Explanation Templates

### What to Do:
Build a template-based localization system for generating Khmer explanations from operation metadata.

### Implementation Steps:

1. **Create `app/core/localization/templates.py`**:
```python
class ExplanationTemplates:
    """Template-based explanation system."""
    
    KHMER_TEMPLATES = {
        "add_to_both_sides": "បូក {value} ទៅភាគីទាំងពីរ",
        "subtract_from_both_sides": "ដក {value} ពីភាគីទាំងពីរ",
        "multiply_both_sides": "គុណភាគីទាំងពីរដោយ {value}",
        "divide_both_sides": "ចែកភាគីទាំងពីរដោយ {value}",
        "isolate_variable": "ដាច់ {variable} ចេញដាច់ដោយឡែក",
        "combine_like_terms": "បូករួមធាតុដូចគ្នា",
        "factor": "បំបែកជាកត្តា",
        "expand": "ពង្រីក",
        "simplify": "សាមញ្ញកម្ម",
        "original_equation": "សមីការដើម",
        "final_answer": "ចម្លើយចុងក្រោយ",
    }
    
    ENGLISH_TEMPLATES = {
        "add_to_both_sides": "Add {value} to both sides",
        "subtract_from_both_sides": "Subtract {value} from both sides",
        # ... etc
    }
    
    def explain(self, operation: OperationType, values: dict, language: str = "km"):
        template_key = get_operation_template_key(operation)
        templates = self.KHMER_TEMPLATES if language == "km" else self.ENGLISH_TEMPLATES
        template = templates.get(template_key, "Step")
        return template.format(**values)
```

2. **Integrate with step generators**:
- Update each step generator to use templates instead of hardcoded strings
- Pass operation metadata to template system

3. **Expand templates** with:
- Conditional logic (e.g., "If negative, reverse inequality")
- Contextual explanations (e.g., "Because we're dividing by negative...")
- Common mistakes warnings

---

## Task #7: Add Verification Layer Improvements

### What to Do:
Create a dedicated verification module with different strategies per problem type.

### Implementation Steps:

1. **Create `app/core/verification/verifier.py`**:
```python
class SolutionVerifier:
    """Verifies solutions by substitution and logical checks."""
    
    def verify(self, problem: MathProblem, solution: str) -> VerificationResult:
        if problem.problem_type == "linear_equation":
            return self._verify_linear(problem, solution)
        elif problem.problem_type == "quadratic_equation":
            return self._verify_quadratic(problem, solution)
        # ... etc
    
    def _verify_linear(self, problem, solution):
        # Substitute solution back into original equation
        # Check if both sides are equal
        # Return confidence score
        pass
```

2. **Add verification metadata** to SolveResult:
```python
@dataclass
class VerificationResult:
    is_verified: bool
    confidence: float
    substitution_lhs: str
    substitution_rhs: str
    error_margin: float
    notes: list[str]
```

3. **Verify before returning**: Always verify in solver before returning answer

---

## Task #8: Implement End-to-End Pipeline Tests

### What to Do:
Create comprehensive tests covering the complete OCR → Solve → Verify → Explain flow.

### Implementation Steps:

1. **Create `tests/test_pipeline_endtoend.py`**:
```python
def test_manual_input_linear():
    """Test: Typed text → Solution"""
    problem = build_problem("2x + 5 = 15", language="km")
    
    assert problem.problem_type == "linear_equation"
    assert problem.overall_confidence > 0.8
    
    solution = solve(problem)
    assert solution.answer == "5"
    assert solution.is_verified == True
    assert len(solution.steps) > 0


def test_ocr_input_quadratic():
    """Test: OCR text → Solution"""
    problem = build_problem(
        "x^2 - 5x + 6 = 0",
        source=ProblemSource.OCR,
        ocr_confidence=0.92
    )
    
    assert problem.problem_type == "quadratic_equation"
    # ... test solution
```

2. **Test normalization pipeline**:
```python
def test_normalization_khmer_digits():
    result = normalize_text("២x + ៥ = ១៥")
    assert "2x + 5 = 15" in result.normalized_text
    assert NormalizationStep.KHMER_DIGITS in result.steps_applied
```

3. **Test confidence tracking**:
```python
def test_low_confidence_warning():
    problem = build_problem("unclear text", ocr_confidence=0.3)
    assert problem.requires_review() == True
    assert len(problem.warnings) > 0
```

4. **Run tests**: `pytest tests/test_pipeline_endtoend.py -v`

---

## Task #9: Create API Endpoint for Problem Review/Correction

### What to Do:
Add an endpoint where users can review/edit OCR results before solving.

### Implementation Steps:

1. **Create new endpoint** `POST /math/review`:
```python
class ReviewRequest(BaseModel):
    original_text: str
    corrected_text: str | None
    ocr_confidence: float
    language: str = "km"


@router.post("/review")
async def review_problem(request: ReviewRequest):
    """
    Review OCR result before solving.
    
    Returns problem analysis with confidence, detected type,
    and warnings. User can correct text before submitting to solve.
    """
    # Build problem from original OCR text
    problem = build_problem(
        text=request.original_text,
        source=ProblemSource.OCR,
        ocr_confidence=request.ocr_confidence,
        language=request.language,
    )
    
    response = {
        "original": request.original_text,
        "normalized": problem.expression,
        "problem_type": problem.problem_type,
        "confidence": problem.overall_confidence,
        "warnings": problem.warnings,
        "requires_review": problem.requires_review(),
        "characteristics": problem.characteristics.to_dict(),
    }
    
    # If user provided correction, also analyze that
    if request.corrected_text:
        corrected = build_problem(
            text=request.corrected_text,
            source=ProblemSource.MANUAL,
            language=request.language,
        )
        response["corrected_analysis"] = corrected.to_dict()
    
    return APIResponse(success=True, data=response)
```

2. **Update `/math/solve`** to accept MathProblem objects:
```python
@router.post("/solve")
async def solve_problem(request: SolveRequest | dict):
    if isinstance(request, dict) and "problem" in request:
        # Pre-built problem from review
        problem = MathProblem(**request["problem"])
    else:
        # Legacy: build from question text
        problem = build_problem(request.question, language=request.language)
    
    # Solve
    solution = math_service.solve(problem)
    return APIResponse(success=True, data=solution)
```

---

## Task #10: Update Documentation and Create Testing Guide

### What to Do:
Document the new architecture and provide testing instructions.

### Files to Update:

1. **README.md**:
- Update architecture diagram
- Add new endpoints
- Explain confidence scoring
- Add MathProblem representation example

2. **docs/API_CONTRACT.md**:
- Document `/math/review` endpoint
- Document `/math/vision/batch` endpoint
- Add MathProblem schema
- Add confidence scoring explanation

3. **Create `docs/TESTING_GUIDE.md`**:
```markdown
# Testing Guide

## Testing the Complete OCR → Solve Flow

### 1. Manual Input (Typed)
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/math/solve \\
  -H "Content-Type: application/json" \\
  -d '{
    "language": "km",
    "question": "ដោះស្រាយ 2x + 5 = 15"
  }'
\`\`\`

Expected: Confidence ~1.0, problem_type="linear_equation", answer="5"

### 2. OCR Input (Image)
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/math/vision \\
  -F "image=@test_image.jpg"
\`\`\`

Expected: OCR confidence, normalization steps, solution with metadata

### 3. Review Before Solving
\`\`\`bash
# Step 1: Review OCR result
curl -X POST http://localhost:8000/api/v1/math/review \\
  -H "Content-Type: application/json" \\
  -d '{
    "original_text": "2x + S = 15",
    "ocr_confidence": 0.85,
    "corrected_text": "2x + 5 = 15"
  }'

# Step 2: Solve with correction
curl -X POST http://localhost:8000/api/v1/math/solve \\
  -d '{"question": "2x + 5 = 15"}'
\`\`\`

### 4. Batch Problems
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/math/vision/batch \\
  -F "image=@exercise_sheet.jpg"
\`\`\`

Expected: Multiple problems solved with labels (a, b, c, etc.)
```

---

## 🎯 Integration Checklist

Before deploying, verify:

- [ ] All existing tests still pass
- [ ] New pipeline tests pass
- [ ] Backward compatibility maintained
- [ ] API documentation updated
- [ ] Example requests work
- [ ] Confidence thresholds tuned
- [ ] Error handling tested
- [ ] Performance acceptable (<1s per problem)

---

## 🚀 Quick Start Testing

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run existing tests**:
```bash
pytest -v
```

3. **Start server**:
```bash
uvicorn app.main:app --reload
```

4. **Test new problem builder**:
```python
from app.core.problem_builder import build_problem

# Test manual input
problem = build_problem("2x + 5 = 15", language="km")
print(f"Type: {problem.problem_type}")
print(f"Confidence: {problem.overall_confidence}")
print(f"Expression: {problem.expression}")

# Test with Khmer digits
problem = build_problem("២x + ៥ = ១៥", language="km")
print(f"Normalized: {problem.normalization.normalized_text}")
```

5. **Test normalization**:
```python
from app.core.normalization import normalize_text

result = normalize_text("២x² + ៥x = ១៥", is_from_ocr=True)
print(f"Original: {result.original_text}")
print(f"Normalized: {result.normalized_text}")
print(f"Confidence: {result.confidence}")
print(f"Steps: {[s.value for s in result.steps_applied]}")
```

6. **Test enhanced classifier**:
```python
from app.core.parser.expression_parser import parse_math_text
from app.core.engine.classifier_enhanced import classify_with_characteristics

parsed = parse_math_text("x^2 - 5x + 6 = 0")
problem_type, chars = classify_with_characteristics(parsed)

print(f"Type: {problem_type}")
print(f"Has exponents: {chars.has_exponents}")
print(f"Degree: {chars.max_polynomial_degree}")
```

---

## 📊 What Changed in the Architecture

### Before:
```
OCR → normalize_khmer_text() → extract_expression() → parse_math_text() 
→ classify_problem() → solve() → steps[]
```

### After:
```
OCR/Typed Input
    ↓
NormalizationPipeline (with confidence tracking)
    ↓
ProblemBuilder
    ├─ Intent Detection
    ├─ Expression Extraction
    ├─ Mathematical Parsing
    └─ Enhanced Classification
    ↓
MathProblem Object (full metadata)
    ↓
Solver (unchanged, deterministic SymPy)
    ↓
SolutionSteps (with operation metadata)
    ↓
Verification (substitution check)
    ↓
Explanation (template-based)
```

### Key Improvements:
1. **Confidence tracking** at every stage
2. **Structured representation** (MathProblem) between OCR and solver
3. **Enhanced classification** with 20+ problem types
4. **Operation metadata** in steps for explainability
5. **Warning system** for ambiguous cases
6. **Batch problem** support
7. **Review/correction** capability
8. **Backward compatible** with existing code

---

## 🔍 Debugging Tips

### Check normalization:
```python
from app.core.normalization import normalize_text

result = normalize_text("your text here", is_from_ocr=True)
print("Transformations:", result.transformations)
print("Warnings:", result.warnings)
```

### Check problem building:
```python
from app.core.problem_builder import build_problem

try:
    problem = build_problem("your text")
    print("Success:", problem.to_dict())
except Exception as e:
    print("Error:", e)
```

### Check confidence:
```python
problem = build_problem("unclear OCR text", ocr_confidence=0.3)
print("Overall confidence:", problem.overall_confidence)
print("Requires review:", problem.requires_review())
print("Warnings:", problem.warnings)
```

---

## 📞 Support

For issues:
1. Check logs for detailed error messages
2. Verify input format matches schema
3. Test with known-good examples
4. Check confidence scores for low values
5. Review warnings for hints about issues

---

**Implementation Status**: 4/10 tasks complete
**Estimated Time for Remaining**: 6-8 hours
**Priority**: Tasks 5, 8, 9 (for production readiness)
