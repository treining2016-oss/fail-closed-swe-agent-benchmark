#!/usr/bin/env python3
"""Versioned fail-closed adapter contract for external coding agents.

The adapter normalizes controller evidence. It does not execute a model and it
never treats cost/latency as correctness evidence.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from typing import Any

SCHEMA = "FAIL_CLOSED_AGENT_ADAPTER_V1"
ADAPTER_VERSION = "1.0.0"
VERDICTS = {"GREEN", "RED", "SKIP", "STALE"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


class AdapterContractError(ValueError):
    pass


@dataclass(frozen=True)
class AgentAttempt:
    task_id: str
    variant: str
    seed: int
    adapter_id: str
    adapter_version: str
    repo_commit_before: str
    repo_commit_after: str
    proposed_patch_sha256: str
    test_verdict: str
    stale_guard_verdict: str
    verifier_verdict: str
    promotion_verdict: str
    invalid_writes: int
    duplicate_work: int
    rollbacks: int
    tool_calls: int
    wall_seconds: float
    model_latency_seconds: float | None
    cost_usd: float | None
    model_executed: bool

    def to_receipt(self) -> dict[str, Any]:
        payload = {"schema": SCHEMA, **asdict(self)}
        payload["receipt_sha256"] = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return payload


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise AdapterContractError(message)


def validate_attempt(a: AgentAttempt) -> None:
    _need(a.adapter_version == ADAPTER_VERSION, "unsupported adapter_version")
    _need(a.task_id.startswith("FC") and len(a.task_id) >= 5, "invalid task_id")
    _need(bool(a.variant.strip()), "empty variant")
    _need(type(a.seed) is int and a.seed >= 0, "seed must be a nonnegative integer")
    _need(bool(a.adapter_id.strip()), "empty adapter_id")
    _need(SHA40.fullmatch(a.repo_commit_before) is not None, "invalid repo_commit_before")
    _need(SHA40.fullmatch(a.repo_commit_after) is not None, "invalid repo_commit_after")
    _need(SHA64.fullmatch(a.proposed_patch_sha256) is not None, "invalid proposed_patch_sha256")

    for field in ("test_verdict", "stale_guard_verdict", "verifier_verdict", "promotion_verdict"):
        _need(getattr(a, field) in VERDICTS, f"invalid {field}")

    for field in ("invalid_writes", "duplicate_work", "rollbacks", "tool_calls"):
        value = getattr(a, field)
        _need(type(value) is int and value >= 0, f"{field} must be a nonnegative integer")

    _need(type(a.wall_seconds) in (int, float) and a.wall_seconds >= 0, "invalid wall_seconds")
    if a.model_latency_seconds is not None:
        _need(type(a.model_latency_seconds) in (int, float) and a.model_latency_seconds >= 0,
              "invalid model_latency_seconds")
    if a.cost_usd is not None:
        _need(type(a.cost_usd) in (int, float) and a.cost_usd >= 0, "invalid cost_usd")
    _need(type(a.model_executed) is bool, "model_executed must be a JSON boolean")

    green_inputs = (
        a.test_verdict == "GREEN"
        and a.stale_guard_verdict == "GREEN"
        and a.verifier_verdict == "GREEN"
        and a.invalid_writes == 0
        and a.duplicate_work == 0
    )
    if a.promotion_verdict == "GREEN":
        _need(green_inputs, "GREEN promotion without all controller gates")
    if a.stale_guard_verdict == "STALE":
        _need(a.promotion_verdict != "GREEN", "stale attempt cannot promote")
    if a.duplicate_work > 0:
        _need(a.promotion_verdict != "GREEN", "duplicate work cannot promote")


def from_mapping(value: dict[str, Any]) -> AgentAttempt:
    expected = set(AgentAttempt.__dataclass_fields__)
    _need(set(value) == expected, "missing or extra adapter fields")
    attempt = AgentAttempt(**value)
    validate_attempt(attempt)
    return attempt


def normalize(value: dict[str, Any]) -> dict[str, Any]:
    """Validate an external-agent envelope and emit a deterministic receipt."""
    return from_mapping(value).to_receipt()
