#!/usr/bin/env bash
# ================================================
# Filename: verifier/cheats/cheat_battery.sh
# Generate and validate cheat patches
#
# -----
# Workflow:
# 1. Assume .patch files already exist in verifier/cheats/
# 2. Loop over every *.patch:
#    i. ensure applies cleanly
#    ii. apply
#    iii. run verifier
#    iv. log result in verifier/cheats/output/generation_log.txt
#    v. restore repo
# ================================================
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
PATCH_DIR="$SCRIPT_DIR"
LOG_FILE="$PATCH_DIR/output/generation_log.txt"

# Ensure current location is repo root
if [[ -z "${ROOT_DIR}" ]]; then
  echo "Error: failed to find git repository" >&2
  exit 1
fi

cd "$ROOT_DIR"

# Ensure repaired baseline is committed and working tree is clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: commit or stash changes first." >&2
  exit 1
fi

# Ensure verifier exists
if [[ ! -f "verifier/verify.py" ]]; then
  echo "Error: missing verifier/verify.py" >&2
  exit 1
fi

PATCHES=()
while IFS= read -r patch; do
  PATCHES+=("$patch")
done < <(find "$PATCH_DIR" -maxdepth 1 -type f -name '*.patch' ! -name 'gold_fix.patch' | sort)

# Ensure .patch file exists
if [[ "${#PATCHES[@]}" -eq 0 ]]; then
  echo "Error: no cheat patches found in $PATCH_DIR" >&2
  exit 1
fi

# Reproduction log
: > "$LOG_FILE"

total_patches=0
apply_check_failures=0
verifier_passes=0
verifier_failures=0

echo "repo_root=$ROOT_DIR" | tee -a "$LOG_FILE"
echo "patch_dir=$PATCH_DIR" | tee -a "$LOG_FILE"
echo "patch_count=${#PATCHES[@]}" | tee -a "$LOG_FILE"
echo | tee -a "$LOG_FILE"

# Clean up function
cleanup() {
  set +e
  git restore . >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Generate one patch at a time
for patch in "${PATCHES[@]}"; do
  total_patches=$((total_patches + 1))
  name="$(basename "$patch")"

  echo "=== $name ===" | tee -a "$LOG_FILE"

  git restore . >>"$LOG_FILE" 2>&1

  # Check that patch applies cleanly
  if ! git apply --check "$patch" >>"$LOG_FILE" 2>&1; then
    echo "apply_check=FAIL" | tee -a "$LOG_FILE"
    apply_check_failures=$((apply_check_failures + 1))
    echo | tee -a "$LOG_FILE"
    continue
  fi

  # Apply patch
  git apply "$patch" >>"$LOG_FILE" 2>&1
  echo "apply=OK" | tee -a "$LOG_FILE"

  # Run verifier, log outcomes
  if python verifier/verify.py >>"$LOG_FILE" 2>&1; then
    echo "verify=OK" | tee -a "$LOG_FILE"
    verifier_passes=$((verifier_passes + 1))
  else
    echo "verify=FAIL" | tee -a "$LOG_FILE"
    verifier_failures=$((verifier_failures + 1))
  fi

  # Restore repo
  git restore . >>"$LOG_FILE" 2>&1
  echo | tee -a "$LOG_FILE"
done

# Print summary
echo "=== summary ===" | tee -a "$LOG_FILE"
echo "total_patches=$total_patches" | tee -a "$LOG_FILE"
echo "apply_check_failures=$apply_check_failures" | tee -a "$LOG_FILE"
echo "verifier_passes=$verifier_passes" | tee -a "$LOG_FILE"
echo "verifier_failures=$verifier_failures" | tee -a "$LOG_FILE"
echo "done" | tee -a "$LOG_FILE"