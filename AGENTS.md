# AGENTS.md

This repository is a public benchmark for fail-closed software-engineering agent control.

## Goal
Improve the benchmark, fixtures, CI, documentation, or maintainer tooling without weakening fail-closed invariants or overstating evidence.

## Required verification
Before proposing a change that affects behavior, run:

```bash
python3 harness/selftest.py
python3 harness/control_gate_simulation_v1.py --output /tmp/fail-closed-control.jsonl
python3 harness/stateful_promotion_v1.py --output /tmp/fail-closed-stateful.jsonl
```

A successful controller test is not evidence of model coding quality. Do not convert synthetic control results into model-performance claims.

## Protected invariants
- immutable starting state per attempt;
- stale-state comparison before promotion;
- one canonical writer;
- independent verification before promotion;
- replay/duplicate-work rejection;
- durable evidence with explicit verdicts;
- GREEN-only canonical promotion;
- no silent mutation of benchmark definitions after results are observed.

## Agent workflow
1. Read `README.md` and `STATEFUL_CONTROL_STATUS_V1.md`.
2. State the intended change and its verification surface.
3. Make the smallest defensible patch.
4. Run the required verification.
5. Record limitations and negative results.
6. Prefer a pull request over direct-to-main mutation for nontrivial changes.

## Boundaries
Never add credentials, private prompts, private server topology, unpublished scientific material, or secrets from external systems. Keep public benchmark artifacts reproducible from the repository alone.
