# Current Results and Claim Boundaries

This repository separates **control-harness evidence** from **model-performance evidence**.

## What is verified now

The public control self-test is GREEN.

Observed public CI evidence:

- repository: `treining2016-oss/fail-closed-swe-agent-benchmark`
- workflow run: `37691690918`
- conclusion: `success`
- FC008 expected/observed: `GREEN`
- FC003 expected/observed: `STALE`

The corresponding machine-readable receipt is `PUBLIC_CI_EVIDENCE_V1.json`.

This verifies that the harness can:

1. promote an ordinary deterministic task when the required checks are GREEN; and
2. refuse promotion after an intervening repository change even when execution itself succeeds.

## What is **not** claimed yet

These control self-tests are **not** an empirical comparison of coding-model quality.

In particular, this repository does not yet claim measured A–F improvements in:

- issue pass rate;
- invalid mutations;
- stale promotions;
- duplicate work;
- rollback frequency;
- tool-call count;
- wall time.

Those claims remain preregistered until the corresponding attempt receipts exist.

## Preregistered model-ablation plan

The six variants are frozen in `VARIANTS_V1.json`:

- A — baseline direct agent
- B — + repository retrieval
- C — + read-only observer
- D — + stale-state and single-writer gates
- E — + independent verifier
- F — + continuity-aware handoff

For the model sweep, each task/variant run will use:

- immutable task baseline;
- fixed seed and budget;
- pinned environment;
- structured attempt receipt;
- candidate patch SHA-256;
- independent test/verifier verdicts;
- promotion verdict;
- invalid-write / duplicate-work / rollback counts;
- tool-call count and wall time.

No aggregate performance table will be published until the underlying receipts are available.

## Why this boundary matters

A fail-closed benchmark should apply its own rule to its paper claims:

> A result is not canonical because a process finished. It is canonical only when the evidence still matches the world and every predeclared gate passed.

This file therefore reports only evidence that is already independently reproducible.
