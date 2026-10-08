# Experimental status and claims boundary

This repository contains **three distinct kinds of executable control tests** and a preregistered, **not yet executed** coding-model comparison. They must not be conflated.

## Verified

1. `python3 harness/selftest.py` builds isolated Git fixtures and checks the controller's expected GREEN / STALE outcomes.
2. `python3 harness/control_gate_simulation_v1.py` executes 48 deterministic controller-scenario evaluations (8 scenario flags × 6 A–F gate configurations) and self-checks the selected promotion rules.
3. `python3 harness/stateful_promotion_v1.py` executes **six isolated stateful Git/filesystem regression scenarios** (actual HEAD comparisons, OS lock contention, shadow clone, hidden verifier and replay suppression). See [the evidence and limitations](STATEFUL_CONTROL_STATUS_V1.md).
4. GitHub Actions runs all three commands; [run 37705925749](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/actions/runs/37705925749) completed successfully.

**None of the three control tests is a Gemma inference run, coding-agent trial, measured repair improvement, or comparison of different model capabilities.** It has no stochastic seed effect or model generated patches.

## Unverified / incomplete

- The legacy `harness/evaluate_candidate.py` accepts `--variant` as an output label. It **does not** configure a model, retriever, observer, or A–F runtime. Its receipt must not be treated as evidence of an A–F model ablation.
- The eight task classes are presently small public-safe fixtures. Several listed failure modes need stronger injections and oracle tests before interpreting benchmark-wide empirical claims.
- An independent model/agent adapter with frozen prompts, tool budgets, temperatures, seeds, and environment has not yet been provided.
- No supported result claims for Gemma A versus F success rate, invalid-mutation reduction, speed, token cost, or prize win probability are available.

## Next acceptance gates

1. Implement independently testable agent adapters for the six preregistered control configurations (no fake variants).
2. Freeze tasks, repository versions, patch oracle, model version, seed policy, token/tool budgets and infrastructure before model evaluations.
3. Demonstrate negative controls: stale commits, conflicting writers, partial effects and hidden invariant violations must be detected by the intended gates, not inferred from labels.
4. Run and publish raw per-attempt receipts, failed and aborted attempts, baseline comparisons, statistical uncertainty, runtime and cost.
5. Only then update the Kaggle paper with an empirical results table.

**No false GREEN:** the public controller test is GREEN; the full model-based A–F scientific claim is OPEN.
