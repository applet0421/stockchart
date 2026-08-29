import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { createInitialState, reduceState } from "../src/state.js";

const fixture = JSON.parse(await readFile(new URL("./fixtures/model-a.json", import.meta.url)));

test("institution and basis changes are serializable", () => {
  const state = createInitialState(fixture);
  const next = reduceState(state, { type: "set-institution", value: "foreign" });
  assert.equal(next.institution, "foreign");
});

test("page navigation does not reset selected date", () => {
  const state = { ...createInitialState(fixture), date: "2026-08-28" };
  const next = reduceState(state, { type: "navigate", page: "rotation" });
  assert.equal(next.date, "2026-08-28");
});

test("sector selection clears stock selection and query updates are serializable", () => {
  let state = createInitialState(fixture);
  state = reduceState(state, { type: "select-symbol", value: "1101" });
  state = reduceState(state, { type: "select-sector", value: "01" });
  assert.equal(state.selectedSector, "01");
  assert.equal(state.selectedSymbol, null);
  state = reduceState(state, { type: "set-stock-query", value: "台泥" });
  assert.equal(state.stockQuery, "台泥");
});
