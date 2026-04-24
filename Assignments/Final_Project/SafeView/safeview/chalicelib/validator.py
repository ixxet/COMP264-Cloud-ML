"""
chalicelib/validator.py
-----------------------
Image validation module for SafeView.

Single responsibility: verify that an uploaded file meets the
format and size requirements before any AWS service is called.

Validation is intentionally local and deterministic. Rejecting unsuitable files
before S3 upload avoids storing bad input and prevents avoidable Rekognition
errors from becoming user-facing service failures.

Supported formats : JPEG, PNG
Maximum file size  : 5 MB (AWS Rekognition API limit via S3 reference)

Author : SafeView Team
Course : COMP 264 — Cloud Machine Learning
"""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024   # 5 MB

# Magic-byte signatures for supported image formats. Extension checks alone are
# not enough because clients can rename arbitrary files to .jpg or .png.
_MAGIC_BYTES = {
    "jpeg": [b"\xff\xd8\xff"],
    "png" : [b"\x89PNG\r\n\x1a\n"],
}

# Allowed file extensions (case-insensitive)
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def validate_image(image_bytes: bytes, filename: str) -> str | None:
    """
    Validate an image before uploading to S3.

    Parameters
    ----------
    image_bytes : bytes
        Raw image data decoded from the base64 payload.
    filename : str
        Original filename provided by the client (used for extension check).

    Returns
    -------
    str | None
        An error message string if validation fails, or None if the image
        passes all checks.
    """
    # ── 1. File size check ────────────────────────────────────
    # Size is checked before inspecting content so oversized files are rejected
    # cheaply and never reach S3 or Rekognition.
    size_error = _check_file_size(image_bytes)
    if size_error:
        return size_error

    # ── 2. File extension check ───────────────────────────────
    # The extension controls S3 content type metadata later in the pipeline.
    ext_error = _check_extension(filename)
    if ext_error:
        return ext_error

    # ── 3. Magic-byte (file signature) check ─────────────────
    # The signature check confirms the bytes match one of the supported image
    # containers rather than relying only on the user-provided filename.
    sig_error = _check_magic_bytes(image_bytes)
    if sig_error:
        return sig_error

    return None   # all checks passed


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------
def _check_file_size(image_bytes: bytes) -> str | None:
    """Return an error string if the file exceeds the Rekognition size limit."""
    size_mb = len(image_bytes) / (1024 * 1024)
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        return (
            f"File size {size_mb:.1f} MB exceeds the 5 MB limit. "
            "Please upload a smaller image."
        )
    return None


def _check_extension(filename: str) -> str | None:
    """Return an error string if the user-provided extension is unsupported."""
    # Extract extension safely — handle filenames with no extension
    dot_index = filename.rfind(".")
    if dot_index == -1:
        return "File has no extension. Only JPEG and PNG files are supported."

    ext = filename[dot_index:].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        return (
            f"File type '{ext}' is not supported. "
            "Only JPEG (.jpg / .jpeg) and PNG (.png) files are accepted."
        )
    return None


def _check_magic_bytes(image_bytes: bytes) -> str | None:
    """
    Verify the file signature (magic bytes) matches a supported format.
    This prevents clients from renaming an unsupported file to .jpg/.png
    and bypassing the extension check.
    """
    for _fmt, signatures in _MAGIC_BYTES.items():
        for sig in signatures:
            if image_bytes[:len(sig)] == sig:
                return None   # matched a known format

    return (
        "File content does not match a supported image format. "
        "Only genuine JPEG and PNG files are accepted."
    )
