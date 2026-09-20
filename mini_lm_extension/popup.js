import { addToList, currentPageEntries, getLists, isSkippableUrl, urlMatchesList } from "./lists.js";
import { cleanTabTitle } from "./clean.js";

const currentUrlEl = document.getElementById("current-url");
const currentTitleEl = document.getElementById("current-title");
const membershipEl = document.getElementById("membership");
const statusEl = document.getElementById("status");
const scoreValueEl = document.getElementById("score-value");
const scoreLabelEl = document.getElementById("score-label");

let pageUrl = "";
let domainEntry = "";
let urlEntry = "";

function setStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.className = `status${kind ? ` ${kind}` : ""}`;
}

function setScore(text, kind, label) {
  scoreValueEl.textContent = text;
  scoreValueEl.className = `score-popup${kind ? ` ${kind}` : ""}`;
  scoreLabelEl.textContent = label;
}

async function refreshMembership() {
  if (!pageUrl || isSkippableUrl(pageUrl)) {
    membershipEl.textContent = "This page cannot be listed.";
    return;
  }
  const lists = await getLists();
  const onBlack = urlMatchesList(pageUrl, lists.blacklist);
  const onWhite = urlMatchesList(pageUrl, lists.whitelist);
  if (onBlack) {
    membershipEl.textContent = "Currently blacklisted. Lists override the model.";
  } else if (onWhite) {
    membershipEl.textContent = "Currently whitelisted. Lists override the model.";
  } else {
    membershipEl.textContent = "Not on either list.";
  }
}

async function refreshScore(tab) {
  if (!tab?.url || isSkippableUrl(tab.url)) {
    setScore("—", "", "This page cannot be scored.");
    return;
  }
  setScore("…", "", "Scoring…");
  let result;
  try {
    result = await chrome.runtime.sendMessage({ type: "SCORE_CURRENT_TAB", tabId: tab.id });
  } catch (error) {
    setScore("—", "", error.message || String(error));
    return;
  }
  if (!result?.ok) {
    setScore("—", "", result?.error || "Scoring failed.");
    return;
  }

  const need = result.minContext ?? 4;
  const have = result.contextCount ?? 0;
  if (result.onTask == null) {
    setScore("—", "", `Need another open http(s) tab to score. ${have} of ${need} for blocking.`);
    return;
  }

  const offTask = Math.round((1 - result.onTask) * 100);
  const onTask = Math.round(result.onTask * 100);
  const wouldBlock = result.onTask < result.threshold;
  const blockingArmed = have >= need;
  const kind = wouldBlock ? "off" : "on";
  const decision = wouldBlock ? "off-task" : "on-task";
  const action = !blockingArmed
    ? `need ${need} other tabs to block`
    : wouldBlock
      ? "would block"
      : "would allow";
  setScore(`${offTask}%`, kind, `${decision} · ${action}. Similarity ${onTask}% (${have} other tabs).`);
}

async function add(listName, value) {
  try {
    if (!value) throw new Error("No URL or domain for this page.");
    const saved = await addToList(listName, value);
    setStatus(`Added ${saved} to ${listName}.`, "ok");
    await refreshMembership();
  } catch (error) {
    setStatus(error.message || String(error), "error");
  }
}

document.getElementById("block-url").addEventListener("click", () => add("blacklist", urlEntry || pageUrl));
document.getElementById("block-domain").addEventListener("click", () => add("blacklist", domainEntry));
document.getElementById("allow-url").addEventListener("click", () => add("whitelist", urlEntry || pageUrl));
document.getElementById("allow-domain").addEventListener("click", () => add("whitelist", domainEntry));
document.getElementById("open-options").addEventListener("click", () => chrome.runtime.openOptionsPage());

const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
pageUrl = tab?.url || "";
currentUrlEl.textContent = pageUrl || "(no tab)";
currentTitleEl.textContent = cleanTabTitle(tab?.title || "");
if (pageUrl && !isSkippableUrl(pageUrl)) {
  const entries = currentPageEntries(pageUrl);
  domainEntry = entries.find((entry) => entry.kind === "domain")?.value || "";
  urlEntry = entries.find((entry) => entry.kind === "url")?.value || "";
}
await refreshMembership();
await refreshScore(tab);
