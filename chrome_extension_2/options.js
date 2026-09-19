import { addToList, getLists, removeFromList } from "./lists.js";

function setStatus(listName, message, kind) {
  const el = document.getElementById(`${listName}-status`);
  el.textContent = message;
  el.className = `status${kind ? ` ${kind}` : ""}`;
}

function renderList(listName, entries) {
  const root = document.getElementById(listName);
  root.replaceChildren();
  if (!entries.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "No entries yet.";
    root.append(empty);
    return;
  }
  for (const entry of entries) {
    const item = document.createElement("li");
    item.className = "list-item";
    const label = document.createElement("span");
    label.textContent = entry;
    const remove = document.createElement("button");
    remove.className = "ghost";
    remove.type = "button";
    remove.textContent = "Remove";
    remove.addEventListener("click", async () => {
      await removeFromList(listName, entry);
      setStatus(listName, `Removed ${entry}.`, "ok");
      await refresh();
    });
    item.append(label, remove);
    root.append(item);
  }
}

async function refresh() {
  const lists = await getLists();
  renderList("blacklist", lists.blacklist);
  renderList("whitelist", lists.whitelist);
}

function bindForm(listName) {
  const form = document.getElementById(`${listName}-form`);
  const input = document.getElementById(`${listName}-input`);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const saved = await addToList(listName, input.value);
      input.value = "";
      setStatus(listName, `Added ${saved}.`, "ok");
      await refresh();
    } catch (error) {
      setStatus(listName, error.message || String(error), "error");
    }
  });
}

bindForm("blacklist");
bindForm("whitelist");
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && (changes.blacklist || changes.whitelist)) {
    refresh();
  }
});
await refresh();
