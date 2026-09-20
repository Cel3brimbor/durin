import { addToList, currentPageEntries, getLists, isSkippableUrl, urlMatchesList } from "./lists.js";

const currentUrlEl = document.getElementById("current-url");
const membershipEl = document.getElementById("membership");
const statusEl = document.getElementById("status");

let pageUrl = "";
let domainEntry = "";
let urlEntry = "";

function setStatus(message, kind) {
  statusEl.textContent = message;
  statusEl.className = `status${kind ? ` ${kind}` : ""}`;
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
    membershipEl.textContent = "Currently blacklisted.";
  } else if (onWhite) {
    membershipEl.textContent = "Currently whitelisted.";
  } else {
    membershipEl.textContent = "Not on either list. The model may score it after 4 other tabs.";
  }
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
if (pageUrl && !isSkippableUrl(pageUrl)) {
  const entries = currentPageEntries(pageUrl);
  domainEntry = entries.find((entry) => entry.kind === "domain")?.value || "";
  urlEntry = entries.find((entry) => entry.kind === "url")?.value || "";
}
await refreshMembership();
