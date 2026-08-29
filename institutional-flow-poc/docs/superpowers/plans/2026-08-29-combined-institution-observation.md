# Combined Institution Observation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the descriptive TWSE observation outputs to show foreign, trust, dealer, combined, All, and user-selected institutional combinations.

**Architecture:** Parse official T86 dealer totals, derive each requested group net directly at stock and sector grains, then reuse existing Flow Ratio, breadth, concentration, rotation, and snapshot pipelines. Keep observation outputs descriptive and allow `+`-joined group names through the CLI.

**Tech Stack:** Python standard library, unittest, CSV/JSON/SVG.

**Spec:** `docs/superpowers/specs/2026-08-29-institutional-flow-poc-design.md`

## Global Constraints

- Use TWSE official raw data already captured in `data/raw/`.
- Keep outputs observation-only; do not add trend labels, trading signals, or investment advice.
- Preserve existing foreign and trust outputs and tests.
- Recompute combined metrics from raw foreign/trust net shares and market volume; do not average ratios.

### Task 1: Add combined metric behavior

**Files:**
- Modify: `tests/test_metrics.py`
- Modify: `src/institutional_flow_poc/metrics.py`

- [ ] Write a failing test asserting stock and sector combined ratios use `(foreign_net + trust_net) / volume`.
- [ ] Run the focused test and confirm it fails because combined fields are absent.
- [ ] Add the minimal combined calculation alongside foreign/trust.
- [ ] Run focused and full tests.

### Task 2: Add combined observation and artifacts

**Files:**
- Modify: `tests/test_observation.py`
- Modify: `src/institutional_flow_poc/pipeline.py`
- Modify: `src/institutional_flow_poc/observation.py`
- Modify: `README.md`
- Modify: `docs/field_mapping.md`

- [ ] Add failing tests for combined observation rows and comparison fields.
- [ ] Implement combined rows and write `combined_rotation.csv`, `combined_rotation_map.svg`, and combined snapshot files.
- [ ] Regenerate real-data outputs and update documentation.
- [ ] Run all tests and validate row counts and observation-only mode.
