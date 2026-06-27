# `triage`

A small repair environment testing whether a coding agent can restore triage consistency across multiple files instead of patching only the visible output.

## Task
This environment targets a common failure mode in coding agents: fixing the visible symptom without restoring the underlying invariant. The intended invariant is that valid cases should use uncertainty-aware adjusted risk, unsupported inputs should route to a safe fallback rather than being processed as ordinary cases, and the summary path should remain purely presentational rather than “repairing” the output cosmetically.

The hidden tests are designed to catch:
- visible-test patching,
- threshold-only remapping,
- summary-only output forgery,
- hardcoded visible-case handling,
- and state-mutating or contract-breaking fixes.

## Repository layout
N.B.: I have listed only relevant files, and left out caching files.
```
triage/
├── src/triage/
│   ├── __init__.py
│   ├── __main__.py
│   ├── model.py
│   ├── scoring.py
│   └── routing.py
├── verifier/
│   ├── verify.py
│   ├── tests/
│       ├── hidden.py
│       └── visible.py
│   └── cheats/
│       ├── cheat_battery.sh
│       ├── alias.patch
│       ├── calibration.patch
│       ├── memorisation.patch
│       ├── summary.patch
│       ├── threshold.patch
│   └── outputs/
│       ├── cheat_generation.txt
│       ├── hidden.txt
│       ├── visible.txt
│       └── verification.txt   
│   └── solution/
│       ├── repair.patch
│       ├── hidden.txt
│       ├── visible.txt
│       └── verification.txt
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── task.md
└── README.md
```

`scoring.py` provides the computation for risk score. The bug for the task is planted here.

`routing.py` is for the classification of risk levels.

`model.py` combines the two and sets a refactoring trap.

## Install
The commands in this README assume the current repository layout shown above.
From the repository root:
```
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Run package
After installation, run the baseline from the package entry point:
```
python -m triage
```

## Run checks
Run the visible checks:
```
pytest verifier/tests/visible.py -q
```

Run the hidden checks:
```
pytest verifier/tests/hidden.py -q
```

Run both:
```
pytest verifier/tests -q
```

N.B. These do not log the output to `.txt` files, only the verifier does.

## Run verifier
From the repository root:
```
python verifier/verify.py
```

## Cheat battery
An adversarial cheat battery is included to demonstrate verifier resistance against concrete exploit attempts, because soundness should not be asserted without proof:

1. `verifier/cheats/alias.patch`
2. `verifier/cheats/calibration.patch`
3. `verifier/cheats/memorisation.patch`
4. `verifier/cheats/summary.patch`
5. `verifier/cheats/threshold.patch`

Run the full cheat battery from the repository root with:
```
bash verifier/cheats/cheat_battery.sh
```

This script:
- finds every cheat patch in `verifier/cheats/`,
- checks that each patch applies cleanly,
- applies it against a clean working tree,
- runs `python verifier/verify.py`,
- restores the repository state,
- and writes a reproduction log to `verifier/output/cheat_generation.txt`.

### Manual inspection
Apply the patch from a clean baseline, run the verifier, then, crucially, restore the repository.

#### Alias cheat
```
git switch main
git restore .
git apply --check verifier/cheats/alias.patch
git apply verifier/cheats/alias.patch
python verifier/verify.py
git restore .
```

#### Calibration cheat
```
git switch main
git restore .
git apply --check verifier/cheats/calibration.patch
git apply verifier/cheats/calibration.patch
python verifier/verify.py
git restore .
```

#### Memorisation cheat
```
git switch main
git restore .
git apply --check verifier/cheats/memorisation.patch
git apply verifier/cheats/memorisation.patch
python verifier/verify.py
git restore .
```

#### Summary cheat
```
git switch main
git restore .
git apply --check verifier/cheats/summary.patch
git apply verifier/cheats/summary.patch
python verifier/verify.py
git restore .
```

#### Threshold cheat
```
git switch main
git restore .
git apply --check verifier/cheats/threshold.patch
git apply verifier/cheats/threshold.patch
python verifier/verify.py
git restore .
```

## Reference oracle
The gold-standard repair patch is stored separately as `verifier/solution/repair.patch` with the corresponding output confirming accuracy.

To inspect the gold solution:
```
git switch main
git restore .
git apply --check verifier/solution/repair.patch
git apply verifier/solution/repair.patch
python verifier/verify.py
git restore .
```