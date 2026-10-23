# Maintainers

## Primary maintainer

**Oleg Zigangirov** — GitHub: [@treining2016-oss](https://github.com/treining2016-oss)

The primary maintainer currently owns repository administration, issue triage, pull-request review, CI/reproducibility checks, benchmark-definition changes, and release/promotion decisions.

## Maintainer responsibilities

- keep the public benchmark runnable without private infrastructure;
- triage reproducible failures and external feedback;
- review PRs for fail-closed invariant regressions;
- preserve immutable evidence and negative results;
- keep CI and documentation aligned with the executable harness;
- reject unsupported performance claims;
- maintain security-reporting guidance;
- record benchmark-definition changes before using them for new results.

## Review policy

Nontrivial changes should use a pull request and pass the public verification commands. Changes to benchmark definitions, task classes, gates, or model-evaluation methodology require explicit documentation of the new version and should not be retroactively applied to previously published receipts.

## Current maintenance status

The repository is actively maintained. The controller harness and stateful Git regression are implemented; the full model A–F comparison remains deliberately unclaimed until actual model receipts are published.
