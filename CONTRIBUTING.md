# Contributing

Contributions that improve reproducibility, fail-closed controls, fixtures, CI, documentation, or independent verification are welcome.

## Before opening a PR

1. Read `README.md`, `AGENTS.md`, and `STATEFUL_CONTROL_STATUS_V1.md`.
2. Keep the change narrowly scoped.
3. Do not add secrets or private infrastructure details.
4. Do not claim model-performance results unless the corresponding immutable receipts exist in the public repository.

## Verification

For behavioral changes run:

```bash
python3 harness/selftest.py
python3 harness/control_gate_simulation_v1.py --output /tmp/fail-closed-control.jsonl
python3 harness/stateful_promotion_v1.py --output /tmp/fail-closed-stateful.jsonl
```

The GitHub Actions workflow runs the public self-tests on pushes and pull requests.

## Pull requests

A useful PR should state:
- problem being solved;
- files changed;
- fail-closed invariant affected, if any;
- commands run;
- observed result;
- known limitation or negative result.

Changes that weaken stale-state checks, replay rejection, single-writer behavior, independent verification, or GREEN-only promotion should be rejected unless the benchmark definition itself is explicitly being revised and re-preregistered.

## Issues

Use issues for reproducible bugs, benchmark-design proposals, external-adopter feedback, and roadmap work. Sensitive security reports should follow `SECURITY.md`.
