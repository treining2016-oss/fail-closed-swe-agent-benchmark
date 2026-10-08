# Stateful fail-closed control regression — v1

This public resource is an executable **control-plane regression**, **not** a Gemma 4, model-quality, or A–F ablation result.

## Evidence

The new `harness/stateful_promotion_v1.py` runs six isolated temporary Git-repository cases. It uses a real `git rev-parse HEAD` compare-and-swap check, `fcntl.flock` nonblocking file lock, private shadow clone, public test invocation, an independent hidden assertion, a pre-promotion partial-failure injection, and durable replay identity.

| Case | Frozen expected outcome | Concrete check |
|---|---|---|
| FC001 clean patch | GREEN | Verify a candidate in a shadow clone and commit once under the lock after HEAD equality |
| FC003 stale HEAD | STALE | Intervening external commit changes the canonical HEAD; candidate is refused |
| FC004 writer conflict | RED_LOCKED | Separate descriptor already holds an OS exclusive lock |
| FC005 partial failure | RED_PARTIAL | Inject failure *before* applying the candidate; canonical HEAD stays identical |
| FC006 hidden invariant | RED_VERIFIER | Candidate passes the weak public test but fails a separate hidden safety assertion |
| FC007 duplicate replay | SKIP_ALREADY_DONE | A previously recorded work identity produces no new commit |

For each case, code checks the expected verdict, a clean canonical working tree, and whether a canonical commit happened **only** in the allowed case. The tool emits per-scenario JSONL receipts and prints `model_results_available: false`.

### How to reproduce

```bash
python3 harness/selftest.py
python3 harness/control_gate_simulation_v1.py --output /tmp/control.jsonl
python3 harness/stateful_promotion_v1.py --output /tmp/stateful.jsonl
```

Requirements: Python 3.10+, Git, a POSIX platform with `fcntl` (Linux GitHub Actions runner). No LLM, API key, card, or model weight is required.

Public GitHub Actions execution: [run 37705925749](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/actions/runs/37705925749), completed `success` on 2026-10-08 UTC. The run log includes `GREEN_STATEFUL_CONTROL_SELFTEST`, `scenarios: 6`, and `model_results_available: false`. The 48 original deterministic control toggles also remain GREEN.

## Important limits

- The six scenarios are deliberately tiny **synthetic fixtures**, not real-world repository bug-fix success rates.
- The writer-conflict case tests OS-level exclusive lock contention with two descriptors in one process; it is not a stress test with multiple distributed agents.
- Partial failure is injected at a single pre-promotion point, not at every possible crash boundary.
- Hidden validation checks a simple toy access-control condition; it is not a trained independent verifier.
- The method is a regression harness, not a hardened general-purpose patch publication library; `git` and filesystem power-loss atomicity are not formally established.
- No Gemma 4 inference, trained agents, stochastic repetitions, calibrated A–F resource comparison, or statistical model-performance conclusions have yet been run.

## Next preregistered gate

Freeze a real Gemma 4/agent adapter and task prompts, budgets, independent oracles, seeds and infrastructure. Execute actual A–F attempts on immutable per-attempt clones with raw receipts and rejected trials preserved. Aggregate performance only after those tests have run.

**No false GREEN:** a successful controller test must never be interpreted as proof of model effectiveness.
