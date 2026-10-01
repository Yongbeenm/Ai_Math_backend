# Backend Architecture Refactoring Plan

## Current Structure Analysis

The current project has good separation but mixes some concerns. Here's what exists and where it should go:

## Mapping: Current → Target Architecture

### 1. API Layer (Already Well Structured) ✅

**Current Location**: `app/api/v1/`

**Target**: `app/api/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/api/v1/endpoints/                →  app/api/routes/
  ├── solve.py                       →    ├── solve.py
  ├── parse.py                       →    ├── parse.py
  ├── vision.py                      →    ├── vision.py
  ├── history.py                     →    ├── history.py
  └── health.py                      →    └── health.py

app/api/v1/router.py                 →  app/api/routes/__init__.py

app/models/schemas.py                →  app/api/schemas/
  ├── SolveRequest                   →    ├── requests.py
  ├── SolutionStep                   →    ├── responses.py
  ├── SolveData                      →    └── common.py
  ├── APIResponse
  └── HealthResponse
```

**Actions**:
- ✅ Keep existing structure (already good)
- Move `schemas.py` → `app/api/schemas/`
- Flatten `v1/` (we can add versioning later if needed)

---

### 2. OCR Layer (Currently: app/core/vision/)

**Current Location**: `app/core/vision/`

**Target**: `app/ocr/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/vision/preprocessor.py     →  app/ocr/preprocessing/
                                         ├── image_preprocessor.py
                                         └── __init__.py

app/core/vision/                     →  app/ocr/extraction/
  ├── kiri_ocr.py                    →    ├── kiri_engine.py
  ├── gemini_vision.py               →    ├── gemini_engine.py
  ├── google_vision.py               →    ├── google_engine.py
  ├── mathpix.py                     →    ├── mathpix_engine.py
  ├── pix2tex_engine.py              →    ├── pix2tex_engine.py
  ├── tesseract.py                   →    ├── tesseract_engine.py
  ├── base.py                        →    ├── base.py
  ├── factory.py                     →    ├── factory.py
  ├── ensemble.py                    →    ├── ensemble.py
  ├── router.py                      →    ├── router.py
  ├── evaluation.py                  →    ├── evaluation.py
  ├── cache.py                       →    ├── cache.py
  └── stub.py                        →    └── stub.py

app/core/vision/postprocessor.py    →  app/ocr/normalization/
                                         ├── ocr_postprocessor.py
                                         └── __init__.py
```

**Actions**:
- Move `app/core/vision/` → `app/ocr/`
- Split into three submodules: preprocessing, extraction, normalization
- Keep existing base/factory pattern

---

### 3. Parser Layer (Currently: Scattered)

**Current Location**: Multiple places

**Target**: `app/parser/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/parser/expression_parser.py →  app/parser/math_parser/
                                         ├── expression_parser.py
                                         └── __init__.py

app/core/khmer/normalizer.py        →  app/parser/expression_parser/
app/core/khmer/digits.py            →    ├── khmer_normalizer.py
                                         ├── khmer_digits.py
                                         └── __init__.py

app/core/khmer/exercise_parser.py   →  app/parser/exercise_parser/
                                         ├── exercise_parser.py
                                         └── __init__.py

app/core/normalization/pipeline.py  →  app/parser/normalization/
                                         ├── normalization_pipeline.py
                                         └── __init__.py
```

**Actions**:
- Create unified `app/parser/` module
- Group math parsing, Khmer processing, and exercise parsing
- Keep normalization as parser submodule

---

### 4. Classifier Layer (Currently: app/core/engine/)

**Current Location**: `app/core/engine/`

**Target**: `app/classifier/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/engine/classifier.py       →  app/classifier/problem_classifier/
app/core/engine/classifier_enhanced.py → ├── classifier.py
                                         ├── enhanced_classifier.py
                                         └── __init__.py

app/core/khmer/intent.py            →  app/classifier/problem_classifier/
                                         ├── intent_classifier.py
                                         └── (integrated above)

(Future)                             →  app/classifier/lesson_classifier/
                                         ├── lesson_matcher.py
                                         └── __init__.py
```

**Actions**:
- Move classifiers from `app/core/engine/` to `app/classifier/`
- Integrate intent classification
- Keep lesson_classifier/ empty for future use

---

### 5. Knowledge Layer (New - For Future)

**Target**: `app/knowledge/`
```
Target Structure (Future)
─────────────────────────────────────────────────────────────
app/knowledge/
  ├── lessons/
  │   ├── algebra_basics.py
  │   ├── quadratic_equations.py
  │   └── __init__.py
  │
  ├── concepts/
  │   ├── equations.py
  │   ├── inequalities.py
  │   └── __init__.py
  │
  ├── rules/
  │   ├── algebraic_rules.py
  │   └── __init__.py
  │
  ├── methods/
  │   ├── solving_methods.py
  │   └── __init__.py
  │
  └── examples/
      └── __init__.py
```

**Actions**:
- Create empty structure for future knowledge base
- Do NOT create unnecessary files yet
- This is for structured math knowledge (lesson content, rules, theorems)

---

### 6. Solvers Layer (Currently: app/core/engine/)

**Current Location**: `app/core/engine/solver.py`

**Target**: `app/solvers/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/engine/solver.py           →  app/solvers/
                                         ├── base_solver.py
                                         ├── solver_registry.py
                                         └── __init__.py

(Extract from solver.py)             →  app/solvers/algebra/
                                         ├── linear_solver.py
                                         ├── quadratic_solver.py
                                         ├── polynomial_solver.py
                                         ├── system_solver.py
                                         ├── inequality_solver.py
                                         └── __init__.py

(Extract from solver.py)             →  app/solvers/arithmetic/
                                         ├── expression_evaluator.py
                                         └── __init__.py

(Future)                             →  app/solvers/calculus/
                                         ├── limit_solver.py
                                         ├── derivative_solver.py
                                         └── __init__.py

(Future)                             →  app/solvers/geometry/
(Future)                             →  app/solvers/complex_numbers/
```

**Actions**:
- Split monolithic `solver.py` by problem type
- Create solver registry for dynamic dispatch
- Extract logic into domain-specific solvers
- Keep calculus/geometry/complex as placeholders

---

### 7. Reasoning Layer (Currently: app/core/engine/steps/)

**Current Location**: `app/core/engine/steps/`

**Target**: `app/reasoning/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/engine/steps/               →  app/reasoning/steps/
  ├── base.py                        →    ├── base_generator.py
  ├── linear.py                      →    ├── linear_steps.py
  ├── quadratic.py                   →    ├── quadratic_steps.py
  ├── polynomial.py                  →    ├── polynomial_steps.py
  ├── system.py                      →    ├── system_steps.py
  ├── inequality.py                  →    ├── inequality_steps.py
  ├── calculus_limit.py              →    ├── calculus_steps.py
  ├── registry.py                    →    ├── registry.py
  └── __init__.py                    →    └── __init__.py

app/core/engine/operations.py       →  app/reasoning/operations/
                                         ├── operation_types.py
                                         ├── transformation_types.py
                                         ├── step_builder.py
                                         └── __init__.py

app/core/problem_builder.py         →  app/reasoning/solution_builder/
                                         ├── problem_builder.py
                                         └── __init__.py
```

**Actions**:
- Move step generation to `app/reasoning/steps/`
- Move operations to `app/reasoning/operations/`
- Move problem builder to `app/reasoning/solution_builder/`

---

### 8. Verification Layer (Already Structured) ✅

**Current Location**: `app/core/verification/`

**Target**: `app/verification/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/verification/               →  app/verification/
  ├── verifier.py                    →    ├── verifier.py
  ├── __init__.py                    →    ├── strategies.py (future)
                                          └── __init__.py

app/core/engine/verification.py     →  (DEPRECATE - use new verifier)
```

**Actions**:
- Move `app/core/verification/` → `app/verification/`
- Deprecate old `app/core/engine/verification.py`

---

### 9. Explanation Layer (Currently: app/core/localization/)

**Current Location**: `app/core/localization/`

**Target**: `app/explanation/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/localization/templates.py  →  app/explanation/templates/
                                         ├── operation_templates.py
                                         ├── number_formatter.py
                                         └── __init__.py

(Future)                             →  app/explanation/generators/
                                         ├── step_explainer.py
                                         ├── concept_explainer.py
                                         └── __init__.py
```

**Actions**:
- Move `app/core/localization/` → `app/explanation/templates/`
- Keep generators/ empty for future context-aware explanations

---

### 10. Localization Layer (New Structure)

**Current**: Embedded in explanation templates

**Target**: `app/localization/`
```
Target Structure
─────────────────────────────────────────────────────────────
app/localization/
  ├── km/
  │   ├── terminology.py         # Mathematical terms in Khmer
  │   ├── messages.py            # UI messages
  │   └── __init__.py
  │
  ├── en/
  │   ├── terminology.py         # Mathematical terms in English
  │   ├── messages.py            # UI messages
  │   └── __init__.py
  │
  └── translator.py              # Language switching logic
```

**Actions**:
- Extract language-specific content from templates
- Create structured localization for UI and math terminology
- Keep templates language-agnostic

---

### 11. Models Layer (Needs Splitting)

**Current Location**: `app/models/`

**Target**: `app/models/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/models/problem.py               →  app/models/
                                         ├── problem.py (keep)
                                         └── __init__.py

app/models/schemas.py               →  app/api/schemas/ (moved above)

app/models/db_models.py             →  app/models/
                                         ├── database.py
                                         └── (keep separate)
```

**Actions**:
- Move API schemas to `app/api/schemas/`
- Keep domain models (`problem.py`) in `app/models/`
- Keep DB models separate

---

### 12. Services Layer (Keep with Refactoring)

**Current Location**: `app/services/`

**Target**: `app/services/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/services/math_service.py        →  app/services/
                                         ├── math_service.py (refactor)
                                         └── __init__.py

app/services/vision_service.py      →  (MOVE to app/ocr/vision_service.py)

app/services/history_service.py     →  app/services/
                                         ├── history_service.py (keep)
                                         └── (keep)
```

**Actions**:
- Refactor `math_service.py` to use new module structure
- Move `vision_service.py` closer to OCR modules
- Keep `history_service.py` as-is

---

### 13. Other Modules

**Current**: `app/core/`, `app/repositories/`, `app/db/`, `app/config.py`

**Target**: `app/utils/`, `app/config/`
```
Current                              →  Target
─────────────────────────────────────────────────────────────
app/core/exceptions.py              →  app/utils/exceptions.py
app/core/logging.py                 →  app/utils/logging.py
app/core/middleware.py              →  app/utils/middleware.py

app/config.py                        →  app/config/settings.py

app/repositories/                    →  app/repositories/ (keep)
app/db/                              →  app/db/ (keep)
```

**Actions**:
- Move utility functions to `app/utils/`
- Keep DB and repositories as-is
- Organize config as module

---

## Final Target Structure

```
app/
├── api/                          # API Layer
│   ├── routes/                   # ✅ Endpoints (flatten from v1)
│   └── schemas/                  # ✅ Request/Response models
│
├── ocr/                          # OCR Layer (from app/core/vision)
│   ├── preprocessing/            # ✅ Image preprocessing
│   ├── extraction/               # ✅ OCR engines
│   └── normalization/            # ✅ OCR postprocessing
│
├── parser/                       # Parser Layer (from multiple locations)
│   ├── math_parser/              # ✅ Expression parsing
│   ├── expression_parser/        # ✅ Khmer normalization
│   ├── exercise_parser/          # ✅ Exercise structure parsing
│   └── normalization/            # ✅ Unified normalization
│
├── classifier/                   # Classifier Layer
│   └── problem_classifier/       # ✅ Problem type classification
│
├── knowledge/                    # Knowledge Layer (NEW - Future)
│   ├── lessons/                  # 🔮 Lesson content
│   ├── concepts/                 # 🔮 Mathematical concepts
│   ├── rules/                    # 🔮 Mathematical rules
│   ├── methods/                  # 🔮 Solution methods
│   └── examples/                 # 🔮 Worked examples
│
├── solvers/                      # Solvers Layer (split from solver.py)
│   ├── algebra/                  # ✅ Linear, quadratic, systems
│   ├── arithmetic/               # ✅ Expression evaluation
│   ├── calculus/                 # 🔮 Limits, derivatives (future)
│   ├── geometry/                 # 🔮 Future
│   └── complex_numbers/          # 🔮 Future
│
├── reasoning/                    # Reasoning Layer
│   ├── steps/                    # ✅ Step generators
│   ├── operations/               # ✅ Operation types
│   └── solution_builder/         # ✅ Problem builder
│
├── verification/                 # Verification Layer
│   └── verifier.py               # ✅ Solution verification
│
├── explanation/                  # Explanation Layer
│   ├── templates/                # ✅ Bilingual templates
│   └── generators/               # 🔮 Context-aware (future)
│
├── localization/                 # Localization Layer (NEW)
│   ├── km/                       # 🔮 Khmer terminology
│   └── en/                       # 🔮 English terminology
│
├── models/                       # Domain Models
│   ├── problem.py                # ✅ Keep
│   └── database.py               # ✅ DB models
│
├── services/                     # Service Layer
│   ├── math_service.py           # ✅ Refactor to use new structure
│   └── history_service.py        # ✅ Keep as-is
│
├── utils/                        # Utilities
│   ├── exceptions.py             # ✅ From core/
│   ├── logging.py                # ✅ From core/
│   └── middleware.py             # ✅ From core/
│
├── config/                       # Configuration
│   └── settings.py               # ✅ From config.py
│
├── repositories/                 # ✅ Keep as-is
├── db/                           # ✅ Keep as-is
└── main.py                       # ✅ Keep
```

Legend:
- ✅ = Exists, needs moving/refactoring
- 🔮 = Future expansion, keep empty/minimal

---

## Migration Strategy

### Phase 1: Foundation (Non-Breaking)
1. Create new directory structure (empty modules)
2. Copy files to new locations (keep old ones)
3. Add imports from new locations to old files
4. Update tests to use new imports (but keep old ones working)

### Phase 2: Refactoring
5. Split `solver.py` into domain-specific solvers
6. Refactor `math_service.py` to use new module structure
7. Update internal imports throughout codebase
8. Ensure all 130+ tests still pass

### Phase 3: Cleanup
9. Deprecate old locations (add warnings)
10. Update documentation
11. Remove deprecated code (after confirming no usage)

---

## Key Principles

1. **No Unnecessary Folders**: Only create folders when we have actual code to put in them
2. **Backward Compatibility**: Keep old imports working during migration
3. **Test-Driven**: Run full test suite after each major change
4. **Incremental**: Move one module at a time, test, commit
5. **Extensibility**: New structure makes adding solvers/lessons easier

---

## Benefits of New Structure

### Current Problems:
- OCR, parsing, and normalization mixed in `app/core/vision/` and `app/core/khmer/`
- Monolithic `solver.py` makes adding new problem types hard
- Classification logic scattered across multiple files
- No clear place for structured mathematical knowledge

### After Refactoring:
- ✅ Clear separation: OCR → Parser → Classifier → Solver → Reasoning → Verification
- ✅ Easy to add new solvers: just create `app/solvers/[domain]/new_solver.py`
- ✅ Scalable for knowledge base: `app/knowledge/` ready for lessons
- ✅ Better testing: can test each layer independently
- ✅ Cleaner dependencies: each module has clear inputs/outputs

---

## Next Steps

1. **Review this plan** - Confirm the mapping makes sense
2. **Start Phase 1** - Create new directory structure
3. **Migrate incrementally** - One module at a time
4. **Test continuously** - Ensure 130+ tests keep passing
5. **Document** - Update README with new architecture

Would you like me to proceed with Phase 1?
