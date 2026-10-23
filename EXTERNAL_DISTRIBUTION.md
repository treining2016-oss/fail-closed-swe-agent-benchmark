# External Distribution and Ecosystem Signals

This file records externally reviewable distribution and ecosystem signals for the public benchmark. It intentionally separates verifiable usage from any claim of broad adoption.

## Kaggle dataset

Public dataset:

https://www.kaggle.com/datasets/malyshl67/fail-closed-swe-agent-benchmark

Title: **Fail-Closed SWE Agent Benchmark**

Kaggle subtitle: *Reliability benchmark for stale-safe verifier-gated coding agents.*

As of **2026-10-24**, the Kaggle public API reported:

- downloads: **43**
- views: **19**
- last updated: **2026-10-07T20:46:58.523Z**

These counts are external usage signals and will naturally change over time. They are **not** represented as broad adoption.

## Gemma 4 Developer Agent Paper Track context

The benchmark was prepared as a public reproducibility resource for the Google DeepMind-hosted **Gemma 4 Developer Agent Paper Track**:

https://www.kaggle.com/competitions/gemma-4-developer-agent-paper/overview

The project is relevant to the Track's software-engineering / agentic-learning context because it focuses on operational control failures that can occur in coding-agent workflows:

- stale repository state;
- conflicting writers;
- partial tool side effects;
- replay / duplicate work;
- hidden-invariant verification failures;
- unsafe promotion before verification.

This file does **not** claim that the benchmark has won, been endorsed by, or been selected by Google DeepMind, Kaggle, or OpenAI.

## Public project catalogue

A public project/publications page links both the Kaggle work and benchmark:

https://l67.ai/services/publications

## GitHub maintenance evidence

The canonical code repository is:

https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark

Current maintainer surfaces include:

- merged PR #1: maintainer/security/contribution/AGENTS/roadmap documentation;
- merged PR #3: public receipt validator and CI gate;
- open roadmap / external-maintainer issue #2;
- SECURITY.md;
- CONTRIBUTING.md;
- AGENTS.md;
- MAINTAINERS.md;
- recurring successful GitHub Actions self-tests.

The repository continues to distinguish **controller/self-test evidence** from any future model-performance evidence.
