"""
Filename: src/triage/routing.py
Routing and labelling decisions

-----
This module is a pure classification layer. It maps a pre-computed 
adjusted risk score to discrete labels for downstream routing.
Escalation is dependent on adjusted risk instead of raw risk, 
since plausible inputs can still become more severe 
as uncertainty changes interpretation.

Routing options:
- Low risk + low uncertainty → routine.
- Moderate risk/elevated uncertainty → urgent.
- High risk/high-risk-under-uncertainty → critical.

IMPORTANT:
- This module must never import from scoring.py.
- escalation_level() and risk_band() must never call each other.
- escalation_level() thresholds (0.30, 0.70) are the decision 
  signal, and must never be touched.
- risk_band() is presentational for patient record only, 
  and must not be used as the routing signal.
"""

# Routing signal — thresholds are fixed contract.
def escalation_level(adjusted: float) -> str:
    if adjusted < 0.30:
        return "routine"
    if adjusted < 0.70:
        return "urgent"
    return "critical"

# Display label — computed independently of routing.
def risk_band(adjusted: float) -> str:
    if adjusted < 0.30:
        return "low"
    if adjusted < 0.70:
        return "moderate"
    return "high"