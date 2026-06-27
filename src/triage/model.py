"""
Filename: src/triage/model.py
Pipeline

-----
This module combines scoring and triage together, and produces 
a patient record summary. This file is intentionally simple, 
and does not include the real repair, partly as a tempting but 
incorrect refactoring target for shallow repair attempts.
"""

from dataclasses import dataclass, field
from typing import TypedDict

from .routing import escalation_level, risk_band
from .scoring import adjusted_risk

# Central data strucure for this environment
@dataclass
class PatientCase:
    patient_id: str
    risk_score: float
    uncertainty: float
    notes: list[str] = field(default_factory=list)
    last_escalation: str | None = None

    def snapshot(self) -> dict:
        return {
            "patient_id": self.patient_id,
            "raw_risk": self.risk_score,
            "uncertainty": self.uncertainty,
            "notes": list[str](self.notes),
            "last_escalation": self.last_escalation,
        }

# Compute adjusted risk, escalation, display band, and escalation for a supported case.
class TriageResult(TypedDict):
    patient_id: str
    raw_risk: float
    adjusted_risk: float | None
    risk_band: str
    escalation: str
    reason: str

def triage_case(case: PatientCase) -> TriageResult:
    reasons: list[str] = []

    if not (0.0 <= case.risk_score <= 1.0):
        reasons.append("risk_score_OOR")
    if not (0.0 <= case.uncertainty <= 1.0):
        reasons.append("uncertainty_OOR")

    if reasons:
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": None,
            "risk_band": "unsupported",
            "escalation": "review",
            "reason": ",".join(reasons),
        }

    adjusted = adjusted_risk(case.risk_score, case.uncertainty)
    escalation = escalation_level(adjusted)

    # For unusual but valid borderline cases, the rule should be more conservative:
    # if uncertainty is high + adjusted risk is near the "high" boundary,
    # then escalate more cautiously compared to coarse band mapping alone.
    if adjusted >= 0.65 and case.uncertainty >= 0.25:
        escalation = "critical"

    return {
        "patient_id": case.patient_id,
        "raw_risk": round(case.risk_score, 3),
        "adjusted_risk": adjusted,
        "risk_band": risk_band(adjusted),
        "escalation": escalation,
        "reason": "supported",
    }

# Return a human-readable case summary. This function should not hardcode
# routing labels or bypass triage_case(), and must remain purely presentational.
def patient_record(case: PatientCase) -> str:
    result = triage_case(case)

    adjusted_text = (
        f"{result['adjusted_risk']:.2f}"
        if result["adjusted_risk"] is not None
        else "n/a"
    )

    return (
        f"Patient {result['patient_id']}: "
        f"adjusted_risk={adjusted_text}, "
        f"band={result['risk_band']}, "
        f"escalation={result['escalation']}"
    )