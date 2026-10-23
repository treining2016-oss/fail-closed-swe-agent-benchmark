# Fail-Closed SWE Agent Benchmark

[![Public benchmark self-test](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/actions/workflows/selftest.yml/badge.svg)](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/actions/workflows/selftest.yml)

Public reproducibility resource for fail-closed software-engineering agent control, originally prepared for the **Google – The Gemma 4 Developer Agent Paper Track**.

## Why OSS maintainers may care

Coding-agent failures are not limited to model capability. Maintainers also face operational risks around stale repository state, concurrent writers, partial tool effects, duplicate work after retries or session rollover, and promotion before independent verification. These failure modes can matter in pull-request review, automated maintenance, release preparation, and security remediation.

This repository turns those control-plane risks into small, reproducible fixtures that require no private infrastructure or paid model access for the controller self-tests. It is intended as a public test surface that other maintainers can adapt when evaluating agentic maintenance workflows.

**No adoption claim:** the project does not currently claim broad usage, download volume, or model-quality results. Ecosystem relevance is the problem class and reproducible control surface, not a fabricated popularity metric.

## What this measures

Coding agents can fail even when the underlying model is capable. Long-running repository repair introduces operational failure modes such as:

- stale repository state;
- conflicting writers;
- duplicate work after session rollover;
- partial tool side effects;
- superficially plausible patches that violate hidden invariants;
- promotion of a result before independent verification.

This benchmark studies whether a **fail-closed control architecture** improves reliability independently of raw model capability.

## Architecture under study

1. **Observer** — read-only reconstruction of repository and work state.
2. **Executor** — bounded mutation against a pinned starting state.
3. **Verifier** — tests, invariants, stale checks and evidence validation.
4. **Promotion gate** — single-writer, atomic, GREEN-only canonical promotion.

Core rule:

> An agent result is not canonical because it finished. It becomes canonical only when the evidence still matches the world and every predeclared gate passed.

## Task classes

The benchmark preregisters eight deterministic classes:

- FC001 — single-file bug repair
- FC002 — multi-file API consistency
- FC003 — stale repository state
- FC004 — conflicting writer
- FC005 — partial tool side effect
- FC006 — plausible patch rejected by a hidden invariant
- FC007 — session rollover without duplicate work
- FC008 — dependency-aware repository navigation

## Ablations

- **A** baseline
- **B** + retrieval
- **C** + read-only observer
- **D** + stale-state / single-writer gate
- **E** + independent verifier
- **F** full fabric + continuity-aware handoff

## Reproducibility contract

Each attempt emits a structured receipt containing:

- task / variant / seed
- repository commits before and after
- candidate patch SHA-256
- test verdict
- stale-guard verdict
- verifier verdict
- promotion verdict
- invalid-write, duplicate-work and rollback counts
- tool-call count and wall time

Attempts run on **fresh clones of immutable baselines** so one attempt cannot contaminate another.

## Quick control self-test

```bash
python3 harness/selftest.py
```

Expected:

- FC008 → **GREEN**
- FC003 → **STALE**

The self-test uses only Python standard library + Git.

## Stateful control regression

In addition to the 48 deterministic A–F controller flag simulations, an independent [six-case Git state/lock/verification/replay test](STATEFUL_CONTROL_STATUS_V1.md) is exercised in public CI. [Verified run 37705925749](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/actions/runs/37705925749) was successful. It measures failure handling of synthetic control fixtures, **not** model coding ability.

## Maintainer workflow

The repository now documents the same surfaces used in real OSS maintenance:

- [AGENTS.md](AGENTS.md) — bounded agent instructions and required verification;
- [CONTRIBUTING.md](CONTRIBUTING.md) — issue/PR expectations and test discipline;
- [SECURITY.md](SECURITY.md) — responsible vulnerability reporting and security scope;
- [MAINTAINERS.md](MAINTAINERS.md) — primary-maintainer responsibilities and review policy;
- [ROADMAP.md](ROADMAP.md) — public external-maintainer and model-evaluation milestones.

Pull requests run the public controller tests before merge. Nontrivial changes are expected to preserve negative results and explicit limitations rather than optimize only for a GREEN outcome.

## Current empirical status

The control harness is implemented and self-tested. The full A–F model comparison remains preregistered. No model-performance claim should be inferred until the corresponding receipts are published.

## Scope

This repository intentionally excludes private prompts, credentials, private server topology, private repositories, and unpublished scientific material.
