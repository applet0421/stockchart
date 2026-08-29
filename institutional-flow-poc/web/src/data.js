export function selectRows(payload, state) {
  const latest = payload.latest_by_institution?.[state.institution] || payload.latest || [];
  const history = payload.history_by_institution?.[state.institution] || payload.history || [];
  const rankings = payload.rankings_by_institution?.[state.institution] || payload.rankings || {};
  return { latest, history, rankings };
}

export function formatMetric(value, basis = "shares") {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const suffix = basis === "amount" ? " 金額估算" : " 股數比";
  return `${(Number(value) * 100).toFixed(2)}%${suffix}`;
}

export function formatCount(value) {
  return value === null || value === undefined ? "—" : String(value);
}

export function formatShares(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Number(value).toLocaleString("zh-TW")} 股`;
}
