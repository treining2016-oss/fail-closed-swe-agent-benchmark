# Quickstart

Requirements:

- Python 3.10+
- Git

## Run the control self-test

```bash
python3 harness/selftest.py
```

Expected output:

```json
{"expected":{"FC003":"STALE","FC008":"GREEN"},"observed":{"FC003":"STALE","FC008":"GREEN"},"status":"GREEN"}
```

The test demonstrates both sides of the control contract:

- **FC008 → GREEN**: a valid deterministic task is allowed to promote.
- **FC003 → STALE**: execution can succeed while promotion is correctly refused because repository state changed.

## Build all deterministic fixtures

```bash
python3 harness/build_fixtures.py --out generated_tasks
```

## Evaluate a candidate patch

```bash
python3 harness/evaluate_candidate.py \
  --task-dir generated_tasks/FC001 \
  --variant F_full_fabric \
  --candidate-patch /path/to/candidate.patch \
  --receipt-out attempt.json
```

Promotion is fail-closed: tests, stale-state checks and verification must all be GREEN.

## Empirical-status note

The A–F comparison is preregistered in `VARIANTS_V1.json`. This repository does **not** claim model-comparison results until corresponding receipts are published.
