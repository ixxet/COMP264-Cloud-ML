"""
chalicelib/report.py
--------------------
Report assembly module for SafeView.

Single responsibility: transform the raw AI orchestrator output into
a clean, structured JSON report suitable for the frontend to render.

The report is the only data structure returned to the client. It is
also cached by the frontend to support UC-03 (threshold re-analysis)
without re-calling the backend AI services.

This module does not call AWS or validate HTTP input. It assumes upstream code
has already produced a normalised moderation_result and focuses on assembling a
stable response schema with a clear verdict and human-readable summary.

Author : SafeView Team
Course : COMP 264 — Cloud Machine Learning
"""

import datetime


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def build_report(
    session_id: str,
    s3_key: str,
    filename: str,
    threshold: float,
    moderation_result: dict,
) -> dict:
    """
    Assemble the SafeView moderation report from AI pipeline outputs.

    Parameters
    ----------
    session_id : str
        UUID for this analysis session (used for audit log correlation).
    s3_key : str
        S3 object key of the analysed image.
    filename : str
        Original filename provided by the client.
    threshold : float
        The confidence threshold applied to produce flagged_labels.
    moderation_result : dict
        Output from orchestrator.run_moderation_pipeline() or
        orchestrator.refilter_results().

    Returns
    -------
    dict
        Structured moderation report. Schema:

        {
          "session_id"     : str,
          "timestamp"      : str (ISO 8601),
          "filename"       : str,
          "s3_key"         : str,
          "threshold"      : float,
          "verdict"        : "FLAGGED" | "SAFE",
          "summary"        : str,
          "flagged_labels" : [ { name, parent_name, confidence } ],
          "all_labels"     : [ { name, parent_name, confidence } ],
          "text_analysis"  : {
              "detected_text" : str | None,
              "sentiment"     : { label, scores } | None,
          }
        }
    """
    # The orchestrator returns both the complete label set and the subset that
    # met the active threshold. Keeping both lets the frontend display details
    # and later request /analyze/threshold without a second AI call.
    flagged_labels = moderation_result.get("flagged_labels", [])
    all_labels     = moderation_result.get("all_labels", [])
    detected_text  = moderation_result.get("detected_text")
    sentiment      = moderation_result.get("sentiment")

    # ── Verdict ───────────────────────────────────────────────
    # Image is FLAGGED if any label exceeds the threshold OR
    # if the detected text sentiment is NEGATIVE (additional safety layer).
    verdict = _determine_verdict(flagged_labels, sentiment)

    # ── Human-readable summary ────────────────────────────────
    # The summary is derived from the same structured fields returned below so
    # the user-facing sentence cannot drift from the machine-readable report.
    summary = _build_summary(verdict, flagged_labels, detected_text, sentiment, threshold)

    return {
        "session_id"     : session_id,
        "timestamp"      : datetime.datetime.utcnow().isoformat() + "Z",
        "filename"       : filename,
        "s3_key"         : s3_key,
        "threshold"      : threshold,
        "verdict"        : verdict,
        "summary"        : summary,
        "flagged_labels" : flagged_labels,
        "all_labels"     : all_labels,
        "text_analysis"  : {
            "detected_text": detected_text,
            "sentiment"    : sentiment,
        },
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _determine_verdict(flagged_labels: list, sentiment: dict | None) -> str:
    """
    Determine FLAGGED or SAFE based on visual labels and text sentiment.

    An image is FLAGGED if:
      - One or more visual moderation labels meet the confidence threshold, OR
      - Text was detected AND Comprehend classifies it as NEGATIVE sentiment.

    Returns
    -------
    str
        "FLAGGED" or "SAFE"
    """
    # Visual moderation labels take priority: any label that meets the threshold
    # is enough to flag the image regardless of text sentiment.
    if flagged_labels:
        return "FLAGGED"

    # Text sentiment is a secondary safety signal. A negative sentiment result
    # flags otherwise visually-safe images that contain concerning text.
    if sentiment and sentiment.get("label") == "NEGATIVE":
        return "FLAGGED"

    return "SAFE"


def _build_summary(
    verdict: str,
    flagged_labels: list,
    detected_text: str | None,
    sentiment: dict | None,
    threshold: float,
) -> str:
    """
    Build a human-readable one-sentence summary of the moderation result.

    Examples
    --------
    "Image FLAGGED: 2 visual concern(s) detected above 80.0% confidence."
    "Image FLAGGED: detected text has NEGATIVE sentiment (confidence 97.3%)."
    "Image SAFE: no moderation concerns detected above 80.0% confidence."
    """
    if verdict == "FLAGGED":
        if flagged_labels:
            count = len(flagged_labels)
            top   = flagged_labels[0]
            # Labels are already confidence-sorted by the orchestrator, so the
            # first label is the most useful concise explanation for the report.
            return (
                f"Image FLAGGED: {count} visual concern(s) detected above "
                f"{threshold:.0f}% confidence. "
                f"Highest: '{top['name']}' ({top['confidence']:.1f}%)."
            )
        if sentiment and sentiment.get("label") == "NEGATIVE":
            neg_score = sentiment["scores"].get("negative", 0.0)
            return (
                f"Image FLAGGED: detected text has NEGATIVE sentiment "
                f"({neg_score:.1f}% confidence). "
                "No visual moderation concerns above threshold."
            )

    # SAFE
    if not flagged_labels and not detected_text:
        return (
            f"Image SAFE: no moderation concerns detected above "
            f"{threshold:.0f}% confidence. No text found in image."
        )
    return (
        f"Image SAFE: no moderation concerns detected above "
        f"{threshold:.0f}% confidence."
    )
