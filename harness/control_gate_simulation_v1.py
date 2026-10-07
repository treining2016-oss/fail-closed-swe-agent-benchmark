#!/usr/bin/env python3
"""Deterministic CONTROL-LOGIC simulation, explicitly NOT a Gemma/model benchmark.

The A-F flags change the promotion controller. This script does not generate
patches or call an LLM. Results may not be reported as model success rates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = json.loads((ROOT / "VARIANTS_V1.json").read_text())
TASKS = {
    "FC001": dict(stale=False, conflict=False, partial=False, invalid=False, duplicate=False),
    "FC002": dict(stale=False, conflict=False, partial=False, invalid=False, duplicate=False),
    "FC003": dict(stale=True, conflict=False, partial=False, invalid=False, duplicate=False),
    "FC004": dict(stale=False, conflict=True, partial=False, invalid=False, duplicate=False),
    "FC005": dict(stale=False, conflict=False, partial=True, invalid=False, duplicate=False),
    "FC006": dict(stale=False, conflict=False, partial=False, invalid=True, duplicate=False),
    "FC007": dict(stale=False, conflict=False, partial=False, invalid=False, duplicate=True),
    "FC008": dict(stale=False, conflict=False, partial=False, invalid=False, duplicate=False),
}

SCHEMA = "FAIL_CLOSED_CONTROL_SIMULATION_V1__NOT_MODEL_RESULTS"


def gate(variant: str, task_id: str, seed: int = 0) -> dict:
    assert variant in VARIANTS, variant
    assert task_id in TASKS, task_id
    v, t = VARIANTS[variant], TASKS[task_id]
    # Reading an upstream repo/commit snapshot is always the input to this
    # deterministic test; only enabled protections may reject promotion.
    stale_enabled = bool(v.get("stale_gate", False))
    writer_enabled = bool(v.get("atomic_promotion", False))
    verifier_enabled = bool(v.get("verifier", False))
    continuity_enabled = bool(v.get("continuity_handoff", False))

    reasons = []
    if stale_enabled and t["stale"]:
        reasons.append("STALE_STATE")
    if writer_enabled and t["conflict"]:
        reasons.append("SINGLE_WRITER_CONFLICT")
    if writer_enabled and t["partial"]:
        reasons.append("PARTIAL_EFFECT_NONATOMIC")
    if verifier_enabled and t["invalid"]:
        reasons.append("INDEPENDENT_VERIFIER_REJECT")
    if continuity_enabled and t["duplicate"]:
        reasons.append("ALREADY_DONE_NO_REPLAY")

    verdict = "REJECT" if reasons else "PROMOTE"
    actually_safe = not any(t.values())
    return {
        "schema": SCHEMA,
        "variant": variant,
        "task_id": task_id,
        "seed_label": seed,
        "scenario_flags": t,
        "gate_flags": {
            "stale_guard": stale_enabled,
            "single_writer_atomic": writer_enabled,
            "independent_verifier": verifier_enabled,
            "continuity_handoff": continuity_enabled,
        },
        "verdict": verdict,
        "reasons": reasons,
        "oracle_safe_to_promote": actually_safe,
        "false_promotion_in_control_simulation": verdict == "PROMOTE" and not actually_safe,
        "is_model_experiment": False,
        "is_agent_patch_attempt": False,
    }


def evaluate() -> list[dict]:
    return [gate(v, t) for v in sorted(VARIANTS) for t in sorted(TASKS)]


def selftest(rows: list[dict]) -> None:
    assert len(rows) == 48, len(rows)
    assert len({(r["variant"], r["task_id"]) for r in rows}) == 48
    by_key = {(r["variant"], r["task_id"]): r for r in rows}
    assert by_key["A_baseline", "FC003"]["false_promotion_in_control_simulation"]
    assert by_key["D_stale_safe", "FC003"]["verdict"] == "REJECT"
    assert by_key["D_stale_safe", "FC004"]["verdict"] == "REJECT"
    assert by_key["D_stale_safe", "FC005"]["verdict"] == "REJECT"
    assert by_key["D_stale_safe", "FC006"]["verdict"] == "PROMOTE"
    assert by_key["E_verifier", "FC006"]["verdict"] == "REJECT"
    assert by_key["E_verifier", "FC007"]["verdict"] == "PROMOTE"
    assert by_key["F_full_fabric", "FC007"]["verdict"] == "REJECT"
    assert not any(r["false_promotion_in_control_simulation"]
                   for r in rows if r["variant"] == "F_full_fabric")
    assert all(r["is_model_experiment"] is False for r in rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", help="Write public-safe JSONL simulation receipts")
    args = ap.parse_args()
    rows = evaluate()
    selftest(rows)
    payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload)
    print(json.dumps({
        "schema": SCHEMA,
        "status": "GREEN_CONTROL_SELFTEST",
        "receipts": len(rows),
        "sha256": digest,
        "model_results_available": False,
        "warning": "Deterministic controller simulation; no LLM was evaluated.",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
