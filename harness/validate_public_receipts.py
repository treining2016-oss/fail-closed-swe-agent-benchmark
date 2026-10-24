#!/usr/bin/env python3
"""Fail-closed validation of public controller receipts (not model results).

Every expected record and field is checked for strict types and completeness.
The tool deliberately rejects malformed or incomplete data rather than
converting strings/integers into truth values.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

CONTROL_SCHEMA = "FAIL_CLOSED_CONTROL_SIMULATION_V1__NOT_MODEL_RESULTS"
STATEFUL_SCHEMA = "FAIL_CLOSED_STATEFUL_PROMOTION_V1__NOT_MODEL_RESULTS"
VARIANTS = {
    "A_baseline", "B_retrieval", "C_observer",
    "D_stale_safe", "E_verifier", "F_full_fabric",
}
TASKS = {f"FC{i:03}" for i in range(1, 9)}
SCENARIO_FLAGS = {"stale", "conflict", "partial", "invalid", "duplicate"}
GATE_FLAGS = {
    "stale_guard", "single_writer_atomic",
    "independent_verifier", "continuity_handoff",
}
REJECTION_REASONS = {
    "STALE_STATE", "SINGLE_WRITER_CONFLICT", "PARTIAL_EFFECT_NONATOMIC",
    "INDEPENDENT_VERIFIER_REJECT", "ALREADY_DONE_NO_REPLAY",
}
STATEFUL_VERDICTS = {
    "FC001_clean_patch": "GREEN",
    "FC003_stale_head": "STALE",
    "FC004_writer_conflict": "RED_LOCKED",
    "FC005_partial_failure": "RED_PARTIAL",
    "FC006_hidden_invariant": "RED_VERIFIER",
    "FC007_duplicate_replay": "SKIP_ALREADY_DONE",
}
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


class ValidationError(RuntimeError):
    pass


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValidationError(f"{path}:{line_no}: receipt is not an object")
        rows.append(row)
    if not rows:
        raise ValidationError(f"{path}: no receipts")
    return rows


def need(row: dict, fields: set[str], label: str) -> None:
    missing = sorted(fields - row.keys())
    if missing:
        raise ValidationError(f"{label}: missing fields: {', '.join(missing)}")


def boolean(value: object, label: str) -> bool:
    if type(value) is not bool:
        raise ValidationError(f"{label}: expected JSON boolean")
    return value


def flags(value: object, expected: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValidationError(f"{label}: missing/extra flag keys")
    for field, field_value in value.items():
        boolean(field_value, f"{label}.{field}")
    return value


def validate_control(rows: list[dict]) -> dict:
    required = {
        "schema", "variant", "task_id", "seed_label", "scenario_flags",
        "gate_flags", "verdict", "reasons", "oracle_safe_to_promote",
        "false_promotion_in_control_simulation", "is_model_experiment",
        "is_agent_patch_attempt",
    }
    seen: set[tuple[str, str]] = set()
    false_promotions = 0
    for i, row in enumerate(rows, 1):
        label = f"control[{i}]"
        need(row, required, label)
        if row["schema"] != CONTROL_SCHEMA:
            raise ValidationError(f"{label}: unexpected schema")
        if row["variant"] not in VARIANTS or row["task_id"] not in TASKS:
            raise ValidationError(f"{label}: unknown variant/task")
        if type(row["seed_label"]) is not int or row["seed_label"] < 0:
            raise ValidationError(f"{label}: seed_label must be nonnegative integer")
        scenario = flags(row["scenario_flags"], SCENARIO_FLAGS, f"{label}.scenario_flags")
        flags(row["gate_flags"], GATE_FLAGS, f"{label}.gate_flags")
        if row["verdict"] not in {"PROMOTE", "REJECT"}:
            raise ValidationError(f"{label}: invalid verdict {row['verdict']!r}")
        reasons = row["reasons"]
        if (not isinstance(reasons, list)
                or any(not isinstance(reason, str) or reason not in REJECTION_REASONS for reason in reasons)
                or len(set(reasons)) != len(reasons)):
            raise ValidationError(f"{label}: invalid reasons")
        if (row["verdict"] == "REJECT") != bool(reasons):
            raise ValidationError(f"{label}: verdict/reasons mismatch")
        oracle = boolean(row["oracle_safe_to_promote"], f"{label}.oracle")
        flag = boolean(
            row["false_promotion_in_control_simulation"],
            f"{label}.false_promotion",
        )
        if oracle != (not any(scenario.values())):
            raise ValidationError(f"{label}: oracle contradicts scenario flags")
        if boolean(row["is_model_experiment"], f"{label}.model") is not False:
            raise ValidationError(f"{label}: model-experiment claim boundary violated")
        if boolean(row["is_agent_patch_attempt"], f"{label}.agent") is not False:
            raise ValidationError(f"{label}: agent-patch claim boundary violated")
        expected_false = row["verdict"] == "PROMOTE" and not oracle
        if flag is not expected_false:
            raise ValidationError(f"{label}: false-promotion flag inconsistent")
        key = (row["variant"], row["task_id"])
        if key in seen:
            raise ValidationError(f"{label}: duplicate variant/task pair {key}")
        seen.add(key)
        false_promotions += int(flag)

    expected_pairs = {(variant, task) for variant in VARIANTS for task in TASKS}
    if seen != expected_pairs:
        raise ValidationError(
            f"control: missing/extra variant-task pairs; "
            f"missing={sorted(expected_pairs - seen)} extra={sorted(seen - expected_pairs)}"
        )
    full_fabric = [r for r in rows if r["variant"] == "F_full_fabric"]
    if any(r["false_promotion_in_control_simulation"] for r in full_fabric):
        raise ValidationError("control: F_full_fabric contains a false promotion")

    return {
        "schema": CONTROL_SCHEMA,
        "receipts": len(rows),
        "unique_variant_task_pairs": len(seen),
        "false_promotions_in_all_variants": false_promotions,
        "full_fabric_false_promotions": 0,
    }


def validate_stateful(rows: list[dict]) -> dict:
    required = {
        "schema", "scenario", "expected", "observed",
        "canonical_head_before", "canonical_head_after",
        "canonical_mutation", "clean_canonical_after",
        "model_executed", "variant_ablation_executed",
    }
    seen: set[str] = set()
    for i, row in enumerate(rows, 1):
        label = f"stateful[{i}]"
        need(row, required, label)
        if row["schema"] != STATEFUL_SCHEMA:
            raise ValidationError(f"{label}: unexpected schema")
        scenario = row["scenario"]
        if scenario not in STATEFUL_VERDICTS:
            raise ValidationError(f"{label}: unknown scenario")
        if scenario in seen:
            raise ValidationError(f"{label}: duplicate scenario {scenario}")
        seen.add(scenario)
        expected_verdict = STATEFUL_VERDICTS[scenario]
        if row["expected"] != expected_verdict or row["observed"] != expected_verdict:
            raise ValidationError(f"{label}: verdict differs from scenario contract")
        before, after = row["canonical_head_before"], row["canonical_head_after"]
        if (not isinstance(before, str) or not SHA40.fullmatch(before)
                or not isinstance(after, str) or not SHA40.fullmatch(after)):
            raise ValidationError(f"{label}: malformed Git HEAD SHA")
        mutation = boolean(row["canonical_mutation"], f"{label}.canonical_mutation")
        if boolean(row["clean_canonical_after"], f"{label}.clean") is not True:
            raise ValidationError(f"{label}: canonical repository not clean")
        if boolean(row["model_executed"], f"{label}.model") is not False:
            raise ValidationError(f"{label}: model-execution claim boundary violated")
        if boolean(row["variant_ablation_executed"], f"{label}.ablation") is not False:
            raise ValidationError(f"{label}: variant-ablation claim boundary violated")
        if mutation is not (expected_verdict == "GREEN"):
            raise ValidationError(f"{label}: forbidden canonical mutation")
        if (before != after) is not mutation:
            raise ValidationError(f"{label}: Git HEAD transition inconsistent")
    if seen != set(STATEFUL_VERDICTS):
        raise ValidationError(
            f"stateful: missing scenarios {sorted(set(STATEFUL_VERDICTS) - seen)}"
        )
    return {
        "schema": STATEFUL_SCHEMA,
        "receipts": len(rows),
        "scenarios": sorted(seen),
        "no_false_promotions": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True, type=Path)
    ap.add_argument("--stateful", required=True, type=Path)
    args = ap.parse_args()
    try:
        control = validate_control(load_jsonl(args.control))
        stateful = validate_stateful(load_jsonl(args.stateful))
    except (ValidationError, OSError) as exc:
        print(json.dumps({
            "schema": "FAIL_CLOSED_PUBLIC_RECEIPT_VALIDATION_V1",
            "status": "RED",
            "error": str(exc),
            "model_results_available": False,
        }, sort_keys=True))
        return 1
    print(json.dumps({
        "schema": "FAIL_CLOSED_PUBLIC_RECEIPT_VALIDATION_V1",
        "status": "GREEN_PUBLIC_RECEIPTS_VALIDATED",
        "control": control,
        "stateful": stateful,
        "model_results_available": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
