#!/usr/bin/env python3
"""Stateful Git/filesystem fail-closed regression; NOT a model evaluation.

Six independent fixtures exercise actual Git HEAD compare-and-swap, OS file
locks, shadow verification, injected partial failure, and replay suppression.
Results must never be presented as Gemma or A--F model comparison.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCHEMA = "FAIL_CLOSED_STATEFUL_PROMOTION_V1__NOT_MODEL_RESULTS"
CASES = (
    ("FC001_clean_patch", "GREEN"),
    ("FC003_stale_head", "STALE"),
    ("FC004_writer_conflict", "RED_LOCKED"),
    ("FC005_partial_failure", "RED_PARTIAL"),
    ("FC006_hidden_invariant", "RED_VERIFIER"),
    ("FC007_duplicate_replay", "SKIP_ALREADY_DONE"),
)


def cmd(argv: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, check=check, capture_output=True, text=True, timeout=30)


def head(repo: Path) -> str:
    return cmd(["git", "rev-parse", "HEAD"], repo).stdout.strip()


def clean(repo: Path) -> bool:
    return not cmd(["git", "status", "--porcelain"], repo).stdout.strip()


def commit(repo: Path, message: str) -> None:
    cmd(["git", "add", "-A"], repo)
    cmd(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", message], repo)


def setup(root: Path, tag: str) -> Path:
    repo = root / tag / "canonical"
    repo.mkdir(parents=True)
    cmd(["git", "init", "-q"], repo)
    (repo / "app.py").write_text("def allowed(role):\n    return False\n", encoding="utf8")
    (repo / "test_public.py").write_text(
        "import unittest\nfrom app import allowed\n"
        "class Public(unittest.TestCase):\n"
        "    def test_admin(self): self.assertTrue(allowed('admin'))\n", encoding="utf8"
    )
    commit(repo, "immutable base")
    return repo


def prepare(repo: Path, root: Path, mode: str) -> tuple[Path, str]:
    shadow = root / "shadow"
    cmd(["git", "clone", "-q", str(repo), str(shadow)], root)
    initial = head(repo)
    code = "def allowed(role):\n    return True\n" if mode == "bad" else "def allowed(role):\n    return role == 'admin'\n"
    (shadow / "app.py").write_text(code, encoding="utf8")
    assert not clean(shadow)
    return shadow, initial


def checks(shadow: Path) -> dict:
    public = cmd([sys.executable, "-m", "unittest", "discover", "-q"], shadow, check=False)
    hidden = cmd([sys.executable, "-c", "from app import allowed; assert allowed('admin') and not allowed('guest')"], shadow, check=False)
    return {"public_pass": public.returncode == 0, "hidden_pass": hidden.returncode == 0}


def promote(repo: Path, shadow: Path, start_head: str, lockfile: Path, done: Path,
            identity: str, *, inject_partial: bool = False) -> str:
    """Promote a verified shadow diff under a nonblocking OS lock and HEAD CAS."""
    with lockfile.open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return "RED_LOCKED"
        try:
            if done.exists() and identity in json.loads(done.read_text()):
                return "SKIP_ALREADY_DONE"
            if head(repo) != start_head or not clean(repo):
                return "STALE"
            gates = checks(shadow)
            if not gates["public_pass"]:
                return "RED_PUBLIC"
            if not gates["hidden_pass"]:
                return "RED_VERIFIER"
            diff = cmd(["git", "diff", "--binary", "--", "app.py"], shadow).stdout
            if not diff:
                return "RED_NO_PATCH"
            p = subprocess.run(["git", "apply", "--check", "-"], cwd=repo, input=diff,
                               text=True, capture_output=True, timeout=30)
            if p.returncode != 0:
                return "RED_PATCH"
            if inject_partial:
                # Crash before applying the candidate: canonical state is untouched.
                return "RED_PARTIAL"
            try:
                p = subprocess.run(["git", "apply", "-"], cwd=repo, input=diff,
                                   text=True, capture_output=True, timeout=30)
                if p.returncode != 0:
                    raise RuntimeError("git apply failed")
                commit(repo, "verified and CAS-promoted")
            except Exception:
                cmd(["git", "reset", "--hard", start_head], repo)
                return "RED_ROLLED_BACK"
            contents = json.loads(done.read_text()) if done.exists() else {}
            contents[identity] = {"commit": head(repo), "patch_sha256": hashlib.sha256(diff.encode()).hexdigest()}
            tmp = done.with_suffix(".tmp")
            tmp.write_text(json.dumps(contents, sort_keys=True) + "\n", encoding="utf8")
            os.replace(tmp, done)
            return "GREEN"
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def run_all() -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="fc-stateful-") as d:
        root = Path(d)
        rows = []
        for scenario, expected in CASES:
            tag = "FC001_clean_patch" if scenario == "FC007_duplicate_replay" else scenario
            folder = root / tag
            if scenario != "FC007_duplicate_replay":
                repo = setup(root, tag)
                shadow, initial = prepare(repo, folder, "bad" if scenario == "FC006_hidden_invariant" else "good")
            else:
                repo = folder / "canonical"
                shadow = folder / "shadow"
                initial = head(repo)
            lockfile = folder / "writer.lock"
            done = folder / "done.json"
            identity = "one-id" if scenario in ("FC001_clean_patch", "FC007_duplicate_replay") else scenario
            if scenario == "FC003_stale_head":
                (repo / "external.txt").write_text("intervening writer\n", encoding="utf8")
                commit(repo, "intervening external change")
            blocker = None
            if scenario == "FC004_writer_conflict":
                blocker = lockfile.open("a+")
                fcntl.flock(blocker.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            before = head(repo)
            try:
                verdict = promote(repo, shadow, initial, lockfile, done, identity,
                                  inject_partial=scenario == "FC005_partial_failure")
            finally:
                if blocker:
                    fcntl.flock(blocker.fileno(), fcntl.LOCK_UN)
                    blocker.close()
            after = head(repo)
            assert verdict == expected, (scenario, verdict, expected)
            assert clean(repo), (scenario, "dirty canonical repository")
            assert (before != after) == (scenario == "FC001_clean_patch"), (scenario, before, after)
            if scenario == "FC007_duplicate_replay":
                assert json.loads(done.read_text())[identity]["commit"] == after
            rows.append({
                "schema": SCHEMA,
                "scenario": scenario,
                "expected": expected,
                "observed": verdict,
                "canonical_head_before": before,
                "canonical_head_after": after,
                "canonical_mutation": before != after,
                "clean_canonical_after": True,
                "model_executed": False,
                "variant_ablation_executed": False,
            })
        return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", help="Optional raw JSONL receipt destination")
    a = ap.parse_args()
    rows = run_all()
    payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
    if a.output:
        dest = Path(a.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(payload, encoding="utf8")
    print(json.dumps({"schema": SCHEMA, "status": "GREEN_STATEFUL_CONTROL_SELFTEST",
                      "scenarios": len(rows), "no_false_promotions": True,
                      "model_results_available": False,
                      "receipts_sha256": hashlib.sha256(payload.encode()).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
