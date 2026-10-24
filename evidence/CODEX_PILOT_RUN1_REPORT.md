# Codex Pilot Run 1 — task-ID schema alignment

**Status:** independently verified, not merged.

This is the first executed maintenance run under the preregistered Codex pilot. The protocol and exact prompt were made public before execution in PR #7.

## What Codex found

Codex identified a real contract mismatch:

- the public JSON Schema restricts `task_id` to `^FC[0-9A-Za-z._-]+$`;
- the Python adapter only checked `startswith("FC")` and minimum length;
- therefore a value such as `FC!!!` could pass Python validation while violating the public schema.

Codex changed only:

- `harness/agent_adapter_v1.py`
- `harness/test_agent_adapter_contract_v1.py`

The patch SHA-256 is:

`774b1024eaa359f45959f16a3e24f58a253d0f9b4b5a2918ed0b36b83fb95a8f`

## Codex verification

Codex first reproduced the missing rejection with a targeted regression. After the fix it reported:

- 31 unit/negative tests passed;
- controller self-test GREEN;
- 48 control receipts generated;
- six stateful promotion scenarios GREEN;
- public receipt validation GREEN;
- `git diff --check` PASS.

## Independent verification

The patch was then re-run independently outside the Codex session:

```bash
python3 -m unittest -v harness/test_agent_adapter_contract_v1.py harness/test_receipt_validator_negative.py
python3 harness/selftest.py
python3 harness/control_gate_simulation_v1.py --output /tmp/codex-pilot-control.jsonl
python3 harness/stateful_promotion_v1.py --output /tmp/codex-pilot-stateful.jsonl
python3 harness/validate_public_receipts.py --control /tmp/codex-pilot-control.jsonl --stateful /tmp/codex-pilot-stateful.jsonl
git diff --check
```

Result: **31/31 PASS**, controller self-test GREEN, 48 control receipts, six stateful scenarios GREEN, public receipt validation GREEN, and clean diff formatting.

## Evidence boundary

This is one bounded maintenance task. It is **not** evidence of general Codex model quality or benchmark performance. It does not claim third-party adoption or endorsement.

Human maintainer review and merge are still pending.
