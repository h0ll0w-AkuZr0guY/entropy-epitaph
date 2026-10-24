"""
Extinction Certificate Generator.

Generates a deterministic, cryptographically-anchored certificate
when a monument reaches entropy_score >= 1.0.

Format: EXTINCT-xxxx-xxxx-xxxx  (derived from SHA-256)
"""

import hashlib
from datetime import datetime


def generate_certificate(
    monument_id: str,
    extinct_at: datetime,
    original_content: str | None,
) -> dict:
    """
    Generate a deterministic extinction certificate.

    Args:
        monument_id: UUID string of the monument
        extinct_at: exact datetime of extinction
        original_content: original content (or empty string if nameless)

    Returns:
        dict with cert_id, full_hash, extinct_at
    """
    # Hash the original content separately to avoid exposing it
    content_hash = hashlib.sha256(
        (original_content or "").encode("utf-8")
    ).hexdigest()[:16]

    # Deterministic payload: monument identity + moment of death + content fingerprint
    payload = f"{monument_id}|{extinct_at.isoformat()}|{content_hash}"
    full_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # Format: EXTINCT-xxxx-xxxx-xxxx (12 hex chars, split into 3 groups of 4)
    raw = full_hash[:12]
    cert_id = f"EXTINCT-{raw[:4]}-{raw[4:8]}-{raw[8:]}"

    return {
        "cert_id": cert_id,
        "full_hash": full_hash,
        "extinct_at": extinct_at.isoformat(),
    }
