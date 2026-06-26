"""
Filename: checks/visible.py
Checks superficial functionality

----

"""

from triage import PatientCase, triage_case

def test_low_risk_case_is_routine():
    case = PatientCase("p1", risk_score=0.10, uncertainty=0.05)
    summary = triage_case(case)
    assert summary["risk_band"] == "low"
    assert summary["escalation"] == "routine"

def test_high_risk_case_is_critical():
    case = PatientCase("p2", risk_score=0.90, uncertainty=0.05)
    summary = triage_case(case)
    assert summary["risk_band"] == "high"
    assert summary["escalation"] == "critical"

def test_summary_contains_expected_keys_for_valid_case():
    case = PatientCase("p3", risk_score=0.50, uncertainty=0.10)
    summary = triage_case(case)
    assert set(summary.keys()) == {
        "patient_id",
        "raw_risk",
        "adjusted_risk",
        "risk_band",
        "escalation",
    }

