"""
safeview/app.py
---------------
Main Chalice application entry point for SafeView.

Defines two REST endpoints:
  POST /analyze           — full moderation pipeline (UC-01)
  POST /analyze/threshold — re-filter cached results at new threshold (UC-03)

All business logic is delegated to modules in chalicelib/ to follow the
Single Responsibility principle (design decision DD-05).

Author : SafeView Team
Course : COMP 264 — Cloud Machine Learning
"""

import base64
import json
import math
import os

from chalice import Chalice, Response

from chalicelib.validator   import validate_image
from chalicelib.s3_handler  import upload_image_to_s3, write_audit_log
from chalicelib.orchestrator import run_moderation_pipeline, refilter_results
from chalicelib.report      import build_report
from chalicelib.llm_reviewer import build_ai_review, unavailable_review

# ---------------------------------------------------------------------------
# Threshold configuration
# ---------------------------------------------------------------------------
# SafeView intentionally keeps confidence thresholds in a constrained operating
# band. Lower values create too many false positives, while values near 100 can
# hide real moderation labels that Rekognition returns with high-but-not-perfect
# confidence.
MIN_THRESHOLD = 50.0
MAX_THRESHOLD = 99.0
_FALLBACK_DEFAULT_THRESHOLD = 80.0
_FALLBACK_LLM_TIMEOUT_SECONDS = 8.0


def _parse_threshold(value) -> tuple[float | None, str | None]:
    """
    Convert request input into a validated confidence threshold.

    Clients may send JSON numbers or numeric strings. Booleans, nulls,
    infinities, NaN, and non-numeric strings are rejected before they can reach
    the AWS orchestration path or the cached-label re-filtering path.
    """
    if value is None or isinstance(value, bool):
        return None, "Threshold must be a number between 50 and 99."

    try:
        threshold = float(value)
    except (TypeError, ValueError):
        return None, "Threshold must be a number between 50 and 99."

    if not math.isfinite(threshold):
        return None, "Threshold must be a number between 50 and 99."

    if not (MIN_THRESHOLD <= threshold <= MAX_THRESHOLD):
        return None, "Threshold must be between 50 and 99."

    return threshold, None


def _load_default_threshold() -> float:
    """
    Read the optional environment default without letting bad configuration
    break module import. The public endpoint still enforces the same threshold
    range when callers provide an explicit value.
    """
    raw_threshold = os.environ.get("MODERATION_THRESHOLD", str(_FALLBACK_DEFAULT_THRESHOLD))
    threshold, error = _parse_threshold(raw_threshold)
    if error:
        return _FALLBACK_DEFAULT_THRESHOLD
    return threshold


def _parse_bool_env(name: str, default: bool = False) -> bool:
    """Parse a feature flag from the environment."""
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _load_llm_timeout() -> float:
    """Read the optional LLM timeout without making bad env config fatal."""
    try:
        timeout = float(os.environ.get(
            "SAFEVIEW_LLM_TIMEOUT_SECONDS",
            str(_FALLBACK_LLM_TIMEOUT_SECONDS),
        ))
    except (TypeError, ValueError):
        return _FALLBACK_LLM_TIMEOUT_SECONDS

    if not math.isfinite(timeout) or timeout <= 0:
        return _FALLBACK_LLM_TIMEOUT_SECONDS
    return min(timeout, 30.0)


# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
app = Chalice(app_name="safeview")
app.debug = os.environ.get("SAFEVIEW_DEBUG", "false").lower() == "true"

# Environment-driven configuration (set in .chalice/config.json). These names
# are the deployment contract, so request handlers read them here rather than
# scattering os.environ lookups through the pipeline.
BUCKET_NAME = os.environ.get("SAFEVIEW_BUCKET", "safeview-images-dev")
REGION      = os.environ.get("SAFEVIEW_REGION", "us-east-1")
DEFAULT_THRESHOLD = _load_default_threshold()
LLM_ENABLED = _parse_bool_env("SAFEVIEW_LLM_ENABLED", False)
LLM_BASE_URL = os.environ.get("SAFEVIEW_LLM_BASE_URL", "").strip()
LLM_MODEL = os.environ.get("SAFEVIEW_LLM_MODEL", "").strip()
LLM_TIMEOUT_SECONDS = _load_llm_timeout()
LLM_API_KEY = os.environ.get("SAFEVIEW_LLM_API_KEY", "").strip() or None

# ---------------------------------------------------------------------------
# Helper — CORS headers for all responses
# ---------------------------------------------------------------------------
CORS_HEADERS = {
    "Content-Type"                 : "application/json",
    "Access-Control-Allow-Origin"  : "*",
    "Access-Control-Allow-Headers" : "Content-Type",
    "Access-Control-Allow-Methods" : "GET, POST, OPTIONS",
}


def _json_response(body: dict, status_code: int = 200) -> Response:
    """Wrap a dict as a Chalice Response with CORS headers."""
    return Response(
        body=json.dumps(body),
        status_code=status_code,
        headers=CORS_HEADERS,
    )


def _error_response(message: str, status_code: int = 400) -> Response:
    """Return a structured error payload."""
    return _json_response({"error": True, "message": message}, status_code)


def _attach_ai_review(report: dict) -> dict:
    """
    Add optional vLLM decision support without changing the core verdict.

    This is intentionally a non-fatal enhancement. Rekognition and Comprehend
    remain the authoritative moderation services; vLLM only explains their
    structured output for a human reviewer.
    """
    if not LLM_ENABLED:
        return report

    try:
        report["ai_review"] = build_ai_review(
            report=report,
            base_url=LLM_BASE_URL,
            model=LLM_MODEL,
            timeout_seconds=LLM_TIMEOUT_SECONDS,
            api_key=LLM_API_KEY,
        )
    except Exception as exc:
        app.log.warning("AI review unavailable: %s", str(exc))
        report["ai_review"] = unavailable_review(
            model=LLM_MODEL,
            reason=str(exc),
        )

    return report


def _validate_cached_labels(cached_labels) -> tuple[list | None, str | None]:
    """
    Validate frontend-cached Rekognition labels before local re-filtering.

    /analyze/threshold intentionally avoids new AWS calls, so the request body
    is the source of truth for labels. This guard keeps malformed cached data
    from surfacing as KeyError/TypeError in thresholding or report assembly and
    returns a clean HTTP 400 instead.
    """
    if not isinstance(cached_labels, list):
        return None, "cached_labels must be a list of label objects."

    normalised_labels = []
    for index, label in enumerate(cached_labels):
        if not isinstance(label, dict):
            return None, f"cached_labels[{index}] must be an object."

        name = label.get("name")
        if not isinstance(name, str):
            return None, f"cached_labels[{index}].name must be a string."

        raw_confidence = label.get("confidence")
        if raw_confidence is None or isinstance(raw_confidence, bool):
            return None, f"cached_labels[{index}].confidence must be a number."

        try:
            confidence = float(raw_confidence)
        except (TypeError, ValueError):
            return None, f"cached_labels[{index}].confidence must be a number."

        if not math.isfinite(confidence) or not (0.0 <= confidence <= 100.0):
            return None, f"cached_labels[{index}].confidence must be between 0 and 100."

        parent_name = label.get("parent_name", "")
        if parent_name is None:
            parent_name = ""
        if not isinstance(parent_name, str):
            return None, f"cached_labels[{index}].parent_name must be a string."

        normalised_label = dict(label)
        normalised_label["name"] = name
        normalised_label["parent_name"] = parent_name
        normalised_label["confidence"] = round(confidence, 2)
        normalised_labels.append(normalised_label)

    return normalised_labels, None


# ---------------------------------------------------------------------------
# OPTIONS preflight handler (CORS)
# ---------------------------------------------------------------------------
@app.route("/analyze", methods=["OPTIONS"])
@app.route("/analyze/threshold", methods=["OPTIONS"])
def options_handler():
    return Response(body="", status_code=200, headers=CORS_HEADERS)


@app.route("/health", methods=["GET"])
def health():
    """Small readiness endpoint for Docker Compose and Kubernetes probes."""
    return _json_response({"status": "ok", "service": "safeview"}, 200)


# ---------------------------------------------------------------------------
# POST /analyze
# Full moderation pipeline — UC-01
#
# Request body (JSON):
#   {
#     "image_data" : "<base64-encoded image bytes>",
#     "filename"   : "photo.jpg",
#     "threshold"  : 80.0          (optional, default from env)
#   }
#
# Response body (JSON):  see chalicelib/report.py → build_report()
# ---------------------------------------------------------------------------
@app.route("/analyze", methods=["POST"], content_types=["application/json"])
def analyze():
    """
    Full moderation pipeline endpoint.

    Steps:
      1. Parse and validate the incoming request body.
      2. Decode the base64 image and validate file type + size.
      3. Upload the image to S3 under a UUID-prefixed key.
      4. Call the AI orchestrator (Rekognition + Comprehend).
      5. Build and return the moderation report.
      6. Write an audit log entry to S3.
    """
    # ── 1. Parse request body ─────────────────────────────────
    try:
        body = app.current_request.json_body
        if body is None:
            return _error_response("Request body must be JSON.", 400)
    except Exception:
        return _error_response("Could not parse request body.", 400)

    if not isinstance(body, dict):
        return _error_response("Request body must be a JSON object.", 400)

    image_b64 = body.get("image_data")
    filename  = body.get("filename", "upload.jpg")
    # Threshold is optional on first analysis, but when present it must still
    # follow the same confidence policy used by the re-filter endpoint.
    threshold, threshold_error = _parse_threshold(body.get("threshold", DEFAULT_THRESHOLD))
    if threshold_error:
        return _error_response(threshold_error, 400)

    if not image_b64:
        return _error_response("Missing required field: image_data.", 400)
    if not isinstance(image_b64, str):
        return _error_response("image_data must be a base64 string.", 400)
    if not isinstance(filename, str) or not filename.strip():
        return _error_response("filename must be a non-empty string.", 400)

    # ── 2. Decode base64 and validate ─────────────────────────
    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception:
        return _error_response("image_data is not valid base64.", 400)

    validation_error = validate_image(image_bytes, filename)
    if validation_error:
        return _error_response(validation_error, 400)

    # ── 3. Upload to S3 ───────────────────────────────────────
    try:
        s3_key, session_id = upload_image_to_s3(
            image_bytes=image_bytes,
            filename=filename,
            bucket=BUCKET_NAME,
            region=REGION,
        )
    except Exception as exc:
        app.log.error("S3 upload failed: %s", str(exc))
        return _error_response("Image storage failed. Please try again.", 503)

    # ── 4. Run AI moderation pipeline ─────────────────────────
    try:
        moderation_result = run_moderation_pipeline(
            s3_key=s3_key,
            bucket=BUCKET_NAME,
            region=REGION,
            threshold=threshold,
        )
    except Exception as exc:
        app.log.error("Moderation pipeline failed: %s", str(exc))
        return _error_response("AI analysis failed. Please try again.", 503)

    # ── 5. Build report ───────────────────────────────────────
    report = build_report(
        session_id=session_id,
        s3_key=s3_key,
        filename=filename,
        threshold=threshold,
        moderation_result=moderation_result,
    )
    report = _attach_ai_review(report)

    # ── 6. Write audit log (non-blocking — log error but don't fail) ──
    try:
        write_audit_log(
            session_id=session_id,
            bucket=BUCKET_NAME,
            region=REGION,
            verdict=report["verdict"],
            s3_key=s3_key,
            threshold=threshold,
        )
    except Exception as exc:
        app.log.warning("Audit log write failed (non-fatal): %s", str(exc))

    return _json_response(report, 200)


# ---------------------------------------------------------------------------
# POST /analyze/threshold
# Re-filter cached results at a new threshold — UC-03
#
# Request body (JSON):
#   {
#     "session_id"       : "<uuid>",
#     "cached_labels"    : [ { "name": ..., "confidence": ..., "parent_name": ... } ],
#     "cached_sentiment" : { ... } or null,
#     "detected_text"    : "<string>" or null,
#     "filename"         : "photo.jpg",
#     "s3_key"           : "uploads/<uuid>/photo.jpg",
#     "threshold"        : 60.0
#   }
#
# No new AWS AI calls are made — only re-filtering logic runs.
# ---------------------------------------------------------------------------
@app.route("/analyze/threshold", methods=["POST"], content_types=["application/json"])
def analyze_threshold():
    """
    Threshold re-filter endpoint — bypasses all AI service calls.
    Applies a new confidence threshold to the cached Rekognition labels
    already held by the frontend and returns an updated report.
    """
    # ── Parse body ────────────────────────────────────────────
    try:
        body = app.current_request.json_body
        if body is None:
            return _error_response("Request body must be JSON.", 400)
    except Exception:
        return _error_response("Could not parse request body.", 400)

    if not isinstance(body, dict):
        return _error_response("Request body must be a JSON object.", 400)

    required = ["session_id", "cached_labels", "filename", "s3_key", "threshold"]
    for field in required:
        if field not in body:
            return _error_response(f"Missing required field: {field}.", 400)

    session_id       = body["session_id"]
    cached_labels    = body["cached_labels"]       # list of cached label dicts
    cached_sentiment = body.get("cached_sentiment")  # may be None
    detected_text    = body.get("detected_text")     # may be None
    filename         = body["filename"]
    s3_key           = body["s3_key"]

    # Parse first so malformed threshold input returns 400 instead of an
    # uncaught ValueError/TypeError from float().
    threshold, threshold_error = _parse_threshold(body["threshold"])
    if threshold_error:
        return _error_response(threshold_error, 400)

    cached_labels, labels_error = _validate_cached_labels(cached_labels)
    if labels_error:
        return _error_response(labels_error, 400)

    # ── Re-filter ─────────────────────────────────────────────
    try:
        filtered_result = refilter_results(
            cached_labels=cached_labels,
            cached_sentiment=cached_sentiment,
            detected_text=detected_text,
            threshold=threshold,
        )
    except Exception as exc:
        app.log.error("Threshold re-filter failed: %s", str(exc))
        return _error_response("Re-filter operation failed.", 500)

    # ── Build updated report ──────────────────────────────────
    report = build_report(
        session_id=session_id,
        s3_key=s3_key,
        filename=filename,
        threshold=threshold,
        moderation_result=filtered_result,
    )
    report = _attach_ai_review(report)

    return _json_response(report, 200)
