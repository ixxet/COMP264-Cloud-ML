"""
chalicelib/s3_handler.py
------------------------
S3 storage module for SafeView.

Single responsibility: all interactions with Amazon S3.
  - Upload validated images under a UUID-prefixed key.
  - Write JSON audit log entries for every analysis request.

The rest of the backend should not construct S3 keys or boto3 S3 clients
directly. Keeping those details here makes the storage layout and audit logging
rules easy to review.

Key naming convention:
  uploads/{session_uuid}/{sanitised_filename}   — image
  logs/{session_uuid}/audit.json                — audit record

This module is cloud-vendor–specific by design. To migrate to a
different object store, only this file needs to change (DD-05).

Author : SafeView Team
Course : COMP 264 — Cloud Machine Learning
"""

import json
import uuid
import re
import datetime

import boto3
from botocore.exceptions import BotoCoreError, ClientError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Prefixes are part of the object layout used by the project documentation and
# IAM policy. Request handlers pass bucket/region in, but this module owns the
# path convention below those bucket-level boundaries.
_UPLOAD_PREFIX = "uploads"
_LOG_PREFIX    = "logs"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def upload_image_to_s3(
    image_bytes: bytes,
    filename: str,
    bucket: str,
    region: str,
) -> tuple[str, str]:
    """
    Upload a validated image to S3.

    Parameters
    ----------
    image_bytes : bytes
        Raw image data.
    filename : str
        Original filename (will be sanitised before use as S3 key).
    bucket : str
        Target S3 bucket name.
    region : str
        AWS region for the S3 client.

    Returns
    -------
    tuple[str, str]
        (s3_key, session_id)
        s3_key     — the full S3 object key for this image.
        session_id — the UUID generated for this request session.

    Raises
    ------
    Exception
        Re-raises any boto3 / S3 error so the caller (app.py) can
        return an appropriate HTTP error response.
    """
    # Each analysis gets an independent UUID. The UUID groups the image object
    # and audit record without relying on user-provided identifiers.
    session_id     = str(uuid.uuid4())
    safe_filename  = _sanitise_filename(filename)
    s3_key         = f"{_UPLOAD_PREFIX}/{session_id}/{safe_filename}"
    # Content type follows the already-validated extension so browsers and S3
    # metadata agree on how the stored object should be interpreted.
    content_type   = _get_content_type(filename)

    client = _get_s3_client(region)

    try:
        client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=image_bytes,
            ContentType=content_type,
            # Explicitly block public access — belt-and-suspenders alongside
            # the bucket-level block-public-access setting.
            ACL="private",
        )
    except (BotoCoreError, ClientError) as exc:
        raise Exception(f"S3 put_object failed for key '{s3_key}': {exc}") from exc

    return s3_key, session_id


def write_audit_log(
    session_id: str,
    bucket: str,
    region: str,
    verdict: str,
    s3_key: str,
    threshold: float,
) -> None:
    """
    Write a JSON audit log entry to S3.

    The audit record captures metadata about the moderation request
    but deliberately excludes image content and extracted text to
    avoid logging sensitive information (FR-13, FR-14).

    Parameters
    ----------
    session_id : str
        The UUID for this analysis session.
    bucket : str
        S3 bucket where the log will be written.
    region : str
        AWS region for the S3 client.
    verdict : str
        "FLAGGED" or "SAFE".
    s3_key : str
        The S3 key of the analysed image.
    threshold : float
        The confidence threshold applied during analysis.

    Raises
    ------
    Exception
        Re-raises S3 errors (caller treats audit log failure as non-fatal).
    """
    # The audit key mirrors the upload key's session folder so operators can
    # correlate storage and audit records without exposing image contents.
    log_key = f"{_LOG_PREFIX}/{session_id}/audit.json"

    audit_record = {
        "session_id" : session_id,
        "timestamp"  : datetime.datetime.utcnow().isoformat() + "Z",
        "s3_image_key": s3_key,
        "verdict"    : verdict,
        "threshold"  : threshold,
        # Intentionally omit: extracted text content, label details,
        # user identifiers, IP addresses (FR-14: no PII stored).
    }

    client = _get_s3_client(region)

    try:
        client.put_object(
            Bucket=bucket,
            Key=log_key,
            Body=json.dumps(audit_record, indent=2).encode("utf-8"),
            ContentType="application/json",
            ACL="private",
        )
    except (BotoCoreError, ClientError) as exc:
        raise Exception(f"S3 audit log write failed for session '{session_id}': {exc}") from exc


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _get_s3_client(region: str):
    """Return a boto3 S3 client for the configured deployment region."""
    return boto3.client("s3", region_name=region)


def _sanitise_filename(filename: str) -> str:
    """
    Remove path components and replace unsafe characters in a filename.

    Only alphanumerics, hyphens, underscores, and dots are kept.
    This prevents path traversal attacks and S3 key injection.
    """
    # Strip any directory components the client might have included. The final
    # key still lives inside the generated session folder.
    basename = filename.split("/")[-1].split("\\")[-1]
    # Replace any character that is not alphanumeric, -, _, or . with _
    safe = re.sub(r"[^a-zA-Z0-9\-_.]", "_", basename)
    # Guard against empty result
    return safe if safe else "upload.jpg"


def _get_content_type(filename: str) -> str:
    """
    Return the MIME type for JPEG or PNG based on file extension.

    validate_image() has already rejected unsupported extensions, so falling
    back to JPEG keeps this helper simple without widening accepted formats.
    """
    ext = filename.rsplit(".", 1)[-1].lower()
    return "image/png" if ext == "png" else "image/jpeg"
