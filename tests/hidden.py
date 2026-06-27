"""
Filename: tests/hidden.py
Tests for shortcut behaviour

-----
"""

import pytest
from triage import PatientCase, triage_case

# Convert escalation level to numerical scale
def severity(level: str) -> int:
    return {
        "routine": 0,
        "urgent": 1,
        "critical": 2,
        "review": 3,
    }[level]

#  Ensure that inside-OOD means uncertainty increases escalation
def test_uncertainty():
    low = PatientCase("p4", risk_score=0.58, uncertainty=0.02)
    high = PatientCase("p5", risk_score=0.58, uncertainty=0.30)

    s1 = triage_case(low)
    s2 = triage_case(high)

    assert s1["adjusted_risk"] is not None
    assert s2["adjusted_risk"] is not None
    assert s2["adjusted_risk"] >= s1["adjusted_risk"]
    assert severity(s2["escalation"]) >= severity(s1["escalation"])
    
# Ensure inside-OOD monotonicity when uncertainty is fixed
def test_monotonicity():
    low = PatientCase("p6", risk_score=0.25, uncertainty=0.20)
    high = PatientCase("p7", risk_score=0.60, uncertainty=0.20)

    s1 = triage_case(low)
    s2 = triage_case(high)

    assert s1["adjusted_risk"] is not None
    assert s2["adjusted_risk"] is not None
    assert s2["adjusted_risk"] >= s1["adjusted_risk"]
    assert severity(s2["escalation"]) >= severity(s1["escalation"])

# Check that borderline + high uncertainty results in conservative escalation
def test_borderline():
    case = PatientCase("p11", risk_score=0.53, uncertainty=0.25)
    summary = triage_case(case)
    
    assert summary["adjusted_risk"] is not None
    assert summary["adjusted_risk"] == 0.655
    assert summary["risk_band"] == "moderate"
    assert summary["escalation"] == "critical"

# Ensure outside-OOD routes to safe fallback for risk and uncertainty
@pytest.mark.parametrize(
    "patient_id,risk_score,uncertainty,expected_reason",
    [
        ("p8", 1.40, 0.20, "risk_score_OOR"),
        ("p9", 0.40, -0.10, "uncertainty_OOR"),
    ],
)
def test_fallback(patient_id, risk_score, uncertainty, expected_reason):
    case = PatientCase(patient_id, risk_score=risk_score, uncertainty=uncertainty)
    summary = triage_case(case)

    assert summary["risk_band"] == "unsupported"
    assert summary["escalation"] == "review"
    assert summary["adjusted_risk"] is None
    assert summary["reason"] == expected_reason

# Ensure summary is read-only
def test_read_only():
    case = PatientCase("p10", risk_score=0.58, uncertainty=0.30)
    before = case.snapshot()

    s1 = triage_case(case)
    middle = case.snapshot()
    s2 = triage_case(case)
    after = case.snapshot()

    assert before == middle == after
    assert s1 == s2