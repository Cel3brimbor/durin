import { getLists, isSkippableUrl, urlMatchesList } from "./lists.js";

const MIN_CONTEXT_TABS = 4;
const ON_TASK_THRESHOLD = 0.5;
const OFFSCREEN_PATH = "offscreen.html";

let creatingOffscreen;
const inFlight = new Map();

function blockedPageUrl({ url, reason, score }) {
  const params = new URLSearchParams({ url, reason });
  if (score != null) params.set("score", String(score));
  return chrome.runtime.getURL(`blocked.html?${params.toString()}`);
}

function isBlockedPage(url) {
  if (!url) return false;
  return url.startsWith(chrome.runtime.getURL("blocked.html"));
}

async function ensureOffscreen() {
  const existing = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [chrome.runtime.getURL(OFFSCREEN_PATH)],
  });
  if (existing.length > 0) return;
  if (!creatingOffscreen) {
    creatingOffscreen = chrome.offscreen
      .createDocument({
        url: OFFSCREEN_PATH,
        reasons: ["WORKERS"],
        justification: "Run the on-task DistilBERT ONNX model in a page context.",
      })
      .catch((error) => {
        const message = String(error?.message || error);
        if (!message.includes("single offscreen document")) throw error;
      })
      .finally(() => {
        creatingOffscreen = undefined;
      });
  }
  await creatingOffscreen;
}

async function sendToOffscreen(message, attempts = 15) {
  await ensureOffscreen();
  let lastError;
  for (let i = 0; i < attempts; i += 1) {
    try {
      const response = await chrome.runtime.sendMessage(message);
      if (response) return response;
      lastError = new Error("Empty offscreen response");
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw lastError || new Error("Offscreen inference is not ready.");
}

async function warmupModel() {
  try {
    await sendToOffscreen({ type: "WARMUP_MODEL" });
  } catch (error) {
    console.warn("Durin model warmup failed:", error);
  }
}

async function contextTitles(tab) {
  const tabs = await chrome.tabs.query({ windowId: tab.windowId });
  return tabs
    .filter((other) => other.id !== tab.id)
    .filter((other) => other.url && /^https?:/i.test(other.url))
    .filter((other) => !isBlockedPage(other.url) && !isSkippableUrl(other.url))
    .map((other) => other.title)
    .filter((title) => Boolean(title && title.trim()));
}

async function redirect(tabId, url) {
  try {
    await chrome.tabs.update(tabId, { url });
  } catch (error) {
    console.warn("Durin could not redirect tab:", error);
  }
}

async function handleBeforeNavigate(details) {
  if (details.frameId !== 0) return;
  if (isSkippableUrl(details.url) || isBlockedPage(details.url)) return;
  const lists = await getLists();
  if (urlMatchesList(details.url, lists.blacklist)) {
    await redirect(details.tabId, blockedPageUrl({ url: details.url, reason: "blacklist" }));
  }
}

async function handleCompleted(details) {
  if (details.frameId !== 0) return;
  if (isSkippableUrl(details.url) || isBlockedPage(details.url)) return;

  const key = `${details.tabId}:${details.url}`;
  if (inFlight.has(key)) return;
  inFlight.set(key, true);

  try {
    const lists = await getLists();
    if (urlMatchesList(details.url, lists.blacklist)) {
      await redirect(details.tabId, blockedPageUrl({ url: details.url, reason: "blacklist" }));
      return;
    }
    if (urlMatchesList(details.url, lists.whitelist)) return;

    await new Promise((resolve) => setTimeout(resolve, 400));

    let tab;
    try {
      tab = await chrome.tabs.get(details.tabId);
    } catch {
      return;
    }
    if (!tab?.url || tab.url !== details.url) return;

    const openedTabs = await contextTitles(tab);
    if (openedTabs.length < MIN_CONTEXT_TABS) return;

    let response;
    try {
      response = await sendToOffscreen({
        type: "SCORE_TABS",
        openedTabs,
        newTab: tab.title || details.url,
      });
    } catch (error) {
      console.warn("Durin scoring failed:", error);
      return;
    }
    if (!response?.ok) {
      console.warn("Durin scoring failed:", response?.error);
      return;
    }

    const current = await chrome.tabs.get(details.tabId).catch(() => null);
    if (!current?.url || current.url !== details.url) return;
    if (urlMatchesList(current.url, (await getLists()).whitelist)) return;

    if (response.onTask < ON_TASK_THRESHOLD) {
      const score = Math.round((1 - response.onTask) * 100);
      await redirect(details.tabId, blockedPageUrl({ url: details.url, reason: "model", score }));
    }
  } catch (error) {
    console.warn("Durin navigation handler failed:", error);
  } finally {
    inFlight.delete(key);
  }
}

chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  handleBeforeNavigate(details).catch((error) => {
    console.warn("Durin blacklist handler failed:", error);
  });
});
chrome.webNavigation.onCompleted.addListener((details) => {
  handleCompleted(details).catch((error) => {
    console.warn("Durin scoring handler failed:", error);
  });
});
chrome.webNavigation.onHistoryStateUpdated.addListener((details) => {
  handleCompleted(details).catch((error) => {
    console.warn("Durin history handler failed:", error);
  });
});
chrome.runtime.onInstalled.addListener(warmupModel);
chrome.runtime.onStartup.addListener(warmupModel);
