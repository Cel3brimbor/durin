const PAD_ID = 0;
const UNK_ID = 100;
const CLS_ID = 101;
const SEP_ID = 102;

function isWhitespace(ch) {
  return ch === " " || ch === "\t" || ch === "\n" || ch === "\r" || /\p{Zs}/u.test(ch);
}

function isControl(ch) {
  if (ch === "\t" || ch === "\n" || ch === "\r") return false;
  return /\p{Cc}|\p{Cf}/u.test(ch);
}

function isPunctuation(ch) {
  const cp = ch.codePointAt(0);
  if (
    (cp >= 33 && cp <= 47) ||
    (cp >= 58 && cp <= 64) ||
    (cp >= 91 && cp <= 96) ||
    (cp >= 123 && cp <= 126)
  ) {
    return true;
  }
  return /\p{P}/u.test(ch);
}

function isChineseChar(cp) {
  return (
    (cp >= 0x4e00 && cp <= 0x9fff) ||
    (cp >= 0x3400 && cp <= 0x4dbf) ||
    (cp >= 0x20000 && cp <= 0x2a6df) ||
    (cp >= 0x2a700 && cp <= 0x2b73f) ||
    (cp >= 0x2b740 && cp <= 0x2b81f) ||
    (cp >= 0x2b820 && cp <= 0x2ceaf) ||
    (cp >= 0xf900 && cp <= 0xfaff) ||
    (cp >= 0x2f800 && cp <= 0x2fa1f)
  );
}

function stripAccents(text) {
  return text.normalize("NFD").replace(/\p{M}/gu, "");
}

function tokenizeChineseChars(text) {
  const out = [];
  for (const ch of text) {
    if (isChineseChar(ch.codePointAt(0))) {
      out.push(" ", ch, " ");
    } else {
      out.push(ch);
    }
  }
  return out.join("");
}

function cleanText(text) {
  const out = [];
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    if (cp === 0 || cp === 0xfffd || isControl(ch)) {
      continue;
    }
    out.push(isWhitespace(ch) ? " " : ch);
  }
  return out.join("");
}

function whitespaceTokenize(text) {
  return text.trim().split(/\s+/).filter(Boolean);
}

function splitOnPunctuation(token) {
  const chars = [...token];
  const output = [];
  let startNewWord = true;
  for (const ch of chars) {
    if (isPunctuation(ch)) {
      output.push(ch);
      startNewWord = true;
    } else {
      if (startNewWord) output.push("");
      startNewWord = false;
      output[output.length - 1] += ch;
    }
  }
  return output.filter((part) => part.length > 0);
}

function basicTokenize(text) {
  const cleaned = tokenizeChineseChars(cleanText(stripAccents(text.toLowerCase())));
  const tokens = [];
  for (const token of whitespaceTokenize(cleaned)) {
    tokens.push(...splitOnPunctuation(token));
  }
  return tokens;
}

function wordpiece(token, vocab, maxInputCharsPerWord = 200) {
  const chars = [...token];
  if (chars.length > maxInputCharsPerWord) {
    return ["[UNK]"];
  }
  const subTokens = [];
  let start = 0;
  while (start < chars.length) {
    let end = chars.length;
    let cur = null;
    while (start < end) {
      let substr = chars.slice(start, end).join("");
      if (start > 0) substr = `##${substr}`;
      if (vocab.has(substr)) {
        cur = substr;
        break;
      }
      end -= 1;
    }
    if (cur == null) {
      return ["[UNK]"];
    }
    subTokens.push(cur);
    start = end;
  }
  return subTokens;
}

export class DistilBertTokenizer {
  constructor(vocab) {
    this.vocab = vocab;
  }

  static fromVocabText(text) {
    const vocab = new Map();
    const lines = text.split(/\r?\n/);
    for (let i = 0; i < lines.length; i += 1) {
      const token = lines[i];
      if (token.length > 0) {
        vocab.set(token, i);
      }
    }
    return new DistilBertTokenizer(vocab);
  }

  static async load(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load vocab from ${url}`);
    }
    return DistilBertTokenizer.fromVocabText(await response.text());
  }

  tokenize(text) {
    const output = [];
    for (const token of basicTokenize(text)) {
      output.push(...wordpiece(token, this.vocab));
    }
    return output;
  }

  encode(text, maxLength = 128) {
    const pieces = this.tokenize(text);
    const maxPieces = Math.max(0, maxLength - 2);
    const truncated = pieces.slice(0, maxPieces);
    const ids = [CLS_ID];
    for (const piece of truncated) {
      ids.push(this.vocab.has(piece) ? this.vocab.get(piece) : UNK_ID);
    }
    ids.push(SEP_ID);
    const attention = new Array(ids.length).fill(1);
    while (ids.length < maxLength) {
      ids.push(PAD_ID);
      attention.push(0);
    }
    return {
      inputIds: BigInt64Array.from(ids, (n) => BigInt(n)),
      attentionMask: BigInt64Array.from(attention, (n) => BigInt(n)),
    };
  }
}
