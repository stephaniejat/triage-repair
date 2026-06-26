"""
Filename: src/triage/model.py

-----
Each patient case has:
- patient_id,
- risk_score in [0,1],
- uncertainty in [0,1],
- admittance notes relevant for triage,
- derived risk_band for patient record keeping, and
- triage routing signal in the form of a categorical escalation level.
"""

from dataclasses import dataclass, field

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
            "risk_score": self.risk_score,
            "uncertainty": self.uncertainty,
            "notes": list(self.notes),
            "last_escalation": self.last_escalation,
        }
