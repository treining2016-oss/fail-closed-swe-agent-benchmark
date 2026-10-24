# Codex Pilot Protocol V1

Status: **NOT YET EXECUTED**

This document freezes a reproducible first Codex maintenance experiment for this repository. It is intentionally published **before** the run so the acceptance criteria cannot be rewritten after seeing the result.

## Objective

Use Codex as a coding agent on one bounded open-source maintenance task while preserving the repository's fail-closed evidence boundary.

The pilot is not a model benchmark and will not be reported as a Codex performance result. Its purpose is to demonstrate a real, inspectable maintenance workflow with independent tests and durable receipts.

## Preconditions

- run from a fresh clone of the public repository;
- start from the then-current `main` SHA;
- create a dedicated branch; never write directly to `main`;
- use the existing repository test surface without weakening assertions;
- no secrets, private code, paid fallback, or hidden infrastructure;
- preserve negative outcomes exactly as observed.

## Frozen task

Codex receives the prompt in `codex_pilot_prompt_v1.txt`.

The task is to inspect the V1 external-agent adapter and its tests, then do **one** of the following:

1. identify a real missing fail-closed invariant and implement the smallest justified fix plus a negative test; or
2. if no defect is found, add one new adversarial regression test that exercises a meaningful boundary already promised by the contract.

Codex must not:
- relax a failing test;
- change a verdict merely to make CI green;
- invent third-party adoption or model-performance claims;
- edit unrelated files;
- merge its own work.

## Required evidence

Record, at minimum:

- base commit SHA;
- resulting commit SHA;
- exact files changed;
- patch SHA-256;
- test command(s) and exit status;
- Codex CLI version and authentication mode;
- wall-clock duration;
- whether a defect was found;
- whether human review changed or rejected the patch;
- final CI URL if a pull request is opened.

Operational metrics such as time or tool calls are evidence about the run, **not** correctness signals.

## Acceptance gates

The pilot is GREEN only if all are true:

- repository tests remain GREEN;
- the new or modified negative test is meaningful and deterministic;
- no stale-state, replay, duplicate-work, or verifier invariant is weakened;
- public claims match the observed run;
- a human-reviewed pull request is used before merge;
- GitHub Actions is GREEN.

A failed or unhelpful Codex attempt is still a valid pilot result and must be preserved.

## Publication boundary

Until a real run occurs, this repository claims only that the protocol is frozen and reproducible.

After the run, the result may be linked from this document with:
- the pull request;
- CI run;
- run receipt;
- a short postmortem including any rejected attempt.

No result should be described as representative of Codex generally from a single maintenance task.
