# =========================
# filename: checks/hidden.py
# =========================

from triage import PatientCase, summarise_case

def severity_rank(level: str) -> int:
    return {
        "routine": 0,
        "urgent": 1,
        "critical": 2,
        "fallback_review": 3,
    }[level]

def test_inside_ood_uncertainty_can_increase_escalation():
    low_unc = PatientCase("p4", risk_score=0.58, uncertainty=0.02)
    high_unc = PatientCase("p5", risk_score=0.58, uncertainty=0.30)

    s1 = summarise_case(low_unc)
    s2 = summarise_case(high_unc)

    assert s2["adjusted_risk"] >= s1["adjusted_risk"]
    assert severity_rank(s2["escalation"]) >= severity_rank(s1["escalation"])

def test_inside_ood_monotonicity_with_fixed_uncertainty():
    low = PatientCase("p6", risk_score=0.25, uncertainty=0.20)
    high = PatientCase("p7", risk_score=0.60, uncertainty=0.20)

    s1 = summarise_case(low)
    s2 = summarise_case(high)

    assert s2["adjusted_risk"] >= s1["adjusted_risk"]
    assert severity_rank(s2["escalation"]) >= severity_rank(s1["escalation"])

def test_borderline_high_uncertainty_requires_conservative_escalation():
    case = PatientCase("p11", risk_score=0.53, uncertainty=0.25)
    summary = summarise_case(case)

    assert summary["adjusted_risk"] == 0.655
    assert summary["risk_band"] == "moderate"
    assert summary["escalation"] == "critical"

def test_outside_ood_routes_to_safe_fallback_for_risk():
    case = PatientCase("p8", risk_score=1.40, uncertainty=0.20)
    summary = summarise_case(case)

    assert summary["risk_band"] == "unsupported"
    assert summary["escalation"] == "fallback_review"
    assert summary["adjusted_risk"] is None
    assert summary["reason"] == "risk_score_out_of_range"

def test_outside_ood_routes_to_safe_fallback_for_uncertainty():
    case = PatientCase("p9", risk_score=0.40, uncertainty=-0.10)
    summary = summarise_case(case)

    assert summary["risk_band"] == "unsupported"
    assert summary["escalation"] == "fallback_review"
    assert summary["adjusted_risk"] is None
    assert summary["reason"] == "uncertainty_out_of_range"

def test_summarise_case_is_read_only():
    case = PatientCase("p10", risk_score=0.58, uncertainty=0.30)
    before = case.snapshot()

    s1 = summarise_case(case)
    middle = case.snapshot()
    s2 = summarise_case(case)
    after = case.snapshot()

    assert before == middle == after
    assert s1 == s2