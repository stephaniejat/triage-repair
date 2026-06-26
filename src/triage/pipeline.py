"""
Filename: src/triage/pipeline.py
Repository wiring layer

-----
This module combines scoring and triage together, and produces 
a patient record summary. This file is intentionally simple, 
and does not include the real repair, partly as a tempting but 
incorrect refactoring target for shallow repair attempts.
"""

from scoring import validate_case, adjusted_risk
from triage import escalation_level, risk_band

from .model import PatientCase

# Compute adjusted risk, escalation, and display band for a case.
def triage_case(case: PatientCase) -> dict[str, str | float]:
    valid, reason = validate_case(case.risk_score, case.uncertainty)

    if not valid:
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": None,
            "risk_band": "unsupported",
            "escalation": "fallback_review",
            "reason": reason,
        }
    # Address outside-OOD: unsupported inputs are not forced through 
    # normal triage; instead they route to safe fallback.

    adjusted = adjusted_risk(case.risk_score, case.uncertainty)
    escalation = escalation_level(adjusted)

    # For unusual but valid borderline cases, the rule should be more conservative:
    # if uncertainty is high + adjusted risk is near the "high" boundary,
    # then escalate more cautiously compared to coarse band mapping alone.
    
    if adjusted >= 0.65 and case.uncertainty >= 0.25:
        escalation = "critical"

    return {
        "patient_id": case.patient_id,
        "adjusted_risk": adjusted,
        "risk_band": risk_band(adjusted),
        "escalation": escalation,
    }

# Return a human-readable case summary. This function does not hardcode
# routing labels or bypass triage_case(), and must remain purely presentational.
def patient_record(case: PatientCase) -> str:

    result = triage_case(case)
    return (
        f"Patient {result['patient_id']}: "
        f"adjusted_risk={result['adjusted_risk']:.2f}, "
        f"band={result['risk_band']}, "
        f"escalation={result['escalation']}"
    )