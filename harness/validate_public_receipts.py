#!/usr/bin/env python3
"""Validate public control receipts without third-party dependencies.

This validator checks only repository-public controller receipts. It does not
interpret them as model-performance evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

CONTROL_SCHEMA = "FAIL_CLOSED_CONTROL_SIMULATION_V1__NOT_MODEL_RESULTS"
STATEFUL_SCHEMA = "FAIL_CLOSED_STATEFUL_PROMOTION_V1__NOT_MODEL_RESULTS"


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
        if row["verdict"] not in {"PROMOTE", "REJECT"}:
            raise ValidationError(f"{label}: invalid verdict {row['verdict']!r}")
        if not isinstance(row["reasons"], list):
            raise ValidationError(f"{label}: reasons must be a list")
        if not isinstance(row["scenario_flags"], dict) or not isinstance(row["gate_flags"], dict):
            raise ValidationError(f"{label}: flags must be objects")
        if row["is_model_experiment"] is not False or row["is_agent_patch_attempt"] is not False:
            raise ValidationError(f"{label}: model/agent claim boundary violated")
        expected_false = row["verdict"] == "PROMOTE" and not bool(row["oracle_safe_to_promote"])
        if row["false_promotion_in_control_simulation"] is not expected_false:
            raise ValidationError(f"{label}: false-promotion flag inconsistent")
        key = (str(row["variant"]), str(row["task_id"]))
        if key in seen:
            raise ValidationError(f"{label}: duplicate variant/task pair {key}")
        seen.add(key)
        false_promotions += int(bool(row["false_promotion_in_control_simulation"]))

    full_fabric = [r for r in rows if r["variant"] == "F_full_fabric"]
    if not full_fabric:
        raise ValidationError("control: no F_full_fabric receipts")
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
        scenario = str(row["scenario"])
        if scenario in seen:
            raise ValidationError(f"{label}: duplicate scenario {scenario}")
        seen.add(scenario)
        if row["expected"] != row["observed"]:
            raise ValidationError(
                f"{label}: expected {row['expected']!r}, observed {row['observed']!r}"
            )
        if row["clean_canonical_after"] is not True:
            raise ValidationError(f"{label}: canonical repository not clean")
        if row["model_executed"] is not False or row["variant_ablation_executed"] is not False:
            raise ValidationError(f"{label}: model/ablation claim boundary violated")
        expected_mutation = row["expected"] == "GREEN"
        if bool(row["canonical_mutation"]) is not expected_mutation:
            raise ValidationError(f"{label}: canonical mutation does not match expected verdict")
        heads_differ = row["canonical_head_before"] != row["canonical_head_after"]
        if heads_differ is not bool(row["canonical_mutation"]):
            raise ValidationError(f"{label}: head transition inconsistent with mutation flag")

    required_scenarios = {
        "FC001_clean_patch",
        "FC003_stale_head",
        "FC004_writer_conflict",
        "FC005_partial_failure",
        "FC006_hidden_invariant",
        "FC007_duplicate_replay",
    }
    if seen != required_scenarios:
        missing = sorted(required_scenarios - seen)
        extra = sorted(seen - required_scenarios)
        raise ValidationError(f"stateful: scenario set mismatch missing={missing} extra={extra}")

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
    except ValidationError as exc:
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
