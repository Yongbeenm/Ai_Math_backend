# Math Vision OCR Setup Guide

This guide explains how to set up and configure different OCR providers for the Math Vision feature.

## Overview

The Khmer Math Lab backend supports multiple OCR providers through a pluggable architecture. You can easily switch between providers by setting an environment variable.

## Available Providers

| Provider | Cost | Accuracy | Khmer Support | Math Support | Setup Difficulty |
|----------|------|----------|---------------|--------------|------------------|
| **Stub** (default) | Free | N/A | N/A | N/A | None |
| **Kiri OCR** (`kiri`, `khmer_ocr`) | Free (Offline) | High | 🇰🇭 Native/Excellent | ✅ Good | Easy (`pip install`) |
| **Tesseract** (`tesseract`) | Free (Offline) | High (with CLAHE) | ✅ Good | ✅ Good (with Sanitizer) | Medium (needs brew) |
| **Gemini Vision** (`gemini`) | Free tier + paid | Superior (SOTA) | 🇰🇭 Native/Exceptional | 🧮 SOTA | Easy (`GEMINI_API_KEY`) |
| **Google Vision** (`google`) | Free tier + paid | High | ✅ Excellent | ⚠️ Good | Medium (GCP account) |
| **Mathpix** (`mathpix`) | Paid | Excellent | ✅ Good | ✅ Excellent | Easy (API keys) |

## Quick Start

The easiest way to get started with **native Khmer OCR** is with **Kiri OCR** (Python library, free, offline):

```bash
# 1. Install Kiri OCR
pip install kiri-ocr

# 2. Set environment variable in .env
VISION_PROVIDER=kiri  # or khmer_ocr

# 3. Test it via API
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@math_problem.jpg"
```

---

## Provider Setup Details

### 1. Stub (Default - No OCR)

**When to use:** API development, testing mobile app integration without OCR.

**Setup:**
```bash
export VISION_PROVIDER=stub
```

No additional configuration needed. Returns "not implemented" message.

---

### 2. Kiri OCR (Recommended for Native Khmer OCR, Free & Offline)

**When to use:** Local, high-accuracy Khmer & English OCR without cloud API fees or system binary installations.

**Pros:**
- ✅ Native Khmer script recognition (consonants, subscripts, vowels, numerals)
- ✅ Free, open-source, runs offline
- ✅ Transformer architecture with CTC + attention decoder
- ✅ Pure Python package (`pip install kiri-ocr`)
- ✅ No cloud API account or internet required during inference

**Cons:**
- ⚠️ Model weights (~150MB) downloaded on first execution
- ⚠️ Uses PyTorch for inference

**Setup:**
```bash
pip install kiri-ocr
export VISION_PROVIDER=kiri
```

---

### 3. Gemini Vision (Recommended for Complex Multimodal Worksheets)

**When to use:** Production, state-of-the-art accuracy on handwritten math, complex textbook worksheets, and mixed Khmer/English exercises.

**Pros:**
- ✅ State-of-the-art multimodal understanding for Khmer script and handwriting
- ✅ Automatically isolates exercise titles ("លំហាត់ទី 1"), instructions, and math expressions
- ✅ Understands complex mathematical formulas, fractions, radicals, and systems
- ✅ Fast response times with `gemini-2.5-flash`

**Cons:**
- ⚠️ Requires internet connection and `GEMINI_API_KEY` (free tier available at AI Studio)

**Setup:**
1. Get an API key from [Google AI Studio](https://aistudio.google.com/)
2. In `.env`:
```bash
VISION_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
```

---

### 4. Tesseract (Traditional Open-Source OCR)

**When to use:** Free development, offline usage, privacy-sensitive applications.

**Pros:**
- ✅ Free and open-source
- ✅ Works offline
- ✅ Supports Khmer language
- ✅ No API limits

**Cons:**
- ⚠️ Less accurate for handwriting
- ⚠️ Struggles with complex math notation

**Setup:**

#### Step 1: Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-khm
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

#### Step 2: Install Python Libraries
```bash
pip install pytesseract pillow
```

#### Step 3: Verify Installation
```bash
tesseract --version
tesseract --list-langs  # Should show 'khm' if Khmer is installed
```

#### Step 4: Configure
```bash
# Add to .env file
VISION_PROVIDER=tesseract
```

#### Step 5: (Optional) Install Khmer Language Data
If Khmer isn't in the `--list-langs` output:
```bash
# Download khm.traineddata from:
# https://github.com/tesseract-ocr/tessdata/raw/main/khm.traineddata

# Copy to Tesseract data directory:
# macOS: /usr/local/share/tessdata/
# Linux: /usr/share/tesseract-ocr/4.00/tessdata/
```

---

### 4. Google Cloud Vision (Recommended for Production)

**When to use:** Production use with good Khmer support, affordable pricing.

**Pros:**
- ✅ Excellent Khmer recognition
- ✅ Good for printed/typed math
- ✅ Affordable ($1.50 per 1000 images after free tier)
- ✅ Free tier: 1000 requests/month

**Cons:**
- ⚠️ Less specialized for handwritten math notation
- ⚠️ Requires Google Cloud account

**Setup:**

#### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Cloud Vision API:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

#### Step 2: Create Service Account
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: "khmer-math-ocr"
4. Grant role: "Cloud Vision" → "Cloud Vision User"
5. Click "Create Key" → JSON
6. Download the JSON file

#### Step 3: Install Python Library
```bash
pip install google-cloud-vision
```

#### Step 4: Configure
```bash
# Add to .env file
VISION_PROVIDER=google
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Security Note:** Never commit the service account JSON file to git!

---

### 5. Mathpix (Best for Complex Math)

**When to use:** Handwritten complex equations, matrices, advanced notation.

**Pros:**
- ✅ Best-in-class for mathematical notation
- ✅ Handles complex equations, matrices, calculus
- ✅ Fast and reliable

**Cons:**
- ⚠️ Paid service (free tier: 1000 requests/month)
- ⚠️ Most expensive option

**Setup:**

#### Step 1: Sign Up
1. Go to https://mathpix.com/
2. Sign up for an account
3. Choose a plan:
   - **Free Tier:** 1000 requests/month
   - **Paid Plans:** Starting at $4.99/month

#### Step 2: Get API Credentials
1. Go to https://accounts.mathpix.com/
2. Navigate to "OCR API"
3. Copy your `APP_ID` and `APP_KEY`

#### Step 3: Install Python Library
```bash
pip install requests
```

#### Step 4: Configure
```bash
# Add to .env file
VISION_PROVIDER=mathpix
MATHPIX_APP_ID=your_app_id_here
MATHPIX_APP_KEY=your_app_key_here
```

---

## Testing Your Setup

### Check Available Providers

```python
from app.core.vision.factory import list_available_providers

providers = list_available_providers()
for name, available in providers.items():
    status = "✓ Available" if available else "✗ Not Available"
    print(f"{name}: {status}")
```

### Test OCR with Sample Image

```bash
# Test the /math/vision endpoint
curl -X POST http://localhost:8000/api/v1/math/vision \
  -F "image=@test_math.jpg" \
  -F "language=km"
```

### Python Test Script

```python
from app.core.vision.factory import create_vision_engine

# Create engine
engine = create_vision_engine("tesseract")  # or "google", "mathpix"

# Read test image
with open("test_math.jpg", "rb") as f:
    image_bytes = f.read()

# Detect
result = engine.detect(image_bytes)

print(f"Detected: {result.detected_text}")
print(f"Confidence: {result.confidence:.2%}")
if result.error_message:
    print(f"Error: {result.error_message}")
```

---

## Choosing the Right Provider

### For Development/Testing
**Use: Tesseract**
- Free, offline, good for testing the integration

### For Production (Budget-Friendly)
**Use: Google Cloud Vision**
- Good balance of cost, Khmer support, and accuracy

### For Production (Best Math Accuracy)
**Use: Mathpix**
- Best for complex handwritten equations
- More expensive but worth it for advanced math

### Hybrid Approach (Recommended)
Use different providers for different scenarios:
```python
# In your code, you can dynamically choose:
if is_complex_math:
    engine = create_vision_engine("mathpix")
else:
    engine = create_vision_engine("google")
```

---

## Cost Comparison

| Provider | Free Tier | After Free Tier | Est. Cost for 10,000 images |
|----------|-----------|-----------------|------------------------------|
| Tesseract | Unlimited | N/A (free) | **$0** |
| Google Vision | 1,000/month | $1.50 per 1,000 | **$13.50** |
| Mathpix | 1,000/month | ~$0.04 per image | **$360** |

---

## Troubleshooting

### Tesseract: "TesseractNotFoundError"
```bash
# Verify installation
which tesseract
tesseract --version

# macOS: Reinstall
brew reinstall tesseract

# Linux: Reinstall
sudo apt-get install --reinstall tesseract-ocr
```

### Tesseract: Khmer Not Detected
```bash
# Check available languages
tesseract --list-langs

# If 'khm' missing, install it:
# Ubuntu
sudo apt-get install tesseract-ocr-khm

# macOS
brew install tesseract-lang
```

### Google Vision: Authentication Error
```bash
# Verify credentials file exists
ls -la $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
python -c "from google.cloud import vision; client = vision.ImageAnnotatorClient(); print('✓ Auth works')"
```

### Mathpix: Invalid Credentials
```bash
# Verify environment variables are set
echo $MATHPIX_APP_ID
echo $MATHPIX_APP_KEY

# Test API connection
curl -X POST https://api.mathpix.com/v3/text \
  -H "app_id: $MATHPIX_APP_ID" \
  -H "app_key: $MATHPIX_APP_KEY" \
  -d '{"src": "data:image/jpeg;base64,..."}'
```

---

## Next Steps

1. Choose and set up an OCR provider (start with Tesseract)
2. Test with sample images containing Khmer math
3. Update `.env` with your chosen provider
4. Test the `/api/v1/math/vision` endpoint
5. Integrate with Flutter mobile app camera flow

For questions or issues, refer to the main README.md or the provider's documentation.
