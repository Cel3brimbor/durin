import * as ort from "./lib/ort.wasm.min.mjs";
import { serializeForBert } from "./serialize.js";
import { DistilBertTokenizer } from "./tokenizer.js";

const MAX_LENGTH = 128;
const MODEL_URL = chrome.runtime.getURL("model/model.onnx");
const VOCAB_URL = chrome.runtime.getURL("model/vocab.txt");

ort.env.wasm.numThreads = 1;
ort.env.wasm.simd = true;
ort.env.wasm.proxy = false;
ort.env.wasm.wasmPaths = chrome.runtime.getURL("lib/");

let sessionPromise;
let tokenizerPromise;

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

function softmax(logits) {
  const values = Array.from(logits, Number);
  const max = Math.max(...values);
  const exps = values.map((value) => Math.exp(value - max));
  const sum = exps.reduce((total, value) => total + value, 0);
  return exps.map((value) => value / sum);
}

async function scoreTabs(openedTabs, newTab) {
  const [tokenizer, session] = await Promise.all([loadTokenizer(), loadSession()]);
  const text = serializeForBert(openedTabs, newTab);
  const encoded = tokenizer.encode(text, MAX_LENGTH);
  const results = await session.run({
    input_ids: new ort.Tensor("int64", encoded.inputIds, [1, MAX_LENGTH]),
    attention_mask: new ort.Tensor("int64", encoded.attentionMask, [1, MAX_LENGTH]),
  });
  const logits = results.logits.data;
  const probs = softmax(logits);
  return probs[1];
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
      .then(() => sendResponse({ ok: true }))
      .catch((error) => sendResponse({ ok: false, error: String(error?.message || error) }));
    return true;
  }
  return false;
});
