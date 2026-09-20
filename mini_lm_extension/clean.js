export function cleanTabTitle(title) {
  const cleaned = String(title || "")
    .replace(/ - Google Search$/i, "")
    .replace(/ - YouTube$/i, "")
    .replace(/ \| LinkedIn$/i, "")
    .replace(/ - Wikipedia$/i, "")
    .replace(/ [–—] Wikipedia$/i, "")
    .replace(/ \| YouTube$/i, "")
    .trim();
  return cleaned || String(title || "").trim();
}
