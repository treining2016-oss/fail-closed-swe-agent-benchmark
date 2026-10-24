# External Agent Adapter Protocol V1

`harness/agent_adapter_v1.py` freezes the first public adapter boundary for bringing an external coding agent or model runner into the benchmark.

## Contract

An external runner may use any model, tool stack, or provider. The benchmark only accepts the normalized fields defined by `AgentAttempt` and `schemas/agent_attempt_receipt_v1.schema.json`.

The adapter deliberately keeps **controller correctness** separate from **operational metrics**:

- correctness: tests, stale guard, independent verifier, invalid writes, duplicate work, promotion verdict;
- operations: wall time, model latency, tool calls, cost;
- provenance: adapter id/version, before/after commits, proposed patch SHA-256.

A cheap or fast attempt is not more correct. A costly or slow attempt is not less correct. Promotion remains fail-closed.

## Promotion rule

`promotion_verdict=GREEN` is valid only when:

- tests are GREEN;
- stale guard is GREEN;
- independent verifier is GREEN;
- invalid writes = 0;
- duplicate work = 0.

A stale attempt or an attempt with duplicate work cannot be promoted.

## Reusable external-maintainer fixtures

`fixtures/external_maintainer_patterns_v1.json` contains synthetic fixtures derived from public OSS maintenance patterns. They copy no third-party source code. The repository links are provenance for the kind of maintenance surface being modeled, not claims that those projects adopted or endorsed this benchmark.

## External pilot

A maintainer can:

1. choose one fixture;
2. run an external agent against a fresh clone;
3. map the result into `AgentAttempt`;
4. run `validate_attempt()`;
5. publish the normalized receipt and negative results;
6. open an issue or PR with feedback.

The benchmark still has **no completed external-maintainer review** until a third party actually performs one.
