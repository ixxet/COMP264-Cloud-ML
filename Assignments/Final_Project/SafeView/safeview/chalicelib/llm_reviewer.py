"""
chalicelib/llm_reviewer.py
--------------------------
Optional vLLM decision-support module for SafeView.

This module does not classify images and does not replace AWS Rekognition or
Amazon Comprehend. It receives the structured SafeView report after the normal
AWS pipeline has finished, asks an OpenAI-compatible vLLM endpoint to explain
the result, and returns a small JSON object for the frontend.

The design is intentionally non-blocking from an application perspective:
app.py catches failures from this module and still returns the core moderation
report. That keeps the assignment's AWS implementation authoritative while
adding a platform AI workflow when SafeView runs on Kubernetes.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


def build_ai_review(
    report: dict,
    base_url: str,
    model: str,
    timeout_seconds: float,
    api_key: str | None = None,
) -> dict:
    """
    Generate a reviewer-facing explanation from a SafeView report.

    Parameters
    ----------
    report : dict
        The structured report produced by report.build_report().
    base_url : str
        OpenAI-compatible vLLM base URL, for example
        http://vllm.ai.svc.cluster.local:8000/v1.
    model : str
        Model name returned by the vLLM /v1/models endpoint.
    timeout_seconds : float
        Hard timeout for the local LLM call.
    api_key : str | None
        Optional bearer token for OpenAI-compatible endpoints that require one.

    Returns
    -------
    dict
        {
          "status": "generated",
          "provider": "vLLM",
          "model": "...",
          "risk_level": "low" | "medium" | "high",
          "decision_support": "...",
          "explanation": "...",
          "evidence": ["..."],
          "limitations": "..."
        }
    """
    if not base_url:
        raise ValueError("SAFEVIEW_LLM_BASE_URL is not configured.")
    if not model:
        raise ValueError("SAFEVIEW_LLM_MODEL is not configured.")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are SafeView's AI review assistant. You do not inspect "
                    "the image and you must not override the AWS verdict. Use "
                    "only the structured report provided by the application. "
                    "The threshold is a cutoff for moderation labels, not a "
                    "confidence score for the overall verdict. Do not invent "
                    "image details, scores, or labels that are not present. "
                    "Return only valid JSON with keys: risk_level, "
                    "decision_support, explanation, evidence, limitations. "
                    "risk_level must be low, medium, or high. evidence must be "
                    "an array of short strings."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Create a concise moderation decision-support review for "
                    "this SafeView report:\n"
                    f"{json.dumps(_compact_report(report), ensure_ascii=True)}"
                ),
            },
        ],
        "temperature": 0.1,
        "max_tokens": 360,
    }

    response = _post_chat_completion(
        base_url=base_url,
        payload=payload,
        timeout_seconds=timeout_seconds,
        api_key=api_key,
    )
    content = _extract_message_content(response)
    review = _parse_review_json(content)
    grounding = _grounded_review(report)
    review = _normalise_review(review, grounding)

    review["status"] = "generated"
    review["provider"] = "vLLM"
    review["model"] = model
    return review


def unavailable_review(model: str, reason: str) -> dict:
    """Return a stable report object when the optional LLM call fails."""
    return {
        "status": "unavailable",
        "provider": "vLLM",
        "model": model or "not configured",
        "risk_level": "unknown",
        "decision_support": "Use the SafeView AWS verdict and report fields.",
        "explanation": "The optional AI review layer was not available.",
        "evidence": [],
        "limitations": reason,
    }


def _post_chat_completion(
    base_url: str,
    payload: dict,
    timeout_seconds: float,
    api_key: str | None,
) -> dict:
    """POST to an OpenAI-compatible /chat/completions endpoint."""
    endpoint = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        endpoint,
        data=body,
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"vLLM returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"vLLM request failed: {exc.reason}") from exc


def _extract_message_content(response: dict) -> str:
    """Extract the assistant text from an OpenAI-compatible response."""
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("vLLM response did not include choices.")

    message = choices[0].get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("vLLM response did not include message content.")
    return content.strip()


def _parse_review_json(content: str) -> dict:
    """Parse model output even if it includes small text outside the JSON."""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(content[start:end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("vLLM review must be a JSON object.")
    return parsed


def _normalise_review(review: dict, grounding: dict) -> dict:
    """Constrain model output to the frontend contract."""
    risk_level = grounding["risk_level"]
    decision_support = grounding["decision_support"]
    explanation = _clean_text(
        review.get("explanation"),
        grounding["explanation"],
        limit=500,
    )
    if not _explanation_is_grounded(explanation, grounding):
        explanation = grounding["explanation"]

    limitations = (
        "This review summarizes AWS Rekognition and Comprehend outputs. "
        "It is not an independent image classifier."
    )

    return {
        "risk_level": risk_level,
        "decision_support": decision_support,
        "explanation": explanation,
        "evidence": grounding["evidence"],
        "limitations": limitations,
    }


def _compact_report(report: dict) -> dict:
    """Keep the prompt grounded in fields that matter for decision support."""
    text_analysis = report.get("text_analysis") or {}
    detected_text = text_analysis.get("detected_text")
    if isinstance(detected_text, str) and len(detected_text) > 700:
        detected_text = detected_text[:700] + "..."

    return {
        "verdict": report.get("verdict"),
        "summary": report.get("summary"),
        "threshold": report.get("threshold"),
        "flagged_labels": (report.get("flagged_labels") or [])[:5],
        "all_labels_count": len(report.get("all_labels") or []),
        "top_labels": (report.get("all_labels") or [])[:5],
        "text_analysis": {
            "detected_text": detected_text,
            "sentiment": text_analysis.get("sentiment"),
        },
    }


def _grounded_review(report: dict) -> dict:
    """Build the source-of-truth review fields from the report itself."""
    verdict = str(report.get("verdict") or "UNKNOWN").upper()
    threshold = report.get("threshold")
    flagged_labels = report.get("flagged_labels") or []
    all_labels = report.get("all_labels") or []
    text_analysis = report.get("text_analysis") or {}
    sentiment = text_analysis.get("sentiment")
    detected_text = text_analysis.get("detected_text")

    evidence = [f"AWS verdict: {verdict}."]
    if flagged_labels:
        top = flagged_labels[0]
        evidence.append(
            f"Top flagged label: {top.get('name', 'unknown')} "
            f"({float(top.get('confidence', 0.0)):.1f}%)."
        )
        evidence.append(
            f"{len(flagged_labels)} moderation label(s) met the "
            f"{float(threshold):.0f}% threshold."
        )
        risk_level = "high"
        decision_support = "Manual review required before approval."
    else:
        evidence.append(
            f"No moderation labels met the {float(threshold):.0f}% threshold."
        )
        if all_labels:
            evidence.append(
                f"{len(all_labels)} label(s) were returned below the active threshold."
            )
            risk_level = "medium"
            decision_support = "Review below-threshold labels before approval."
        else:
            risk_level = "low"
            decision_support = "Approve automatically if the deployment policy allows."

    if sentiment:
        label = str(sentiment.get("label", "UNKNOWN")).upper()
        evidence.append(f"Detected text sentiment: {label}.")
        if label == "NEGATIVE":
            risk_level = "high"
            decision_support = "Manual review required because detected text is negative."
    elif detected_text:
        evidence.append("Text was detected, but sentiment was not available.")
        if risk_level == "low":
            risk_level = "medium"
            decision_support = "Review detected text before approval."
    else:
        evidence.append("No OCR text was detected.")

    explanation = (
        "The AI reviewer summarizes SafeView's structured AWS results. "
        f"The current report is {verdict}; " + " ".join(evidence[1:])
    )

    label_names = " ".join(
        str(label.get("name", "")).lower()
        for label in all_labels[:10]
        if isinstance(label, dict)
    )

    return {
        "risk_level": risk_level,
        "decision_support": decision_support,
        "explanation": explanation,
        "evidence": evidence[:5],
        "label_names": label_names,
        "has_labels": bool(all_labels),
    }


def _explanation_is_grounded(explanation: str, grounding: dict) -> bool:
    """Reject common unsupported phrases from free-form model output."""
    lowered = explanation.lower()
    if "confidence level" in lowered or "confidence score" in lowered:
        return False

    sensitive_terms = [
        "explicit",
        "suggestive",
        "nudity",
        "violence",
        "weapon",
        "drug",
        "hate",
    ]
    if not grounding["has_labels"]:
        return not any(term in lowered for term in sensitive_terms)

    label_names = grounding["label_names"]
    return not any(term in lowered and term not in label_names for term in sensitive_terms)


def _clean_text(value, fallback: str, limit: int) -> str:
    """Convert arbitrary model output fields into bounded strings."""
    if value is None:
        text = fallback
    else:
        text = " ".join(str(value).split())
        if not text:
            text = fallback
    return text[:limit]
