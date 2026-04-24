/* ══════════════════════════════════════════════════════════════
   SafeView Frontend — app.js
   COMP 264 Cloud Machine Learning
══════════════════════════════════════════════════════════════ */

// ── Configuration ──────────────────────────────────────────
// When running locally with `chalice local`, the API is at:
const API_BASE = getApiBase();
const MAX_FILE_BYTES = 5 * 1024 * 1024;   // 5 MB
const ALLOWED_TYPES  = ["image/jpeg", "image/png"];
const RERUN_DEBOUNCE_MS = 600;

// ── State ───────────────────────────────────────────────────
let selectedFile    = null;   // File object
let imageDataURL    = null;   // base64 data URL for preview
let currentReport   = null;   // last full report from server
let rerunTimer      = null;   // debounce timer for threshold re-run

// ── DOM refs ────────────────────────────────────────────────
const dropZone       = document.getElementById("drop-zone");
const fileInput      = document.getElementById("file-input");
const previewThumb   = document.getElementById("preview-thumb");
const previewName    = document.getElementById("preview-name");
const previewSize    = document.getElementById("preview-size");
const analyzeBtn     = document.getElementById("analyze-btn");
const thresholdSlider= document.getElementById("threshold-slider");
const thresholdVal   = document.getElementById("threshold-val");
const statusText     = document.getElementById("status-text");
const spinner        = document.getElementById("spinner");
const errorBanner    = document.getElementById("error-banner");
const errorText      = document.getElementById("error-text");
const uploadPanel    = document.getElementById("upload-panel");
const resultsPanel   = document.getElementById("results-panel");
const rerunSlider    = document.getElementById("rerun-slider");
const rerunVal       = document.getElementById("rerun-val");

// ── Drag-and-drop setup ─────────────────────────────────────
dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelected(file);
});

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFileSelected(fileInput.files[0]);
});

// ── Threshold slider ────────────────────────────────────────
thresholdSlider.addEventListener("input", () => {
  thresholdVal.textContent = thresholdSlider.value + "%";
});

// ── File selection handler ──────────────────────────────────
/**
 * handleFileSelected
 * Validates the chosen file (client-side) and updates the drop-zone
 * preview. Mirrors the server-side validation in chalicelib/validator.py.
 *
 * @param {File} file - The chosen File object.
 */
function handleFileSelected(file) {
  dismissError();

  // Client-side type check
  if (!ALLOWED_TYPES.includes(file.type)) {
    showError(`File type '${file.type}' is not supported. Only JPEG and PNG files are accepted.`);
    return;
  }

  // Client-side size check
  if (file.size > MAX_FILE_BYTES) {
    const mb = (file.size / 1024 / 1024).toFixed(1);
    showError(`File size ${mb} MB exceeds the 5 MB limit. Please upload a smaller image.`);
    return;
  }

  selectedFile = file;

  // Generate preview data URL
  const reader = new FileReader();
  reader.onload = e => {
    imageDataURL = e.target.result;
    previewThumb.src = imageDataURL;
    previewName.textContent = file.name;
    previewSize.textContent = formatBytes(file.size);

    dropZone.classList.add("has-file");
    document.getElementById("file-preview").classList.add("visible");
    analyzeBtn.disabled = false;
    setStatus("Image selected — adjust threshold and click Analyze");
  };
  reader.readAsDataURL(file);
}

// ── Main analysis flow ──────────────────────────────────────
/**
 * runAnalysis
 * Encodes the selected image as base64, sends POST /analyze, and
 * renders the moderation report. Implements UC-01.
 */
async function runAnalysis() {
  if (!selectedFile || !imageDataURL) return;

  const threshold = parseInt(thresholdSlider.value, 10);

  setBusy(true, "Uploading image to S3…");
  dismissError();

  try {
    // Strip the data URL prefix to get raw base64
    const base64 = imageDataURL.split(",")[1];

    setStatus("Analysing with AWS Rekognition + Comprehend…");

    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_data: base64,
        filename:   selectedFile.name,
        threshold:  threshold,
      }),
    });

    const data = await readApiJson(response);

    if (!response.ok || data.error) {
      showError(data.message || "Analysis failed. Please try again.");
      setBusy(false, "Analysis failed.");
      return;
    }

    currentReport = data;
    renderReport(data);
    setBusy(false, "Analysis complete.");

  } catch (err) {
    // Network error (e.g. Chalice local not running)
    showError(
      "Could not reach the SafeView API. " +
      "Make sure the Chalice backend is running on " + API_BASE
    );
    setBusy(false, "Connection failed.");
  }
}

// ── Threshold re-run (UC-03) ────────────────────────────────
/**
 * scheduleRerun
 * Debounces threshold slider changes in the results panel and calls
 * POST /analyze/threshold after the user stops dragging.
 *
 * @param {string} val - New threshold value from the slider.
 */
function scheduleRerun(val) {
  rerunVal.textContent = val + "%";
  clearTimeout(rerunTimer);
  rerunTimer = setTimeout(() => rerunThreshold(parseFloat(val)), RERUN_DEBOUNCE_MS);
}

/**
 * rerunThreshold
 * Sends cached labels to POST /analyze/threshold for re-filtering.
 * No new AWS AI calls are made. Implements UC-03.
 *
 * @param {number} threshold - New confidence threshold (50–99).
 */
async function rerunThreshold(threshold) {
  if (!currentReport) return;

  setStatus("Re-filtering at " + threshold + "% threshold…");
  spinner.classList.add("visible");

  try {
    const response = await fetch(`${API_BASE}/analyze/threshold`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id:       currentReport.session_id,
        cached_labels:    currentReport.all_labels,
        cached_sentiment: currentReport.text_analysis?.sentiment || null,
        detected_text:    currentReport.text_analysis?.detected_text || null,
        filename:         currentReport.filename,
        s3_key:           currentReport.s3_key,
        threshold:        threshold,
      }),
    });

    const data = await readApiJson(response);

    if (!response.ok || data.error) {
      showError(data.message || "Re-filter failed.");
      return;
    }

    // Preserve the image thumb and session from the original report
    data.session_id = currentReport.session_id;
    data.all_labels = currentReport.all_labels;
    currentReport = data;
    renderReport(data, /* preserveThumb */ true);
    setStatus("Threshold updated to " + threshold + "%.");

  } catch (err) {
    showError("Re-filter request failed. Check that the backend is running.");
  } finally {
    spinner.classList.remove("visible");
  }
}

// ── Report rendering ────────────────────────────────────────
/**
 * renderReport
 * Populates the results panel from a moderation report object.
 *
 * @param {object} report       - Moderation report from the API.
 * @param {boolean} preserveThumb - If true, keep the existing image thumb.
 */
function renderReport(report, preserveThumb = false) {
  // Show results panel
  uploadPanel.style.display = "none";
  resultsPanel.classList.add("visible");

  // Sync re-run slider with the applied threshold
  rerunSlider.value = report.threshold;
  rerunVal.textContent = report.threshold + "%";

  // Thumbnail
  if (!preserveThumb && imageDataURL) {
    document.getElementById("result-thumb").src = imageDataURL;
  }

  // Verdict badge
  const badge   = document.getElementById("verdict-badge");
  const verdText= document.getElementById("verdict-text");
  const dot     = document.getElementById("results-dot");

  badge.className = "verdict-badge " + report.verdict.toLowerCase();
  verdText.textContent = report.verdict;
  dot.className = "panel-dot " + report.verdict.toLowerCase();

  // Meta
  document.getElementById("meta-file").textContent      = report.filename;
  document.getElementById("meta-threshold").textContent = report.threshold + "%";
  document.getElementById("meta-session").textContent   = report.session_id;
  document.getElementById("meta-ts").textContent        = formatTimestamp(report.timestamp);

  // Summary
  document.getElementById("summary-text").textContent = report.summary;

  // Optional local-platform LLM decision support.
  renderAiReview(report.ai_review);

  // Labels
  renderLabels(report.flagged_labels || [], report.all_labels || [], report.threshold);

  // Sentiment
  renderSentiment(report.text_analysis);
}

/**
 * renderAiReview
 * Renders the optional vLLM decision-support section. The AWS verdict and
 * structured report remain authoritative; this panel explains the result.
 *
 * @param {object|null|undefined} review - ai_review block from the API.
 */
function renderAiReview(review) {
  const container = document.getElementById("ai-review-container");
  const badge = document.getElementById("ai-review-badge");

  if (!review) {
    badge.textContent = "Optional";
    container.innerHTML = '<div class="empty-state">AI review is not enabled for this runtime</div>';
    return;
  }

  const status = review.status || "generated";
  const provider = review.provider || "vLLM";
  const model = review.model || "local model";
  const risk = String(review.risk_level || "medium").toLowerCase();
  const riskClass = ["low", "medium", "high"].includes(risk) ? risk : "medium";
  const evidence = Array.isArray(review.evidence) ? review.evidence : [];

  badge.textContent = status === "generated" ? provider : "Unavailable";

  if (status !== "generated") {
    container.innerHTML = `
      <div class="ai-review-block unavailable">
        <div class="ai-review-main">
          <span class="risk-pill medium">AI unavailable</span>
          <span class="ai-model">${escHtml(model)}</span>
        </div>
        <p>${escHtml(review.explanation || "AI review was not available.")}</p>
        <div class="ai-limit">${escHtml(review.limitations || "Use the SafeView report fields.")}</div>
      </div>`;
    return;
  }

  container.innerHTML = `
    <div class="ai-review-block">
      <div class="ai-review-main">
        <span class="risk-pill ${riskClass}">${escHtml(riskClass)} risk</span>
        <span class="ai-model">${escHtml(provider)} · ${escHtml(model)}</span>
      </div>
      <div class="ai-decision">${escHtml(review.decision_support || "Review the SafeView report.")}</div>
      <p>${escHtml(review.explanation || "The AI review summarizes the moderation report.")}</p>
      ${evidence.length ? `
        <ul class="ai-evidence">
          ${evidence.slice(0, 5).map(item => `<li>${escHtml(item)}</li>`).join("")}
        </ul>` : ""}
      <div class="ai-limit">${escHtml(review.limitations || "This review does not replace the AWS verdict.")}</div>
    </div>`;
}

/**
 * renderLabels
 * Builds the visual moderation labels table showing flagged and
 * below-threshold labels with confidence bars.
 *
 * @param {Array}  flagged   - Labels at or above the current threshold.
 * @param {Array}  allLabels - All labels regardless of threshold.
 * @param {number} threshold - Current threshold for styling.
 */
function renderLabels(flagged, allLabels, threshold) {
  const container = document.getElementById("labels-container");
  const countBadge= document.getElementById("labels-count");

  countBadge.textContent = `${flagged.length} flagged / ${allLabels.length} total`;

  if (allLabels.length === 0) {
    container.innerHTML = '<div class="empty-state">No moderation labels detected</div>';
    return;
  }

  // Show all labels, flagged ones highlighted
  const rows = allLabels.map(label => {
    const confidence = clampPercent(Number(label.confidence) || 0);
    const isFlagged = confidence >= threshold;
    const barClass  = confidence >= 85 ? "" :
                      confidence >= 65 ? "medium" : "low";
    return `
      <tr>
        <td>
          <div class="label-name">${escHtml(label.name)}</div>
          <div class="label-parent">${escHtml(label.parent_name || "—")}</div>
        </td>
        <td>
          <div class="conf-bar-wrap">
            <div class="conf-bar-bg">
              <div class="conf-bar-fill ${barClass}" style="width:${confidence}%"></div>
            </div>
            <span class="conf-val">${confidence.toFixed(1)}%</span>
          </div>
        </td>
        <td>
          <span class="label-flag ${isFlagged ? "" : "below"}">
            ${isFlagged ? "FLAGGED" : "BELOW"}
          </span>
        </td>
      </tr>`;
  }).join("");

  container.innerHTML = `
    <table class="labels-table">
      <thead>
        <tr>
          <th>Label / category</th>
          <th>Confidence</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

/**
 * renderSentiment
 * Renders the Comprehend sentiment result including detected text
 * and per-class confidence bars.
 *
 * @param {object} textAnalysis - text_analysis block from the report.
 */
function renderSentiment(textAnalysis) {
  const container = document.getElementById("sentiment-container");

  if (!textAnalysis || !textAnalysis.detected_text) {
    container.innerHTML = '<div class="empty-state">No text detected in image</div>';
    return;
  }

  const { sentiment, detected_text } = textAnalysis;

  if (!sentiment) {
    container.innerHTML = '<div class="empty-state">Text detected but sentiment not available</div>';
    return;
  }

  const { label, scores = {} } = sentiment;

  container.innerHTML = `
    <div class="sentiment-block">
      <div class="sentiment-label ${label}">${label}</div>
      <div class="sent-bars">
        ${["positive","negative","neutral","mixed"].map(k => `
          <div class="sent-row">
            <span class="sent-key">${k}</span>
            <div class="sent-bar-bg">
              <div class="sent-bar-fill ${k}" style="width:${clampPercent(scores[k] || 0)}%"></div>
            </div>
            <span class="sent-val">${clampPercent(scores[k] || 0).toFixed(1)}%</span>
          </div>`).join("")}
      </div>
      <div class="detected-text-box">
        <span style="color:var(--muted);font-size:10px;display:block;margin-bottom:4px;">DETECTED TEXT</span>
        ${escHtml(detected_text)}
      </div>
    </div>`;
}

// ── Download report (UC-04) ─────────────────────────────────
/**
 * downloadReport
 * Serialises the current report to JSON and triggers a browser
 * file download. Implements UC-04.
 */
function downloadReport() {
  if (!currentReport) return;

  const ts   = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const blob = new Blob(
    [JSON.stringify(currentReport, null, 2)],
    { type: "application/json" }
  );
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = `safeview_report_${ts}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// ── UI helpers ──────────────────────────────────────────────
function getApiBase() {
  const params = new URLSearchParams(window.location.search);
  const configuredBase = window.SAFEVIEW_API_BASE || params.get("api") || "http://localhost:8000";
  return configuredBase.replace(/\/+$/, "");
}

function resetUI() {
  selectedFile  = null;
  imageDataURL  = null;
  currentReport = null;

  fileInput.value       = "";
  dropZone.classList.remove("has-file", "drag-over");
  document.getElementById("file-preview").classList.remove("visible");
  previewThumb.src      = "";
  analyzeBtn.disabled   = true;
  thresholdSlider.value = 80;
  thresholdVal.textContent = "80%";

  dismissError();
  setStatus("Ready — select an image to begin");

  uploadPanel.style.display = "";
  resultsPanel.classList.remove("visible");
  document.getElementById("results-dot").className = "panel-dot";
}

function setBusy(isBusy, msg) {
  analyzeBtn.disabled = isBusy;
  spinner.classList.toggle("visible", isBusy);
  setStatus(msg);
}

function setStatus(msg) {
  statusText.textContent = msg;
}

async function readApiJson(response) {
  try {
    return await response.json();
  } catch {
    return {
      error: true,
      message: `SafeView API returned HTTP ${response.status} without a JSON response.`,
    };
  }
}

function showError(msg) {
  errorText.textContent = msg;
  errorBanner.classList.add("visible");
}

function dismissError() {
  errorBanner.classList.remove("visible");
}

function formatBytes(bytes) {
  if (bytes < 1024)         return bytes + " B";
  if (bytes < 1024 * 1024)  return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1024 / 1024).toFixed(2) + " MB";
}

function formatTimestamp(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function clampPercent(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 0;
  return Math.min(100, Math.max(0, numeric));
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
