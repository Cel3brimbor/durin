const params = new URLSearchParams(window.location.search);
const url = params.get("url") || "";
const reason = params.get("reason") || "";
const score = params.get("score");

document.getElementById("blocked-url").textContent = url || "(unknown URL)";

const reasonEl = document.getElementById("reason");
const scoreWrap = document.getElementById("score-wrap");
const scoreEl = document.getElementById("score");

if (reason === "blacklist") {
  reasonEl.textContent = "Blocked by blacklist. The neural network was not used.";
} else {
  reasonEl.textContent = "MiniLM scored this tab as off-task given your other open tabs.";
  if (score != null && score !== "") {
    scoreWrap.hidden = false;
    scoreEl.textContent = `${score}%`;
  }
}
