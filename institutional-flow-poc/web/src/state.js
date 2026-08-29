export const PAGES = ["today", "rotation", "ranking", "watchlist", "quality"];

export function createInitialState(payload) {
  let watchlist = [];
  if (typeof localStorage !== "undefined") {
    try {
      const stored = JSON.parse(localStorage.getItem("stockchart.watchlist") || "[]");
      if (Array.isArray(stored)) watchlist = stored.filter((code) => typeof code === "string");
    } catch { /* ignore malformed browser state */ }
  }
  return {
    page: "today",
    institution: payload.institutions?.includes("all") ? "all" : (payload.institutions?.[0] || "all"),
    date: payload.meta?.date_max || null,
    basis: payload.meta?.basis || "shares",
    trailWindow: 20,
    selectedIndustryCode: null,
    selectedSector: null,
    selectedSymbol: null,
    stockQuery: "",
    watchlist,
  };
}

export function reduceState(state, action) {
  switch (action.type) {
    case "navigate":
      return PAGES.includes(action.page) ? { ...state, page: action.page } : state;
    case "set-institution":
      return { ...state, institution: action.value, selectedIndustryCode: null, selectedSector: null, selectedSymbol: null };
    case "set-date":
      return { ...state, date: action.value, selectedIndustryCode: null };
    case "set-basis":
      return { ...state, basis: action.value };
    case "set-trail-window":
      return { ...state, trailWindow: action.value };
    case "select-industry":
      return { ...state, selectedIndustryCode: action.value, selectedSector: action.value, selectedSymbol: null };
    case "select-sector":
      return { ...state, selectedSector: action.value, selectedSymbol: null };
    case "select-symbol":
      return { ...state, selectedSymbol: action.value };
    case "set-stock-query":
      return { ...state, stockQuery: action.value, selectedSymbol: null };
    case "toggle-watchlist":
      return state.watchlist.includes(action.value)
        ? { ...state, watchlist: state.watchlist.filter((code) => code !== action.value) }
        : { ...state, watchlist: [...state.watchlist, action.value] };
    default:
      return state;
  }
}
