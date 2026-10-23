# Security Policy

## Scope

This project studies fail-closed control for software-engineering agents. Security-sensitive areas include stale-state protection, writer exclusion, replay protection, verification gates, promotion logic, and any future adapter that can mutate a real repository.

## Reporting a vulnerability

Please do **not** publish a live exploit or credential in a public issue.

Preferred routes:
1. Use GitHub private vulnerability reporting / Security Advisories if available for this repository.
2. If private reporting is unavailable, email **treining2016@gmail.com** with subject `SECURITY: fail-closed-swe-agent-benchmark`.

Include:
- affected commit or release;
- minimal reproduction;
- expected vs observed fail-closed behavior;
- whether canonical repository state can be mutated incorrectly;
- whether the issue enables replay, duplicate work, stale promotion, verifier bypass, or secret exposure.

## Response targets

The maintainer will triage reproducible security reports, preserve evidence, and publish a fix or documented limitation when appropriate. No response-time SLA is promised.

## Disclosure

Please allow time for a fix before public disclosure. Security fixes should include a regression test whenever feasible.

## Non-security reports

Ordinary bugs, documentation errors, and benchmark-design questions should use GitHub Issues.
