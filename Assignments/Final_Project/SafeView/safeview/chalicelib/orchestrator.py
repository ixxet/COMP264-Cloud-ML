"""
chalicelib/orchestrator.py
--------------------------
AI orchestration module for SafeView.

Single responsibility: coordinate all AWS AI service calls and apply
confidence-threshold filtering to the results.

This module deliberately has no HTTP knowledge. app.py owns request/response
handling, while this file owns the service-call sequence and the normalised
shape passed to report.py.

AWS services called:
  - Amazon Rekognition  : DetectModerationLabels, DetectText
  - Amazon Comprehend   : DetectSentiment

Design decision DD-03: Rekognition's built-in DetectText is used for
OCR rather than introducing a third service (AWS Textract).

Design decision DD-04: Threshold filtering is applied here in the
backend, not in the frontend, to ensure consistent behaviour across
all client types.

Design decision DD-05: All Rekognition and Comprehend calls are
isolated in this module. Swapping to a different AI provider requires
changes only here.

Author : SafeView Team
Course : COMP 264 — Cloud Machine Learning
"""

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# AWS Comprehend's DetectSentiment accepts 5,000 UTF-8 bytes. The lower limit
# leaves room for multibyte characters after truncation and avoids service-side
# validation errors from OCR output that is close to the boundary.
_COMPREHEND_MAX_BYTES = 4900

# Rekognition text detection does not identify language; SafeView currently
# treats extracted text as English because that is the language Comprehend is
# configured to score.
_COMPREHEND_LANGUAGE  = "en"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def run_moderation_pipeline(
    s3_key: str,
    bucket: str,
    region: str,
    threshold: float,
) -> dict:
    """
    Run the full AI moderation pipeline for a given S3 image.

    Steps:
      1. Call DetectModerationLabels  → raw content flags
      2. Call DetectText              → text strings embedded in the image
      3. Call DetectSentiment         → sentiment of detected text (if any)
      4. Apply threshold filter       → remove labels below confidence cutoff

    Parameters
    ----------
    s3_key : str
        S3 object key of the uploaded image.
    bucket : str
        S3 bucket name.
    region : str
        AWS region.
    threshold : float
        Minimum confidence score (0–100) for a label to be included.

    Returns
    -------
    dict
        {
          "all_labels"      : [ { name, confidence, parent_name } ],
          "flagged_labels"  : [ { name, confidence, parent_name } ],
          "detected_text"   : str | None,
          "sentiment"       : { label, scores } | None,
          "threshold"       : float,
        }

    Raises
    ------
    Exception
        Re-raises boto3 errors so app.py can return HTTP 503.
    """
    # Clients are created here so the orchestration layer is the only place that
    # knows which AWS AI services are needed for a full analysis request.
    rekog_client      = _get_rekognition_client(region)
    comprehend_client = _get_comprehend_client(region)

    s3_ref = {"S3Object": {"Bucket": bucket, "Name": s3_key}}

    # ── Step 1: Content moderation labels ─────────────────────
    all_labels = _detect_moderation_labels(rekog_client, s3_ref)

    # ── Step 2: Text detection ────────────────────────────────
    detected_text = _detect_text(rekog_client, s3_ref)

    # ── Step 3: Sentiment analysis (conditional) ──────────────
    sentiment = None
    if detected_text:
        sentiment = _detect_sentiment(comprehend_client, detected_text)

    # ── Step 4: Apply threshold filter ───────────────────────
    flagged_labels = _apply_threshold(all_labels, threshold)

    return {
        "all_labels"    : all_labels,
        "flagged_labels": flagged_labels,
        "detected_text" : detected_text,
        "sentiment"     : sentiment,
        "threshold"     : threshold,
    }


def refilter_results(
    cached_labels: list,
    cached_sentiment: dict | None,
    detected_text: str | None,
    threshold: float,
) -> dict:
    """
    Re-filter a previously analysed result at a new confidence threshold.

    No AWS service calls are made — this operates entirely on data
    already held by the frontend (UC-03, design decision DD-04).
    app.py validates the cached label shape before calling this function so
    thresholding can stay focused on moderation logic rather than HTTP errors.

    Parameters
    ----------
    cached_labels : list
        The full list of labels returned by the original analysis
        (all_labels, not pre-filtered).
    cached_sentiment : dict | None
        The Comprehend sentiment result from the original analysis.
    detected_text : str | None
        The OCR text extracted during the original analysis.
    threshold : float
        New confidence threshold to apply.

    Returns
    -------
    dict
        Same structure as run_moderation_pipeline() return value.
    """
    flagged_labels = _apply_threshold(cached_labels, threshold)

    return {
        "all_labels"    : cached_labels,
        "flagged_labels": flagged_labels,
        "detected_text" : detected_text,
        "sentiment"     : cached_sentiment,
        "threshold"     : threshold,
    }


# ---------------------------------------------------------------------------
# Private — Rekognition helpers
# ---------------------------------------------------------------------------
def _detect_moderation_labels(rekog_client, s3_ref: dict) -> list:
    """
    Call DetectModerationLabels and return a normalised list of label dicts.

    Each label dict:
      {
        "name"        : str,    # e.g. "Explicit Nudity"
        "parent_name" : str,    # e.g. "Nudity" (top-level category)
        "confidence"  : float,  # 0.0 – 100.0
      }

    Raises
    ------
    Exception
        On any Rekognition API error.
    """
    try:
        response = rekog_client.detect_moderation_labels(
            Image=s3_ref,
            MinConfidence=0.0,   # Fetch ALL labels; threshold applied separately
        )
    except (BotoCoreError, ClientError) as exc:
        raise Exception(f"Rekognition DetectModerationLabels failed: {exc}") from exc

    labels = []
    for item in response.get("ModerationLabels", []):
        labels.append({
            "name"        : item.get("Name", ""),
            "parent_name" : item.get("ParentName", ""),
            # Store confidence as a percentage rounded for stable frontend
            # display and for repeatable cached re-filtering.
            "confidence"  : round(float(item.get("Confidence", 0.0)), 2),
        })

    # Sort by confidence descending so the most likely flags appear first in
    # both the report summary and the detailed frontend list.
    labels.sort(key=lambda x: x["confidence"], reverse=True)
    return labels


def _detect_text(rekog_client, s3_ref: dict) -> str | None:
    """
    Call DetectText and return all detected text concatenated as a single
    string, or None if no text was found.

    Only LINE-level detections are used (not individual WORDs) to avoid
    duplicate text and reduce Comprehend payload size.

    Raises
    ------
    Exception
        On any Rekognition API error.
    """
    try:
        response = rekog_client.detect_text(Image=s3_ref)
    except (BotoCoreError, ClientError) as exc:
        raise Exception(f"Rekognition DetectText failed: {exc}") from exc

    lines = [
        item["DetectedText"]
        for item in response.get("TextDetections", [])
        if item.get("Type") == "LINE"
    ]

    if not lines:
        return None

    combined = " ".join(lines)

    # Truncate by bytes rather than characters because Comprehend enforces the
    # payload limit after UTF-8 encoding.
    encoded = combined.encode("utf-8")
    if len(encoded) > _COMPREHEND_MAX_BYTES:
        combined = encoded[:_COMPREHEND_MAX_BYTES].decode("utf-8", errors="ignore")

    return combined if combined.strip() else None


# ---------------------------------------------------------------------------
# Private — Comprehend helper
# ---------------------------------------------------------------------------
def _detect_sentiment(comprehend_client, text: str) -> dict:
    """
    Call DetectSentiment and return a normalised sentiment result.

    Return value:
      {
        "label"  : "POSITIVE" | "NEGATIVE" | "NEUTRAL" | "MIXED",
        "scores" : {
            "positive" : float,
            "negative" : float,
            "neutral"  : float,
            "mixed"    : float,
        }
      }

    Raises
    ------
    Exception
        On any Comprehend API error.
    """
    try:
        response = comprehend_client.detect_sentiment(
            Text=text,
            LanguageCode=_COMPREHEND_LANGUAGE,
        )
    except (BotoCoreError, ClientError) as exc:
        raise Exception(f"Comprehend DetectSentiment failed: {exc}") from exc

    raw_scores = response.get("SentimentScore", {})

    return {
        "label" : response.get("Sentiment", "NEUTRAL"),
        "scores": {
            "positive": round(raw_scores.get("Positive", 0.0) * 100, 2),
            "negative": round(raw_scores.get("Negative", 0.0) * 100, 2),
            "neutral" : round(raw_scores.get("Neutral",  0.0) * 100, 2),
            "mixed"   : round(raw_scores.get("Mixed",    0.0) * 100, 2),
        },
    }


# ---------------------------------------------------------------------------
# Private — Threshold filter
# ---------------------------------------------------------------------------
def _apply_threshold(labels: list, threshold: float) -> list:
    """
    Return only labels whose confidence meets or exceeds the threshold.

    The caller supplies labels in the normalised SafeView shape. The function
    does not mutate label objects; it only selects the labels that should be
    considered flagged for the active confidence policy.

    Parameters
    ----------
    labels : list
        Full list of label dicts from _detect_moderation_labels().
    threshold : float
        Minimum confidence (0–100) for inclusion.

    Returns
    -------
    list
        Filtered and sorted list of label dicts.
    """
    return [
        label for label in labels
        if label["confidence"] >= threshold
    ]


# ---------------------------------------------------------------------------
# Private — Client factories
# ---------------------------------------------------------------------------
def _get_rekognition_client(region: str):
    """Return a boto3 Rekognition client."""
    return boto3.client("rekognition", region_name=region)


def _get_comprehend_client(region: str):
    """Return a boto3 Comprehend client."""
    return boto3.client("comprehend", region_name=region)
