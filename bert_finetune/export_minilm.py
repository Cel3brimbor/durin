"""Export sentence-transformers/all-MiniLM-L6-v2 for the Chrome extension.

The ONNX graph mean-pools token embeddings, L2-normalizes, and hides BERT
token_type_ids so the extension only passes input_ids and attention_mask.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_OUT = ROOT / "chrome_extension_2" / "model"
MAX_LENGTH = 128


class MiniLMEmbedder(torch.nn.Module):
    def __init__(self, encoder: AutoModel):
        super().__init__()
        self.encoder = encoder

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        token_type_ids = torch.zeros_like(input_ids)
        hidden = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        ).last_hidden_state
        mask = attention_mask.unsqueeze(-1).to(hidden.dtype)
        pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        return F.normalize(pooled, p=2, dim=1)


def encode_texts(embedder: MiniLMEmbedder, tokenizer: AutoTokenizer, texts: list[str], device: torch.device):
    encoded = tokenizer(
        texts,
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )
    encoded = {key: value.to(device) for key, value in encoded.items() if key in ("input_ids", "attention_mask")}
    with torch.no_grad():
        return embedder(encoded["input_ids"], encoded["attention_mask"]).cpu().numpy()


def session_cosine(embedder, tokenizer, opened_tabs: list[str], new_tab: str, device: torch.device) -> float:
    session = encode_texts(embedder, tokenizer, [" | ".join(opened_tabs)], device)[0]
    query = encode_texts(embedder, tokenizer, [new_tab], device)[0]
    return float(np.dot(session, query))


def export_onnx(embedder: MiniLMEmbedder, path: Path) -> None:
    embedder.eval()
    dummy_ids = torch.ones(1, MAX_LENGTH, dtype=torch.long)
    dummy_mask = torch.ones(1, MAX_LENGTH, dtype=torch.long)
    torch.onnx.export(
        embedder,
        (dummy_ids, dummy_mask),
        str(path),
        input_names=["input_ids", "attention_mask"],
        output_names=["embedding"],
        opset_version=17,
        dynamo=False,
    )


def check_pairs(embedder, tokenizer, device: torch.device) -> None:
    cases = [
        (["bert", "google deepmind", "edge ai", "local inference"], "large language models"),
        (["bert", "google deepmind", "edge ai", "local inference"], "YouTube - Funny Cat Compilation 2026"),
        (["bert", "google deepmind", "edge ai", "local inference"], "bert fine tuning"),
        (["physics 2", "newtonian laws"], "black hole relativity"),
        (["physics 2", "newtonian laws"], "roblox"),
    ]
    print("Session cosine checks:")
    for tabs, new in cases:
        score = session_cosine(embedder, tokenizer, tabs, new, device)
        print(f"  {score:+.4f}  new={new!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export MiniLM ONNX for chrome_extension_2.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Directory for model.onnx and vocab.txt")
    parser.add_argument("--skip-check", action="store_true", help="Skip cosine smoke tests")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cpu")
    print(f"Loading {MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    encoder = AutoModel.from_pretrained(MODEL_ID)
    encoder.eval()
    embedder = MiniLMEmbedder(encoder).to(device)
    embedder.eval()

    if not args.skip_check:
        check_pairs(embedder, tokenizer, device)

    onnx_path = out_dir / "model.onnx"
    print(f"Exporting ONNX to {onnx_path}")
    export_onnx(embedder.cpu(), onnx_path)

    vocab_src = Path(tokenizer.vocab_file) if getattr(tokenizer, "vocab_file", None) else None
    vocab_dest = out_dir / "vocab.txt"
    if vocab_src and vocab_src.exists():
        shutil.copyfile(vocab_src, vocab_dest)
    else:
        items = sorted(tokenizer.get_vocab().items(), key=lambda item: item[1])
        vocab_dest.write_text("".join(f"{token}\n" for token, _ in items), encoding="utf-8")
    print(f"Wrote {vocab_dest}")

    try:
        import onnxruntime as ort
    except ImportError:
        print("onnxruntime not installed; skipped ONNX numeric check.")
        return

    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    text = "large language models"
    encoded = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="np",
    )
    with torch.no_grad():
        torch_vec = encode_texts(embedder, tokenizer, [text], torch.device("cpu"))[0]
    onnx_vec = session.run(
        ["embedding"],
        {
            "input_ids": encoded["input_ids"].astype(np.int64),
            "attention_mask": encoded["attention_mask"].astype(np.int64),
        },
    )[0][0]
    delta = float(np.max(np.abs(torch_vec - onnx_vec)))
    print(f"ONNX vs PyTorch max abs diff: {delta:.6g}")
    print(f"ONNX size: {onnx_path.stat().st_size / (1024 * 1024):.1f} MB")


if __name__ == "__main__":
    main()
