#!/usr/bin/env python3
"""Adversarial public-receipt validation tests. No models or API credits used."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from control_gate_simulation_v1 import evaluate
from stateful_promotion_v1 import run_all
from validate_public_receipts import (
    ValidationError, load_jsonl, validate_control, validate_stateful,
)


class ReceiptValidatorNegativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.control = evaluate()
        cls.stateful = run_all()

    def control_mutated(self) -> list[dict]:
        return copy.deepcopy(self.control)

    def stateful_mutated(self) -> list[dict]:
        return copy.deepcopy(self.stateful)

    def test_real_generator_receipts_pass(self):
        self.assertEqual(validate_control(self.control)["receipts"], 48)
        self.assertEqual(validate_stateful(self.stateful)["receipts"], 6)

    def test_control_rejects_missing_variant_task_pair(self):
        rows = self.control_mutated()[:-1]
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_duplicate_variant_task_pair(self):
        rows = self.control_mutated()
        rows[1] = copy.deepcopy(rows[0])
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_unknown_task(self):
        rows = self.control_mutated()
        rows[0]["task_id"] = "FC999"
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_boolean_string_oracle(self):
        rows = self.control_mutated()
        rows[0]["oracle_safe_to_promote"] = "false"
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_boolean_integer_false_promotion(self):
        rows = self.control_mutated()
        rows[0]["false_promotion_in_control_simulation"] = 0
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_scenario_flag_string(self):
        rows = self.control_mutated()
        rows[0]["scenario_flags"]["stale"] = "false"
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_rejection_without_reason(self):
        rows = self.control_mutated()
        rows[0]["verdict"] = "REJECT"
        rows[0]["reasons"] = []
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_full_fabric_false_promotion(self):
        rows = self.control_mutated()
        row = next(r for r in rows if r["variant"] == "F_full_fabric" and r["task_id"] == "FC003")
        row["verdict"] = "PROMOTE"
        row["reasons"] = []
        row["false_promotion_in_control_simulation"] = True
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_control_rejects_model_experiment_claim(self):
        rows = self.control_mutated()
        rows[0]["is_model_experiment"] = True
        with self.assertRaises(ValidationError):
            validate_control(rows)

    def test_stateful_rejects_missing_scenario(self):
        with self.assertRaises(ValidationError):
            validate_stateful(self.stateful_mutated()[:-1])

    def test_stateful_rejects_duplicate_scenario(self):
        rows = self.stateful_mutated()
        rows[1]["scenario"] = rows[0]["scenario"]
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_stateful_rejects_forged_expected_verdict(self):
        rows = self.stateful_mutated()
        row = next(r for r in rows if r["scenario"] == "FC003_stale_head")
        row["expected"] = row["observed"] = "GREEN"
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_stateful_rejects_string_false_canonical_mutation(self):
        rows = self.stateful_mutated()
        row = next(r for r in rows if r["scenario"] == "FC003_stale_head")
        row["canonical_mutation"] = "false"
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_stateful_rejects_wrong_head_transition(self):
        rows = self.stateful_mutated()
        row = next(r for r in rows if r["scenario"] == "FC003_stale_head")
        row["canonical_head_after"] = "a" * 40 if row["canonical_head_before"] != "a" * 40 else "b" * 40
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_stateful_rejects_fake_git_sha(self):
        rows = self.stateful_mutated()
        rows[0]["canonical_head_before"] = "not-a-sha"
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_stateful_rejects_dirty_canonical(self):
        rows = self.stateful_mutated()
        rows[0]["clean_canonical_after"] = "true"
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_stateful_rejects_model_run_claim(self):
        rows = self.stateful_mutated()
        rows[0]["model_executed"] = True
        with self.assertRaises(ValidationError):
            validate_stateful(rows)

    def test_parser_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text("{malformed\\n", encoding="utf8")
            with self.assertRaises(ValidationError):
                load_jsonl(path)

    def test_parser_rejects_empty_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.jsonl"
            path.write_text("", encoding="utf8")
            with self.assertRaises(ValidationError):
                load_jsonl(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
