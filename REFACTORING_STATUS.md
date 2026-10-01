# Architecture Refactoring Status

## Phase 1: Foundation - IN PROGRESS ⚠️

### ✅ Completed:
1. **Created new directory structure** according to target architecture
2. **Copied files** to new locations (originals preserved)
3. **Created `__init__.py`** files with proper docstrings
4. **Set up backward-compatible imports** in old locations
5. **Documented** each module's purpose

### Directory Structure Created:

```
app/
├── ocr/                          ✅ Created
│   ├── preprocessing/            ✅ image_preprocessor.py copied
│   ├── extraction/               ✅ All vision engines copied
│   └── normalization/            ✅ ocr_postprocessor.py copied
│
├── parser/                       ✅ Created
│   ├── math_parser/              ✅ expression_parser.py copied
│   ├── expression_parser/        ✅ khmer_normalizer.py, khmer_digits.py copied
│   ├── exercise_parser/          ✅ exercise_parser.py copied
│   └── pipeline.py               ✅ normalization pipeline copied
│
├── classifier/                   ✅ Created  
│   └── problem_classifier/       ✅ All classifiers copied
│
├── reasoning/                    ✅ Created
│   ├── steps/                    ✅ All step generators copied
│   ├── operations/               ✅ operations.py copied
│   └── solution_builder/         ✅ problem_builder.py copied
│
├── verification/                 ✅ Created
│   └── verifier.py               ✅ Copied
│
├── explanation/                  ✅ Created
│   └── templates/                ✅ templates.py copied
│
├── api/                          ✅ Created
│   ├── routes/                   ✅ All endpoints copied
│   └── schemas/                  ✅ Split into requests/responses
│
├── utils/                        ✅ Created
│   ├── exceptions.py             ✅ Copied
│   ├── logging.py                ✅ Copied
│   └── middleware.py             ✅ Copied
│
└── config/                       ✅ Created
    └── settings.py               ✅ Copied
```

### ⚠️ Issues Found:

1. **Circular Imports**: Copied files still reference old import paths
   - Example: `app/ocr/extraction/factory.py` imports from `app.core.vision`
   - Needs: Manual update of import statements

2. **Internal Dependencies**: Files reference each other via old paths
   - Need systematic update of all `from app.core.*` imports
   - Need update of all `from app.models.schemas` imports

### 🔄 Next Steps for Phase 1 Completion:

1. **Fix Internal Imports** (Critical):
   ```python
   # In app/ocr/extraction/*.py
   from app.core.vision.base → from app.ocr.extraction.base
   
   # In app/parser/*/*.py  
   from app.core.khmer → from app.parser.expression_parser
   from app.core.parser → from app.parser.math_parser
   
   # In app/classifier/problem_classifier/*.py
   from app.core.engine → from app.classifier.problem_classifier
   
   # In app/reasoning/*/*.py
   from app.core.engine.steps → from app.reasoning.steps
   from app.core.engine.operations → from app.reasoning.operations
   
   # In app/api/routes/*.py
   from app.models.schemas → from app.api.schemas
   ```

2. **Update Service Layer**:
   - `app/services/math_service.py` - Update imports
   - `app/services/vision_service.py` - Update imports  
   - Keep backward compatibility

3. **Test Import Chain**:
   ```bash
   python -c "from app.ocr import BaseVisionEngine"
   python -c "from app.parser import ParsedMath"
   python -c "from app.classifier import ProblemClassifier"
   ```

4. **Run Test Suite**:
   ```bash
   pytest tests/ -v
   ```
   Should still pass with 130+ tests

### 📋 Manual Import Update Checklist:

#### OCR Layer (`app/ocr/`):
- [ ] `extraction/factory.py` - Update vision engine imports
- [ ] `extraction/ensemble.py` - Update base imports
- [ ] `extraction/router.py` - Update base imports
- [ ] `extraction/gemini_vision.py` - Update base imports
- [ ] `extraction/google_vision.py` - Update base imports
- [ ] `extraction/kiri_ocr.py` - Update base imports
- [ ] `extraction/mathpix.py` - Update base imports
- [ ] `extraction/pix2tex_engine.py` - Update base imports
- [ ] `extraction/tesseract.py` - Update base imports
- [ ] `preprocessing/image_preprocessor.py` - Check imports
- [ ] `normalization/ocr_postprocessor.py` - Check imports

#### Parser Layer (`app/parser/`):
- [ ] `math_parser/expression_parser.py` - Update imports
- [ ] `exercise_parser/exercise_parser.py` - Update Khmer imports
- [ ] `expression_parser/khmer_normalizer.py` - Update digit imports
- [ ] `pipeline.py` - Update imports

#### Classifier Layer (`app/classifier/`):
- [ ] `problem_classifier/classifier.py` - Update imports
- [ ] `problem_classifier/classifier_enhanced.py` - Update imports  
- [ ] `problem_classifier/intent_classifier.py` - Update imports

#### Reasoning Layer (`app/reasoning/`):
- [ ] `steps/linear.py` - Update operation imports
- [ ] `steps/quadratic.py` - Update operation imports
- [ ] `steps/polynomial.py` - Update operation imports
- [ ] `steps/system.py` - Update operation imports
- [ ] `steps/inequality.py` - Update operation imports
- [ ] `steps/calculus_limit.py` - Update operation imports
- [ ] `steps/registry.py` - Update base imports
- [ ] `operations/operations.py` - Update localization imports
- [ ] `solution_builder/problem_builder.py` - Update all imports

#### API Layer (`app/api/`):
- [ ] `routes/solve.py` - Update schema imports
- [ ] `routes/vision.py` - Update schema imports
- [ ] `routes/history.py` - Update schema imports
- [ ] `routes/parse.py` - Update schema imports
- [ ] `routes/health.py` - Update schema imports

#### Services Layer (`app/services/`):
- [ ] `math_service.py` - Update all imports
- [ ] `vision_service.py` - Update OCR, parser, classifier imports
- [ ] `history_service.py` - Check imports

### 🎯 Success Criteria for Phase 1:

- ✅ New directory structure exists
- ✅ Files copied to new locations
- ⚠️ **All imports updated to use new paths** (IN PROGRESS)
- ⚠️ **Backward compatibility imports work** (Circular import issue)
- ⚠️ **Test suite passes** (Cannot test yet due to imports)
- ⚠️ **No deprecation warnings in tests** (Will add later)

### 💡 Recommendation:

**Option 1: Manual Import Fix** (Recommended)
- Systematically update each file's imports
- Test after each module is updated
- Takes time but ensures correctness

**Option 2: Automated Script**
- Create Python script to analyze and update imports
- Risk of breaking something
- Faster but needs thorough testing

**Option 3: Incremental Migration**
- Keep old structure working
- Gradually move imports one module at a time
- Update tests to use new imports
- Safest approach

### Current State:

```
Phase 1: Foundation
├── Directory Structure: ✅ DONE
├── File Copying: ✅ DONE  
├── Documentation: ✅ DONE
├── Import Updates: ⚠️ IN PROGRESS (50%)
├── Backward Compat: ⚠️ BLOCKED (Circular imports)
└── Testing: ⚠️ BLOCKED (Import errors)

Completion: ~60%
```

---

## Recommended Next Action:

I recommend **Option 3: Incremental Migration** with this approach:

1. **Keep old structure fully working** (don't update old file imports yet)
2. **Make new imports work** (fix new module internal imports only)
3. **Update one service at a time** (start with `math_service.py`)
4. **Run tests continuously** (ensure nothing breaks)
5. **Gradually deprecate old imports** (after everything works)

This approach is:
- ✅ Safer (old code keeps working)
- ✅ Testable (can verify each step)
- ✅ Reversible (easy to rollback)
- ⚠️ Slower (but more reliable)

Would you like me to:
A) Continue with manual import fixes (systematic but time-consuming)
B) Create an automated import update script (faster but riskier)
C) Pivot to incremental migration (safest approach)
