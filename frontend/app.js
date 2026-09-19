// -------------------------------------------------------------
// Khmer Math Lab — Client Application Logic (KaTeX & LaTeX First)
// -------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  // Elements: Tabs
  const tabTypingBtn = document.getElementById('tab-typing-btn');
  const tabVisionBtn = document.getElementById('tab-vision-btn');
  const tabTyping = document.getElementById('tab-typing');
  const tabVision = document.getElementById('tab-vision');

  // Elements: Typing Tab & Live Math Preview
  const questionInput = document.getElementById('question-input');
  const charCounter = document.getElementById('char-counter');
  const solveBtn = document.getElementById('solve-btn');
  const liveMathPreviewCard = document.getElementById('live-math-preview-card');
  const liveMathPreviewContent = document.getElementById('live-math-preview-content');

  // Elements: Vision Dropzone & Cropping
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const dropzoneEmpty = document.getElementById('dropzone-empty');
  const dropzonePreview = document.getElementById('dropzone-preview');
  const previewImage = document.getElementById('preview-image');
  const cropCanvas = document.getElementById('crop-canvas');
  const btnCropFormula = document.getElementById('btn-crop-formula');
  const btnResetCrop = document.getElementById('btn-reset-crop');
  const removeImageBtn = document.getElementById('remove-image-btn');
  const visionSolveBtn = document.getElementById('vision-solve-btn');

  // Elements: OCR LaTeX Card & Inline Editor
  const ocrLatexCard = document.getElementById('ocr-latex-card');
  const ocrLatexInput = document.getElementById('ocr-latex-input');
  const btnCopyLatex = document.getElementById('btn-copy-latex');
  const btnSolveEditedLatex = document.getElementById('btn-solve-edited-latex');

  // Elements: Solution Section
  const solutionEmpty = document.getElementById('solution-empty');
  const solutionLoading = document.getElementById('solution-loading');
  const solutionError = document.getElementById('solution-error');
  const errorMessage = document.getElementById('error-message');
  const errorActions = document.getElementById('error-actions');
  const btnErrorSwitchManual = document.getElementById('btn-error-switch-manual');
  const solutionContent = document.getElementById('solution-content');

  let pendingFallbackMath = '\\lim_{x \\to 0} \\frac{\\sin^2 x}{1 - \\cos^4 x}';

  const badgeProblemType = document.getElementById('badge-problem-type');
  const badgeVerified = document.getElementById('badge-verified');
  const heroVar = document.getElementById('hero-var');
  const heroAnswer = document.getElementById('hero-answer');
  const stepsList = document.getElementById('steps-list');

  // OCR Info Banner elements
  const ocrInfoBanner = document.getElementById('ocr-info-banner');
  const ocrDetectedText = document.getElementById('ocr-detected-text');
  const ocrExerciseHeaderRow = document.getElementById('ocr-exercise-header-row');
  const ocrExerciseBadge = document.getElementById('ocr-exercise-badge');
  const ocrInstructionBadge = document.getElementById('ocr-instruction-badge');
  const ocrCleanedRow = document.getElementById('ocr-cleaned-row');
  const ocrCleanedText = document.getElementById('ocr-cleaned-text');
  const ocrConfFill = document.getElementById('ocr-conf-fill');
  const ocrConfVal = document.getElementById('ocr-conf-val');

  // History elements
  const historyToggleBtn = document.getElementById('history-toggle-btn');
  const historyDrawer = document.getElementById('history-drawer');
  const closeHistoryBtn = document.getElementById('close-history-btn');
  const historyList = document.getElementById('history-list');
  const historyEmpty = document.getElementById('history-empty');
  const historyCount = document.getElementById('history-count');
  const clearHistoryBtn = document.getElementById('clear-history-btn');
  const apiStatus = document.getElementById('api-status');

  // State: Images & Crop
  let originalImageFile = null;
  let originalDataUrl = null;
  let currentImageFile = null;
  let cropRect = null; // { x, y, w, h }
  let isDraggingCrop = false;
  let cropStartX = 0;
  let cropStartY = 0;

  // ---------------- KaTeX Rendering Helpers ----------------
  function renderKaTeX(element, latexStr, displayMode = false) {
    if (!element || latexStr === undefined || latexStr === null) return;
    const str = String(latexStr).trim();
    if (!str) {
      element.innerHTML = '';
      return;
    }

    if (window.katex) {
      try {
        let clean = str;
        if (clean.startsWith('$$') && clean.endsWith('$$')) {
          clean = clean.slice(2, -2).trim();
        } else if (clean.startsWith('$') && clean.endsWith('$')) {
          clean = clean.slice(1, -1).trim();
        }
        window.katex.render(clean, element, {
          throwOnError: false,
          displayMode: displayMode,
          trust: true,
        });
        return;
      } catch (e) {
        console.warn('KaTeX rendering error:', e);
      }
    }
    element.textContent = str;
  }

  function renderMathIn(container) {
    if (!container || !window.renderMathInElement) return;
    try {
      window.renderMathInElement(container, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true },
        ],
        throwOnError: false,
      });
    } catch (e) {
      console.warn('renderMathInElement error:', e);
    }
  }

  // ---------------- Health Check ----------------
  async function checkHealth() {
    try {
      const res = await fetch('/api/v1/health');
      if (res.ok) {
        apiStatus.innerHTML = `
          <span class="status-dot"></span>
          <span class="status-text">API Live (v0.1.0)</span>
        `;
      }
    } catch {
      apiStatus.innerHTML = `
        <span class="status-dot" style="background:#f43f5e;box-shadow:0 0 8px #f43f5e"></span>
        <span class="status-text" style="color:#fda4af">API Offline</span>
      `;
    }
  }
  checkHealth();

  // ---------------- Tab Switching ----------------
  tabTypingBtn.addEventListener('click', () => {
    tabTypingBtn.classList.add('active');
    tabVisionBtn.classList.remove('active');
    tabTyping.classList.add('active');
    tabVision.classList.remove('active');
  });

  tabVisionBtn.addEventListener('click', () => {
    tabVisionBtn.classList.add('active');
    tabTypingBtn.classList.remove('active');
    tabVision.classList.add('active');
    tabTyping.classList.remove('active');
    setTimeout(syncCropCanvas, 150);
  });

  // ---------------- Live Math Preview & Typing ----------------
  function updateLivePreview() {
    charCounter.textContent = questionInput.value.length;
    const raw = questionInput.value.trim();
    if (!raw) {
      if (liveMathPreviewCard) liveMathPreviewCard.classList.add('hidden');
      return;
    }

    // Detect if input has LaTeX or mathematical symbols
    const hasMath = /[\\^_{}]|lim|frac|sqrt|sin|cos|tan|\d+\s*[\+\-\*\/=]|\d+[a-zA-Z]/i.test(raw);
    if (!hasMath) {
      if (liveMathPreviewCard) liveMathPreviewCard.classList.add('hidden');
      return;
    }

    // Clean instructions and sub-problem labels for KaTeX math preview
    let formula = raw;
    formula = formula.replace(/^(?:លំហាត់ទី|លំហាត់|សំណួរទី|សំណួរ|វិញ្ញាសាទី|វិញ្ញាសា|ឧទាហរណ៍ទី|ឧទាហរណ៍|Exercise|Problem|Task|Question|Example|Ex|Q)\s*[:.-]?\s*[0-9\u17e0-\u17e9]*[:.-]?\s*/i, '');
    formula = formula.replace(/^(?:(?:ចូរ)?(?:គណនា|រក|ដោះស្រាយ)(?:នូវ)?(?:តម្លៃ)?(?:នៃ)?លីមីត(?:នៃអនុគមន៍)?(?:ខាងក្រោម)?(?:នេះ)?(?:ទាំងនេះ)?(?:ដូចខាងក្រោម)?|ដោះស្រាយសមីការ(?:ខាងក្រោម)?|ចូរដោះស្រាយសមីការ|ចូរដោះស្រាយ|ដោះស្រាយ|រកតម្លៃនៃ\s*[a-zA-Z]?|រកតម្លៃ\s*[a-zA-Z]?|រក\s*[a-zA-Z]?|ចូររកតម្លៃ|គណនាតម្លៃនៃ\s*[a-zA-Z]?|គណនាតម្លៃ|គណនាកន្សោម(?:ខាងក្រោម)?|គណនាប្រភាគ|គណនា|ចូរគណនា|ធ្វើឲ្យសាមញ្ញ(?:នូវកន្សោម)?(?:ខាងក្រោម)?|ចូរធ្វើឲ្យសាមញ្ញ|បង្រួមកន្សោម(?:ខាងក្រោម)?|Find\s+(?:the\s+)?value\s+of\s+[a-zA-Z]?|Solve\s+for\s+[a-zA-Z]?|Solve\s+the\s+equation|Find\s+[a-zA-Z]|(?:Find|Calculate|Evaluate|Compute|Solve)\s+(?:each\s+of\s+)?(?:the\s+)?(?:following\s+)?limits?(?:\s+of)?(?:\s+the\s+following)?|Calculate|Evaluate|Simplify|Compute)[:៖\s]*/i, '');
    // Clean sub-item label like 'ខ.', 'ក.', '1.', '2.', 'a.', '(a)', '(1)', '\mathcal{Q}.'
    formula = formula.replace(/^(?:\([a-zA-Z0-9\u1780-\u17a2]{1,2}\)[\.៖:]?|(?:\\(?:mathcal|mathbf|mathrm|text)\{[a-zA-Z0-9\u1780-\u17a2]+\}|[ក-អ]|[a-zA-Z]|[0-9]{1,2}|[\u17e0-\u17e9]{1,2})[\)\.៖:](?!\d))\s*/i, '');

    // Format ASCII limits and sqrt for smooth KaTeX display
    formula = formula.replace(/(?:\\)?sqrt\(([^)]+)\)/gi, '\\sqrt{$1}');
    formula = formula.replace(/(?:\\\\|\\|\/)*lim(?:it)?\s*(?:_\{?|\s+)\s*([a-zA-Z])\s*(?:->|\\\\rightarrow|\\rightarrow|\\\\to|\\to|\bto\b)\s*([0-9+\-a-zA-Z]+|\\[a-zA-Z]+)\}?/gi, '\\lim_{$1 \\to $2} ');

    formula = formula.trim();
    if (!formula) {
      if (liveMathPreviewCard) liveMathPreviewCard.classList.add('hidden');
      return;
    }

    if (liveMathPreviewCard && liveMathPreviewContent) {
      liveMathPreviewCard.classList.remove('hidden');
      renderKaTeX(liveMathPreviewContent, formula, true);
    }
  }

  questionInput.addEventListener('input', updateLivePreview);

  // Shortcut Chips Insertion
  document.querySelectorAll('.btn-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const insertText = chip.getAttribute('data-insert');
      if (!insertText) return;
      insertAtCursor(questionInput, insertText);
      updateLivePreview();
      questionInput.focus();
    });
  });

  function insertAtCursor(input, textToInsert) {
    const start = input.selectionStart || 0;
    const end = input.selectionEnd || 0;
    const text = input.value;
    input.value = text.substring(0, start) + textToInsert + text.substring(end);
    input.selectionStart = input.selectionEnd = start + textToInsert.length;
  }

  // Example Presets
  document.querySelectorAll('.preset-pill').forEach((pill) => {
    pill.addEventListener('click', () => {
      const exampleText = pill.getAttribute('data-example');
      questionInput.value = exampleText;
      updateLivePreview();
      solveManualMath();
    });
  });

  // ---------------- Solve Manual Math ----------------
  solveBtn.addEventListener('click', solveManualMath);
  questionInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      solveManualMath();
    }
  });

  async function solveManualMath() {
    const question = questionInput.value.trim();
    if (!question) {
      showError('សូមបញ្ចូលលំហាត់គណិតវិទ្យា (Please enter a math expression).');
      return;
    }

    showLoading();

    try {
      const response = await fetch('/api/v1/math/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: 'km', question: question }),
      });

      const result = await response.json();

      if (result.success && result.data) {
        renderSolution(result.data, false);
        loadHistory();
      } else {
        showError(result.error || 'មិនអាចដោះស្រាយលំហាត់នេះបានទេ');
      }
    } catch (err) {
      showError('កំហុសក្នុងការតភ្ជាប់ទៅកាន់ Server: ' + err.message);
    }
  }

  // ---------------- File Dropzone & Image Handling ----------------
  dropzone.addEventListener('click', (e) => {
    if (e.target !== removeImageBtn && e.target !== btnCropFormula && e.target !== btnResetCrop) {
      fileInput.click();
    }
  });

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      handleImageSelected(fileInput.files[0]);
    }
  });

  function handleImageSelected(file) {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file (PNG, JPG, WebP)');
      return;
    }

    originalImageFile = file;
    currentImageFile = file;
    cropRect = null;
    if (btnResetCrop) btnResetCrop.classList.add('hidden');
    if (ocrLatexCard) ocrLatexCard.classList.add('hidden');

    const reader = new FileReader();
    reader.onload = (e) => {
      originalDataUrl = e.target.result;
      previewImage.src = originalDataUrl;
      dropzoneEmpty.classList.add('hidden');
      dropzonePreview.classList.remove('hidden');
      visionSolveBtn.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  previewImage.addEventListener('load', () => {
    syncCropCanvas();
  });

  window.addEventListener('resize', () => {
    syncCropCanvas();
  });

  function syncCropCanvas() {
    if (!previewImage.complete || !previewImage.naturalWidth || !cropCanvas) return;
    cropCanvas.width = previewImage.clientWidth;
    cropCanvas.height = previewImage.clientHeight;
    drawCropOverlay();
  }

  // Crop Drag Events
  if (cropCanvas) {
    cropCanvas.addEventListener('mousedown', (e) => {
      const rect = cropCanvas.getBoundingClientRect();
      cropStartX = e.clientX - rect.left;
      cropStartY = e.clientY - rect.top;
      isDraggingCrop = true;
      cropRect = null;
    });

    cropCanvas.addEventListener('mousemove', (e) => {
      if (!isDraggingCrop) return;
      const rect = cropCanvas.getBoundingClientRect();
      const currX = e.clientX - rect.left;
      const currY = e.clientY - rect.top;
      const x = Math.min(cropStartX, currX);
      const y = Math.min(cropStartY, currY);
      const w = Math.abs(currX - cropStartX);
      const h = Math.abs(currY - cropStartY);
      cropRect = { x, y, w, h };
      drawCropOverlay();
    });

    window.addEventListener('mouseup', () => {
      if (isDraggingCrop) {
        isDraggingCrop = false;
        if (cropRect && (cropRect.w < 15 || cropRect.h < 15)) {
          cropRect = null;
          drawCropOverlay();
        }
      }
    });
  }

  function drawCropOverlay() {
    if (!cropCanvas) return;
    const ctx = cropCanvas.getContext('2d');
    ctx.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
    if (!cropRect || cropRect.w === 0 || cropRect.h === 0) return;

    // Dim mask over image
    ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
    ctx.fillRect(0, 0, cropCanvas.width, cropCanvas.height);

    // Clear selected rectangle
    ctx.clearRect(cropRect.x, cropRect.y, cropRect.w, cropRect.h);

    // Cyan glowing border
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 2]);
    ctx.strokeRect(cropRect.x, cropRect.y, cropRect.w, cropRect.h);

    // Handles
    ctx.setLineDash([]);
    ctx.fillStyle = '#38bdf8';
    const hSize = 6;
    const corners = [
      [cropRect.x, cropRect.y],
      [cropRect.x + cropRect.w, cropRect.y],
      [cropRect.x, cropRect.y + cropRect.h],
      [cropRect.x + cropRect.w, cropRect.y + cropRect.h],
    ];
    corners.forEach(([cx, cy]) => {
      ctx.fillRect(cx - hSize / 2, cy - hSize / 2, hSize, hSize);
    });
  }

  // Crop Button
  if (btnCropFormula) {
    btnCropFormula.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!cropRect || cropRect.w < 15 || cropRect.h < 15) {
        alert('សូមគូសប្រអប់ជុំវិញរូបមន្តដែលអ្នកចង់កាត់ជាមុនសិន (Drag a box on the image to crop first).');
        return;
      }

      const scaleX = previewImage.naturalWidth / previewImage.clientWidth;
      const scaleY = previewImage.naturalHeight / previewImage.clientHeight;

      const sx = Math.round(cropRect.x * scaleX);
      const sy = Math.round(cropRect.y * scaleY);
      const sw = Math.round(cropRect.w * scaleX);
      const sh = Math.round(cropRect.h * scaleY);

      const offscreen = document.createElement('canvas');
      offscreen.width = sw;
      offscreen.height = sh;
      const ctx = offscreen.getContext('2d');
      ctx.drawImage(previewImage, sx, sy, sw, sh, 0, 0, sw, sh);

      offscreen.toBlob((blob) => {
        if (!blob) return;
        currentImageFile = new File([blob], 'cropped_formula.png', { type: 'image/png' });
        previewImage.src = URL.createObjectURL(blob);
        if (btnResetCrop) btnResetCrop.classList.remove('hidden');
        cropRect = null;
        const cctx = cropCanvas.getContext('2d');
        cctx.clearRect(0, 0, cropCanvas.width, cropCanvas.height);
      }, 'image/png');
    });
  }

  // Reset Crop Button
  if (btnResetCrop) {
    btnResetCrop.addEventListener('click', (e) => {
      e.stopPropagation();
      if (originalDataUrl && originalImageFile) {
        currentImageFile = originalImageFile;
        previewImage.src = originalDataUrl;
        btnResetCrop.classList.add('hidden');
        cropRect = null;
        setTimeout(syncCropCanvas, 100);
      }
    });
  }

  // Remove Image Button
  removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    originalImageFile = null;
    currentImageFile = null;
    originalDataUrl = null;
    cropRect = null;
    fileInput.value = '';
    previewImage.src = '';
    dropzoneEmpty.classList.remove('hidden');
    dropzonePreview.classList.add('hidden');
    visionSolveBtn.disabled = true;
    if (btnResetCrop) btnResetCrop.classList.add('hidden');
    if (ocrLatexCard) ocrLatexCard.classList.add('hidden');
  });

  // Sample Image Shortcuts
  document.querySelectorAll('.btn-sample').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const samplePath = btn.getAttribute('data-sample');
      try {
        const res = await fetch(samplePath);
        const blob = await res.blob();
        const file = new File([blob], 'sample.png', { type: blob.type || 'image/png' });
        handleImageSelected(file);
      } catch (err) {
        console.error('Failed to load sample image:', err);
      }
    });
  });

  // ---------------- Solve Image Vision ----------------
  visionSolveBtn.addEventListener('click', solveVisionMath);

  async function solveVisionMath() {
    if (!currentImageFile) return;

    showLoading();

    const formData = new FormData();
    formData.append('image', currentImageFile);

    try {
      const response = await fetch('/api/v1/math/vision', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success && result.data) {
        renderSolution(result.data, true);
        loadHistory();
      } else {
        let errorMsg = result.error || 'No mathematical text recognized in image.';
        let isStub = errorMsg.includes('stub') || errorMsg.includes('not implemented yet');
        if (isStub) {
          errorMsg = `⚠️ ប្រព័ន្ធ OCR (Math Vision) កំពុងស្ថិតក្នុងដំណាក់កាលទាញយកកញ្ចប់ម៉ូឌែលនៅក្នុង Background។\n\n💡 ប៉ុន្តែប្រព័ន្ធគណិតវិទ្យា (Math Engine) អាចដោះស្រាយលំហាត់នេះបានភ្លាមៗ!`;
          pendingFallbackMath = (result.data && result.data.ocr_detected_text) ? result.data.ocr_detected_text : '4/3 + 2/4';
          showError(errorMsg, true);
        } else {
          showError(errorMsg, false);
        }
      }
    } catch (err) {
      showError('កំហុសក្នុងការតភ្ជាប់ OCR: ' + err.message, false);
    }
  }

  // ---------------- OCR LaTeX Box Actions ----------------
  if (btnCopyLatex) {
    btnCopyLatex.addEventListener('click', () => {
      if (!ocrLatexInput || !ocrLatexInput.value) return;
      navigator.clipboard.writeText(ocrLatexInput.value).then(() => {
        const orig = btnCopyLatex.textContent;
        btnCopyLatex.textContent = '✅ បានចម្លង!';
        setTimeout(() => {
          btnCopyLatex.textContent = orig;
        }, 1500);
      });
    });
  }

  if (btnSolveEditedLatex) {
    btnSolveEditedLatex.addEventListener('click', async () => {
      if (!ocrLatexInput || !ocrLatexInput.value.trim()) return;
      const editedVal = ocrLatexInput.value.trim();
      questionInput.value = editedVal;
      updateLivePreview();
      await solveManualMath();
    });
  }

  // Action button to switch directly to manual solve
  if (btnErrorSwitchManual) {
    btnErrorSwitchManual.addEventListener('click', () => {
      tabTypingBtn.click();
      if (pendingFallbackMath) {
        questionInput.value = pendingFallbackMath;
        updateLivePreview();
      }
      solveManualMath();
    });
  }

  // ---------------- Render Solution States ----------------
  function showLoading() {
    solutionEmpty.classList.add('hidden');
    solutionError.classList.add('hidden');
    solutionContent.classList.add('hidden');
    if (errorActions) errorActions.classList.add('hidden');
    solutionLoading.classList.remove('hidden');
  }

  function showError(msg, showAction = false) {
    solutionEmpty.classList.add('hidden');
    solutionLoading.classList.add('hidden');
    solutionContent.classList.add('hidden');
    solutionError.classList.remove('hidden');
    errorMessage.textContent = msg;

    if (errorActions) {
      if (showAction) {
        errorActions.classList.remove('hidden');
      } else {
        errorActions.classList.add('hidden');
      }
    }
  }

  function renderSolution(data, isFromVision) {
    solutionEmpty.classList.add('hidden');
    solutionLoading.classList.add('hidden');
    solutionError.classList.add('hidden');
    solutionContent.classList.remove('hidden');

    // Format Problem Type label
    const typeLabel = (data.problem_type || 'math_problem')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase());
    badgeProblemType.textContent = typeLabel;

    // Verified badge
    if (data.is_verified) {
      badgeVerified.className = 'badge badge-success';
      badgeVerified.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <span>ផ្ទៀងផ្ទាត់ត្រឹមត្រូវ (Verified)</span>
      `;
    } else {
      badgeVerified.className = 'badge badge-primary';
      badgeVerified.textContent = 'ដំណោះស្រាយ (Solution)';
    }

    // Hero variable and answer (Rendered with KaTeX)
    if (data.variable) {
      heroVar.textContent = `${data.variable} = `;
    } else {
      heroVar.textContent = '';
    }
    heroAnswer.innerHTML = '';
    renderKaTeX(heroAnswer, String(data.answer ?? 'N/A'), false);

    // OCR Info Banner & LaTeX Card
    if (isFromVision && (data.ocr_detected_text || data.cleaned_math_expression)) {
      const bestLatex = data.cleaned_math_expression || data.ocr_detected_text;
      ocrInfoBanner.classList.remove('hidden');
      ocrDetectedText.textContent = data.ocr_detected_text || '';
      const conf = Math.round((data.ocr_confidence || 0.95) * 100);
      ocrConfVal.textContent = `${conf}%`;
      ocrConfFill.style.width = `${conf}%`;

      // Populate editable LaTeX card
      if (ocrLatexCard && ocrLatexInput) {
        ocrLatexCard.classList.remove('hidden');
        ocrLatexInput.value = bestLatex;
      }

      // Exercise title and instruction badges
      if (data.exercise_title || data.instruction) {
        ocrExerciseHeaderRow.classList.remove('hidden');
        if (data.exercise_title) {
          ocrExerciseBadge.textContent = data.exercise_title;
          ocrExerciseBadge.classList.remove('hidden');
        } else {
          ocrExerciseBadge.classList.add('hidden');
        }
        if (data.instruction) {
          ocrInstructionBadge.textContent = data.instruction;
          ocrInstructionBadge.classList.remove('hidden');
        } else {
          ocrInstructionBadge.classList.add('hidden');
        }
      } else {
        ocrExerciseHeaderRow.classList.add('hidden');
      }

      // Extracted math expression display
      if (data.cleaned_math_expression && data.cleaned_math_expression !== data.ocr_detected_text) {
        ocrCleanedRow.classList.remove('hidden');
        ocrCleanedText.textContent = data.cleaned_math_expression;
      } else {
        ocrCleanedRow.classList.add('hidden');
      }
    } else {
      ocrInfoBanner.classList.add('hidden');
    }

    // Steps list with KaTeX rendering
    stepsList.innerHTML = '';
    if (data.steps && data.steps.length > 0) {
      data.steps.forEach((step) => {
        const stepCard = document.createElement('div');
        stepCard.className = 'step-card';

        const stepNumber = document.createElement('div');
        stepNumber.className = 'step-number';
        stepNumber.textContent = step.order || '•';

        const stepContent = document.createElement('div');
        stepContent.className = 'step-content';

        const titleKm = document.createElement('div');
        titleKm.className = 'step-title-km';
        titleKm.textContent = step.description_km || '';
        stepContent.appendChild(titleKm);

        if (step.description_en) {
          const titleEn = document.createElement('div');
          titleEn.className = 'step-title-en';
          titleEn.textContent = step.description_en;
          stepContent.appendChild(titleEn);
        }

        if (step.expression) {
          const exprBox = document.createElement('div');
          exprBox.className = 'step-expression';
          renderKaTeX(exprBox, step.expression, true);
          stepContent.appendChild(exprBox);
        }

        renderMathIn(stepContent);

        stepCard.appendChild(stepNumber);
        stepCard.appendChild(stepContent);
        stepsList.appendChild(stepCard);
      });
    } else {
      stepsList.innerHTML = `
        <div class="step-card">
          <div class="step-content">
            <div class="step-title-km">ចម្លើយគណនាដោយ SymPy ៖ ${escapeHtml(String(data.answer))}</div>
          </div>
        </div>
      `;
    }
  }

  // ---------------- History Drawer ----------------
  historyToggleBtn.addEventListener('click', () => {
    historyDrawer.classList.toggle('hidden');
    if (!historyDrawer.classList.contains('hidden')) {
      loadHistory();
    }
  });

  closeHistoryBtn.addEventListener('click', () => {
    historyDrawer.classList.add('hidden');
  });

  async function loadHistory() {
    try {
      const res = await fetch('/api/v1/math/history?limit=30');
      const json = await res.json();

      if (json.success && json.data && json.data.items) {
        const items = json.data.items;
        historyCount.textContent = `${items.length} problems`;

        if (items.length === 0) {
          historyEmpty.classList.remove('hidden');
          historyList.innerHTML = '';
          return;
        }

        historyEmpty.classList.add('hidden');
        historyList.innerHTML = '';

        items.forEach((item) => {
          const card = document.createElement('div');
          card.className = 'history-item';

          const timeFormatted = new Date(item.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          });

          card.innerHTML = `
            <div class="history-meta">
              <span class="history-type">${item.problem_type.replace(/_/g, ' ')}</span>
              <span class="history-time">${timeFormatted}</span>
            </div>
            <div class="history-q">${escapeHtml(item.question)}</div>
            <div class="history-ans">Answer: ${escapeHtml(item.answer || '')}</div>
          `;

          card.addEventListener('click', () => {
            renderSolution(
              {
                problem_type: item.problem_type,
                original_question: item.question,
                answer: item.answer,
                is_verified: item.is_verified,
                steps: item.steps || [],
              },
              false
            );
            questionInput.value = item.question;
            updateLivePreview();
            historyDrawer.classList.add('hidden');
          });

          historyList.appendChild(card);
        });
      }
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  }

  clearHistoryBtn.addEventListener('click', async () => {
    if (confirm('តើអ្នកពិតជាចង់លុបប្រវត្តិទាំងអស់មែនទេ? (Clear all history?)')) {
      try {
        await fetch('/api/v1/math/history', { method: 'DELETE' });
        loadHistory();
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  });

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
});
