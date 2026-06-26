#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "${ROOT_DIR}" ]]; then
  echo "Error: failed to find git repository" >&2
  exit 1
fi
cd "$ROOT_DIR"

PIPELINE_FILE="src/triage/pipeline.py"
CHEAT_DIR="verifier/cheats"
BASE_BRANCH="${1:-main}"

if [[ ! -f "$PIPELINE_FILE" ]]; then
  echo "Error: missing $PIPELINE_FILE" >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: Commit or stash changes first." >&2
  exit 1
fi

mkdir -p "$CHEAT_DIR"

if ! git rev-parse --verify "$BASE_BRANCH" >/dev/null 2>&1; then
  echo "Error: failed to find base branch '$BASE_BRANCH'" >&2
  exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
if [[ -z "$CURRENT_BRANCH" ]]; then
  echo "Error: detached HEAD is not supported by this script" >&2
  exit 1
fi

cleanup() {
  set +e
  git switch "$CURRENT_BRANCH" >/dev/null 2>&1 || true
}
trap cleanup EXIT

assert_patch_applies() {
  local patch_file="$1"
  git switch "$BASE_BRANCH" >/dev/null
  git apply --check "$patch_file"
  git apply "$patch_file"
  if [[ -f verifier/verify.py ]]; then
    python verifier/verify.py >/tmp/cheat_verify.out 2>/tmp/cheat_verify.err || true
    echo "Verifier output for $(basename "$patch_file"):"
    cat /tmp/cheat_verify.out 2>/dev/null || true
    cat /tmp/cheat_verify.err 2>/dev/null || true
  fi
  git restore .
}

write_pipeline_calibration_only() {
  cat > "$PIPELINE_FILE" <<'PYEOF'
from .model import PatientCase
from .scoring import validate_case_inputs, adjusted_risk, risk_band
from .triage import escalation_level_from_adjusted

def summarise_case(case: PatientCase) -> dict:
    valid, reason = validate_case_inputs(case.risk_score, case.uncertainty)

    if not valid:
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": None,
            "risk_band": "unsupported",
            "escalation": "fallback_review",
            "reason": reason,
        }

    adj = adjusted_risk(case.risk_score, case.uncertainty)
    band = risk_band(adj)
    if band == "low":
        escalation = "routine"
    elif band == "moderate":
        escalation = "urgent"
    else:
        escalation = "critical"

    return {
        "patient_id": case.patient_id,
        "raw_risk": round(case.risk_score, 3),
        "adjusted_risk": round(adj, 3),
        "risk_band": band,
        "escalation": escalation,
    }
PYEOF
}

write_pipeline_summary_only() {
  cat > "$PIPELINE_FILE" <<'PYEOF'
from .model import PatientCase
from .scoring import validate_case_inputs, adjusted_risk, risk_band
from .triage import escalation_level_from_adjusted

def summarise_case(case: PatientCase) -> dict:
    valid, reason = validate_case_inputs(case.risk_score, case.uncertainty)

    if not valid:
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": None,
            "risk_band": "unsupported",
            "escalation": "fallback_review",
            "reason": reason,
        }

    adj = adjusted_risk(case.risk_score, case.uncertainty)
    band = risk_band(adj)
    escalation = escalation_level_from_adjusted(adj)

    if band == "low":
        shown_escalation = "routine"
    elif band == "moderate":
        shown_escalation = "urgent"
    else:
        shown_escalation = "critical"

    return {
        "patient_id": case.patient_id,
        "raw_risk": round(case.risk_score, 3),
        "adjusted_risk": round(adj, 3),
        "risk_band": band,
        "escalation": shown_escalation,
    }
PYEOF
}

write_pipeline_hardcoded_cases() {
  cat > "$PIPELINE_FILE" <<'PYEOF'
from .model import PatientCase
from .scoring import validate_case_inputs, adjusted_risk, risk_band
from .triage import escalation_level_from_adjusted

def summarise_case(case: PatientCase) -> dict:
    if case.risk_score == 0.10 and case.uncertainty == 0.05:
        return {
            "patient_id": case.patient_id,
            "raw_risk": 0.1,
            "adjusted_risk": 0.125,
            "risk_band": "low",
            "escalation": "routine",
        }

    if case.risk_score == 0.90 and case.uncertainty == 0.05:
        return {
            "patient_id": case.patient_id,
            "raw_risk": 0.9,
            "adjusted_risk": 0.925,
            "risk_band": "high",
            "escalation": "critical",
        }

    if case.risk_score == 0.50 and case.uncertainty == 0.10:
        return {
            "patient_id": case.patient_id,
            "raw_risk": 0.5,
            "adjusted_risk": 0.55,
            "risk_band": "moderate",
            "escalation": "urgent",
        }

    if case.risk_score == 0.58 and case.uncertainty == 0.30:
        return {
            "patient_id": case.patient_id,
            "raw_risk": 0.58,
            "adjusted_risk": 0.73,
            "risk_band": "high",
            "escalation": "critical",
        }

    valid, reason = validate_case_inputs(case.risk_score, case.uncertainty)

    if not valid:
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": None,
            "risk_band": "unsupported",
            "escalation": "fallback_review",
            "reason": reason,
        }

    adj = adjusted_risk(case.risk_score, case.uncertainty)
    band = risk_band(adj)
    if band == "low":
        escalation = "routine"
    elif band == "moderate":
        escalation = "urgent"
    else:
        escalation = "critical"

    return {
        "patient_id": case.patient_id,
        "raw_risk": round(case.risk_score, 3),
        "adjusted_risk": round(adj, 3),
        "risk_band": band,
        "escalation": escalation,
    }
PYEOF
}

write_pipeline_mutation() {
  cat > "$PIPELINE_FILE" <<'PYEOF'
from .model import PatientCase
from .scoring import validate_case_inputs, adjusted_risk, risk_band
from .triage import escalation_level_from_adjusted

def summarise_case(case: PatientCase) -> dict:
    if case.last_escalation is not None:
        valid, reason = validate_case_inputs(case.risk_score, case.uncertainty)
        if not valid:
            return {
                "patient_id": case.patient_id,
                "raw_risk": round(case.risk_score, 3),
                "adjusted_risk": None,
                "risk_band": "unsupported",
                "escalation": "fallback_review",
                "reason": reason,
            }

        adj = adjusted_risk(case.risk_score, case.uncertainty)
        band = risk_band(adj)
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": round(adj, 3),
            "risk_band": band,
            "escalation": case.last_escalation,
        }

    valid, reason = validate_case_inputs(case.risk_score, case.uncertainty)

    if not valid:
        return {
            "patient_id": case.patient_id,
            "raw_risk": round(case.risk_score, 3),
            "adjusted_risk": None,
            "risk_band": "unsupported",
            "escalation": "fallback_review",
            "reason": reason,
        }

    adj = adjusted_risk(case.risk_score, case.uncertainty)
    band = risk_band(adj)
    if band == "low":
        escalation = "routine"
    elif band == "moderate":
        escalation = "urgent"
    else:
        escalation = "critical"

    case.last_escalation = escalation

    return {
        "patient_id": case.patient_id,
        "raw_risk": round(case.risk_score, 3),
        "adjusted_risk": round(adj, 3),
        "risk_band": band,
        "escalation": escalation,
    }
PYEOF
}

generate_patch() {
  local branch_name="$1"
  local patch_name="$2"
  local writer_fn="$3"

  git switch "$BASE_BRANCH" >/dev/null
  git branch -D "$branch_name" >/dev/null 2>&1 || true
  git switch -c "$branch_name" >/dev/null

  "$writer_fn"

  git add "$PIPELINE_FILE"
  git commit -m "Cheat: $patch_name" >/dev/null
  git diff "$BASE_BRANCH"...HEAD > "$CHEAT_DIR/$patch_name"
  git switch "$BASE_BRANCH" >/dev/null
  git branch -D "$branch_name" >/dev/null

  echo "Generated $CHEAT_DIR/$patch_name"
  assert_patch_applies "$CHEAT_DIR/$patch_name"
  echo "Validated $CHEAT_DIR/$patch_name"
}

generate_patch "calibration-only" "calibration_only.patch" write_pipeline_calibration_only
generate_patch "summary-only" "summary_only.patch" write_pipeline_summary_only
generate_patch "hardcoded-cases" "hardcoded_cases.patch" write_pipeline_hardcoded_cases
generate_patch "mutation" "mutation.patch" write_pipeline_mutation

git switch "$CURRENT_BRANCH" >/dev/null

echo
echo "Done. Generated patches:"
ls -1 "$CHEAT_DIR"/*.patch
