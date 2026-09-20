import * as ort from "./lib/ort.wasm.min.mjs";
import { cleanTabTitle } from "./clean.js";
import { DistilBertTokenizer } from "./tokenizer.js";

const MAX_LENGTH = 128;
const CACHE_LIMIT = 512;
const MODEL_URL = chrome.runtime.getURL("model/model.onnx");
const VOCAB_URL = chrome.runtime.getURL("model/vocab.txt");

ort.env.wasm.numThreads = 1;
ort.env.wasm.simd = true;
ort.env.wasm.proxy = false;
ort.env.wasm.wasmPaths = chrome.runtime.getURL("lib/");

let sessionPromise;
let tokenizerPromise;
const embeddingCache = new Map();

function loadTokenizer() {
  if (!tokenizerPromise) {
    tokenizerPromise = DistilBertTokenizer.load(VOCAB_URL);
  }
  return tokenizerPromise;
}

function loadSession() {
  if (!sessionPromise) {
    sessionPromise = ort.InferenceSession.create(MODEL_URL, {
      executionProviders: ["wasm"],
    });
  }
  return sessionPromise;
}

function remember(text, vector) {
  embeddingCache.set(text, vector);
  if (embeddingCache.size > CACHE_LIMIT) {
    const oldest = embeddingCache.keys().next().value;
    embeddingCache.delete(oldest);
  }
}

async function embed(text, tokenizer, session) {
  const key = String(text || "").trim();
  if (!key) return null;
  const cached = embeddingCache.get(key);
  if (cached) return cached;

  const encoded = tokenizer.encode(key, MAX_LENGTH);
  const results = await session.run({
    input_ids: new ort.Tensor("int64", encoded.inputIds, [1, MAX_LENGTH]),
    attention_mask: new ort.Tensor("int64", encoded.attentionMask, [1, MAX_LENGTH]),
  });
  const vector = Float32Array.from(results.embedding.data);
  remember(key, vector);
  return vector;
}

function cosine(a, b) {
  let sum = 0;
  for (let i = 0; i < a.length; i += 1) sum += a[i] * b[i];
  return sum;
}

async function scoreTabs(openedTabs, newTab) {
  const [tokenizer, session] = await Promise.all([loadTokenizer(), loadSession()]);
  const sessionText = (openedTabs || [])
    .map((title) => cleanTabTitle(title))
    .filter(Boolean)
    .join(" | ");
  const sessionVec = await embed(sessionText, tokenizer, session);
  const query = await embed(cleanTabTitle(newTab), tokenizer, session);
  if (!sessionVec || !query) return 1;
  return Math.min(1, Math.max(0, cosine(sessionVec, query)));
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "SCORE_TABS") {
    scoreTabs(message.openedTabs || [], message.newTab || "")
      .then((onTask) => sendResponse({ ok: true, onTask }))
      .catch((error) => sendResponse({ ok: false, error: String(error?.message || error) }));
    return true;
  }
  if (message?.type === "WARMUP_MODEL") {
    Promise.all([loadTokenizer(), loadSession()])
      .then(async ([tokenizer, session]) => {
        await embed("warmup", tokenizer, session);
        sendResponse({ ok: true });
      })
      .catch((error) => sendResponse({ ok: false, error: String(error?.message || error) }));
    return true;
  }
  return false;
});
