"""
Filename: checks/visible.py
Superficial functionality tests

----
Checks include:
- Risk/escalation mismatch
- Summary completeness
"""

import pytest
from triage import PatientCase, triage_case

# Check that risk band matches escalation level
@pytest.mark.parametrize(
    "patient_id,risk_score,uncertainty,expected_band,expected_escalation",
    [
        ("p1", 0.10, 0.05, "low", "routine"),
        ("p2", 0.90, 0.05, "high", "critical"),
    ],
)
def test_label_mismatch(patient_id, risk_score, uncertainty, expected_band, expected_escalation):
    case = PatientCase(patient_id, risk_score=risk_score, uncertainty=uncertainty)
    summary = triage_case(case)
    assert summary["risk_band"] == expected_band
    assert summary["escalation"] == expected_escalation
    
# Check that summary contains expected snapshot items for valid case
def test_summary_complete():
    case = PatientCase("p3", risk_score=0.50, uncertainty=0.10)
    summary = triage_case(case)
    assert set(summary.keys()) == {
        "patient_id",
        "raw_risk",
        "adjusted_risk",
        "risk_band",
        "escalation",
        "reason",
    }