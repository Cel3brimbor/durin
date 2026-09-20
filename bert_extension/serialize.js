import { cleanTabTitle } from "./clean.js";

export function cleanText(text) {
  return String(text || "")
    .replace(/\t/g, " ")
    .replace(/\n/g, " ")
    .replace(/\r/g, " ")
    .split(/\s+/)
    .filter(Boolean)
    .join(" ");
}

export function serializeForBert(openedTabs, newTab, maxWords = 90) {
  const newPart = `New: ${cleanText(cleanTabTitle(newTab))}`;
  let budget = maxWords - newPart.split(/\s+/).filter(Boolean).length;
  const kept = [];
  for (let i = openedTabs.length - 1; i >= 0; i -= 1) {
    const text = cleanText(cleanTabTitle(openedTabs[i]));
    const cost = text.split(/\s+/).filter(Boolean).length + 1;
    if (kept.length && budget - cost < 0) {
      break;
    }
    kept.push(text);
    budget -= cost;
  }
  kept.reverse();
  return `${newPart} || ${kept.join(" | ")}`;
}
