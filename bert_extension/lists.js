const STORAGE_KEYS = {
  blacklist: "blacklist",
  whitelist: "whitelist",
};

function stripWww(host) {
  return host.replace(/^www\./, "");
}

function canonicalizeHref(url) {
  url.hash = "";
  url.hostname = stripWww(url.hostname.toLowerCase());
  return url.href.toLowerCase().replace(/\/+$/, "");
}

export function normalizeEntry(raw) {
  let value = String(raw || "").trim().toLowerCase();
  if (!value) return "";
  value = value.replace(/#.*$/, "").replace(/\/+$/, "");

  if (value.includes("://")) {
    try {
      const url = new URL(value);
      if (!url.hostname) return "";
      const path = url.pathname === "" || url.pathname === "/" ? "/" : url.pathname;
      if (path === "/" && !url.search) {
        return stripWww(url.hostname.toLowerCase());
      }
      return canonicalizeHref(url);
    } catch {
      return "";
    }
  }

  value = value.replace(/^https?:\/\//, "").replace(/\/+$/, "");
  if (!value) return "";

  if (value.includes("/")) {
    try {
      return canonicalizeHref(new URL(`https://${value}`));
    } catch {
      return "";
    }
  }

  return stripWww(value);
}

export function isDomainEntry(entry) {
  return Boolean(entry) && !entry.includes("://") && !entry.includes("/");
}

export function normalizePageUrl(pageUrl) {
  try {
    return canonicalizeHref(new URL(pageUrl));
  } catch {
    return String(pageUrl || "").trim().toLowerCase().replace(/\/+$/, "");
  }
}

export function pageHostname(pageUrl) {
  try {
    return stripWww(new URL(pageUrl).hostname.toLowerCase());
  } catch {
    return "";
  }
}

export function entryMatchesUrl(entry, pageUrl) {
  if (!entry || !pageUrl) return false;
  const host = pageHostname(pageUrl);
  if (isDomainEntry(entry)) {
    const domain = stripWww(entry);
    return host === domain || host.endsWith(`.${domain}`);
  }
  const page = normalizePageUrl(pageUrl);
  return page === entry || page.startsWith(`${entry}/`);
}

export function urlMatchesList(pageUrl, entries) {
  return (entries || []).some((entry) => entryMatchesUrl(entry, pageUrl));
}

export function isSkippableUrl(url) {
  if (!url) return true;
  const lower = url.toLowerCase();
  return (
    lower.startsWith("chrome://") ||
    lower.startsWith("chrome-extension://") ||
    lower.startsWith("edge://") ||
    lower.startsWith("about:") ||
    lower.startsWith("devtools://") ||
    lower.startsWith("moz-extension://") ||
    lower.startsWith("file:") ||
    lower.startsWith("data:") ||
    lower.startsWith("blob:") ||
    lower.startsWith("javascript:")
  );
}

export async function getLists() {
  const data = await chrome.storage.local.get([STORAGE_KEYS.blacklist, STORAGE_KEYS.whitelist]);
  return {
    blacklist: Array.isArray(data.blacklist) ? data.blacklist : [],
    whitelist: Array.isArray(data.whitelist) ? data.whitelist : [],
  };
}

export async function addToList(listName, rawEntry) {
  if (listName !== "blacklist" && listName !== "whitelist") {
    throw new Error("Unknown list.");
  }
  const entry = normalizeEntry(rawEntry);
  if (!entry) {
    throw new Error("Enter a URL or domain.");
  }

  const lists = await getLists();
  const otherName = listName === "blacklist" ? "whitelist" : "blacklist";
  if (lists[otherName].includes(entry)) {
    throw new Error(`Already on the ${otherName}. Remove it there first.`);
  }
  if (lists[listName].includes(entry)) {
    return entry;
  }

  const next = {
    blacklist: [...lists.blacklist],
    whitelist: [...lists.whitelist],
  };
  next[listName] = [...next[listName], entry];
  await chrome.storage.local.set(next);
  return entry;
}

export async function removeFromList(listName, entry) {
  if (listName !== "blacklist" && listName !== "whitelist") {
    throw new Error("Unknown list.");
  }
  const lists = await getLists();
  await chrome.storage.local.set({
    ...lists,
    [listName]: lists[listName].filter((item) => item !== entry),
  });
}

export function currentPageEntries(pageUrl) {
  const host = pageHostname(pageUrl);
  const page = normalizePageUrl(pageUrl);
  const entries = [];
  if (host) entries.push({ kind: "domain", value: host });
  if (page && page !== host) entries.push({ kind: "url", value: page });
  return entries;
}
