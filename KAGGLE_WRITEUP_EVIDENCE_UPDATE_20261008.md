# Kaggle Writeup Addendum — verified control regression (2026-10-08)

**Status: publication-ready draft; NOT YET inserted into the Kaggle Writeup.**
This paragraph updates the implementation/reproducibility sections of the existing submitted draft. It must **not** be used as evidence of Gemma 4 model performance.

## Suggested paragraph (English, 131 words)

Beyond the original GREEN/STALE fixture self-tests and 48 deterministic A–F controller configurations, we implemented six stateful, model-independent Git control regressions. Each scenario executes on a fresh temporary repository and uses observable Git state rather than merely reading a scenario label. A clean candidate is verified in a shadow clone and promoted only after a nonblocking OS file lock and a Git HEAD compare-and-swap check. An intervening commit, contested writer lock, injected pre-promotion partial failure, hidden-invariant violation, and duplicate work identity are each rejected or skipped. Tests assert that canonical commits occur only in the allowed case and that rejected scenarios leave the canonical tree clean. All six regressions passed on the public GitHub Actions runner (run 37705925749). These are deliberately small synthetic control tests, **not** Gemma 4 inference, trained-agent evaluations, or measured A–F coding success rates. Real-model ablation remains future work.

## Supporting public evidence

- [Public regression source](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/blob/main/harness/stateful_promotion_v1.py)
- [Six-case scope and caveats](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/blob/main/STATEFUL_CONTROL_STATUS_V1.md)
- [First verified six-case CI run](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/actions/runs/37705925749)
- [Current validation boundaries](https://github.com/treining2016-oss/fail-closed-swe-agent-benchmark/blob/main/VALIDATION_STATUS.md)

When adding the paragraph, keep the total Kaggle Writeup at or below 3000 words. The Kaggle site requires a separately submitted Writeup to qualify; a public GitHub repository alone is not an entry.
