#!/usr/bin/env python3
from __future__ import annotations

import copy
import unittest

from harness.agent_adapter_v1 import (
    ADAPTER_VERSION,
    AdapterContractError,
    normalize,
)


def valid():
    return {
        "task_id": "FC101",
        "variant": "external-pilot",
        "seed": 0,
        "adapter_id": "example.external-agent",
        "adapter_version": ADAPTER_VERSION,
        "repo_commit_before": "1" * 40,
        "repo_commit_after": "2" * 40,
        "proposed_patch_sha256": "a" * 64,
        "test_verdict": "GREEN",
        "stale_guard_verdict": "GREEN",
        "verifier_verdict": "GREEN",
        "promotion_verdict": "GREEN",
        "invalid_writes": 0,
        "duplicate_work": 0,
        "rollbacks": 0,
        "tool_calls": 7,
        "wall_seconds": 3.5,
        "model_latency_seconds": 1.2,
        "cost_usd": 0.0,
        "model_executed": True,
    }


class AdapterContractTests(unittest.TestCase):
    def test_valid_receipt_is_deterministic(self):
        a = normalize(valid())
        b = normalize(valid())
        self.assertEqual(a["receipt_sha256"], b["receipt_sha256"])

    def test_cost_does_not_control_promotion(self):
        value = valid()
        value["cost_usd"] = 999.0
        self.assertEqual(normalize(value)["promotion_verdict"], "GREEN")

    def test_latency_does_not_control_promotion(self):
        value = valid()
        value["model_latency_seconds"] = 9999.0
        self.assertEqual(normalize(value)["promotion_verdict"], "GREEN")

    def test_stale_cannot_promote(self):
        value = valid()
        value["stale_guard_verdict"] = "STALE"
        with self.assertRaises(AdapterContractError):
            normalize(value)

    def test_duplicate_work_cannot_promote(self):
        value = valid()
        value["duplicate_work"] = 1
        with self.assertRaises(AdapterContractError):
            normalize(value)

    def test_failed_verifier_cannot_promote(self):
        value = valid()
        value["verifier_verdict"] = "RED"
        with self.assertRaises(AdapterContractError):
            normalize(value)

    def test_invalid_write_cannot_promote(self):
        value = valid()
        value["invalid_writes"] = 1
        with self.assertRaises(AdapterContractError):
            normalize(value)

    def test_unknown_adapter_version_rejected(self):
        value = valid()
        value["adapter_version"] = "2.0.0"
        with self.assertRaises(AdapterContractError):
            normalize(value)

    def test_extra_field_rejected(self):
        value = valid()
        value["marketing_claim"] = "fastest"
        with self.assertRaises(AdapterContractError):
            normalize(value)

    def test_cost_must_be_nonnegative(self):
        value = valid()
        value["cost_usd"] = -0.01
        with self.assertRaises(AdapterContractError):
            normalize(value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
