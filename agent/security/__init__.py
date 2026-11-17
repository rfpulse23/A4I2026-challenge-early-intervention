"""
Security and Privacy Guardrails for Early Intervention Referral & Triage Platform.
Enforces HIPAA Privacy Rule (45 CFR § 164.514) and IDEA Part C / FERPA confidentiality (34 CFR § 303.401).
"""
from .privacy_guard import (
    mask_identifier,
    mask_name,
    generalize_tract,
    sanitize_handoff_reason,
    deidentify_candidate_record
)

__all__ = [
    "mask_identifier",
    "mask_name",
    "generalize_tract",
    "sanitize_handoff_reason",
    "deidentify_candidate_record",
]
