# Public Roadmap

This roadmap describes intended work, not completed results.

## v0.2 — external-maintainer readiness

- [ ] add one externally reproducible task fixture derived from a public OSS maintenance pattern;
- [ ] freeze a versioned agent/model adapter interface;
- [ ] publish a machine-readable receipt schema;
- [ ] add a replay corpus for duplicate-work and stale-state failures;
- [ ] document cost / latency fields without requiring paid inference for controller self-tests;
- [ ] solicit external maintainer feedback through GitHub Issues.

## v0.3 — bounded model evaluation

- [ ] freeze prompts, model identifiers, effort levels, budgets, seeds, and stop rules;
- [ ] run the preregistered A–F comparison on immutable per-attempt clones;
- [ ] preserve rejected attempts and negative results;
- [ ] publish aggregate analysis only after raw receipts are available.

## v1.0 criteria

A first stable release should require:
- reproducible controller CI;
- documented security and contribution process;
- at least one external-adopter or external-review cycle;
- versioned benchmark schema;
- published limitations;
- no unresolved contradiction between README claims and executable evidence.
