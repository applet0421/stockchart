# Phase 1 Stock Drill-down Design

**Goal:** Extend Model A from sector-level observations to a transparent sector-to-stock drill-down using existing public stock flow data.

## Scope

- Keep the existing 32 validated sectors; add a versioned topic mapping schema without inventing new assignments.
- Selecting a sector shows its component stocks for the selected institution and date.
- Each stock exposes 1D/5D/20D flow, institutional components, contribution share, and source-gap state.
- Selecting a stock shows its historical flow for the available 120 trading days.
- Nulls and missing-source flags remain visible; no imputation.
- No authentication, payment, push notification, or remote persistence in this phase.

## Data contract

`web/data/model-a.json` gains `topic_mapping` metadata and per-sector `stocks` rows. Stock rows use `symbol`, `name`, `industry_code`, `date`, `flow_1d`, `flow_5d`, `flow_20d`, `foreign_net`, `trust_net`, `dealer_net`, `contribution_share`, and `source_missing`.

## Interaction

Model A detail panel provides a keyboard-accessible “查看成分股” action. The stock table supports symbol/name search and clicking a row opens a compact history panel. Institution and date controls remain shared with the page state.

## Verification

Python contract tests cover aggregation, null preservation, and mapping versioning. Node tests cover reducer transitions. Browser smoke checks cover sector selection, stock table rendering, search, and history panel on desktop and mobile widths.
