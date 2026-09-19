from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch.nn.functional import softmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_DIR = ROOT / "general_model"
TOKENIZER_NAME = "distilbert-base-uncased"
MAX_LENGTH = 128


def clean_text(text: str) -> str:
    return " ".join(text.replace("\t", " ").replace("\n", " ").replace("\r", " ").split())


def serialize_for_bert(opened_tabs: list[str], new_tab: str, max_words: int = 90) -> str:
    new_part = f"New: {clean_text(new_tab)}"
    budget = max_words - len(new_part.split())
    kept = []
    for tab in reversed(opened_tabs):
        text = clean_text(tab)
        cost = len(text.split()) + 1
        if kept and budget - cost < 0:
            break
        kept.append(text)
        budget -= cost
    kept.reverse()
    return f"{new_part} || " + " | ".join(kept)


def checkpoint_epoch(path: Path) -> int:
    state_file = path / "trainer_state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text())
        epoch = state.get("epoch")
        if epoch is not None:
            return int(round(float(epoch)))
    step = int(path.name.split("-")[-1])
    return max(1, round(step / 1250))


def list_checkpoints(model_dir: Path) -> list[tuple[int, Path]]:
    checkpoints = []
    for path in model_dir.glob("checkpoint-*"):
        if (path / "model.safetensors").exists() or (path / "pytorch_model.bin").exists():
            checkpoints.append((checkpoint_epoch(path), path))
    checkpoints.sort(key=lambda item: int(item[1].name.split("-")[-1]))
    return checkpoints


def resolve_model_dir(model_dir: Path, epoch: int | None = None) -> Path:
    checkpoints = list_checkpoints(model_dir)
    if epoch is not None:
        matches = [path for ckpt_epoch, path in checkpoints if ckpt_epoch == epoch]
        if not matches:
            available = ", ".join(str(ckpt_epoch) for ckpt_epoch, _ in checkpoints) or "none"
            raise FileNotFoundError(
                f"No checkpoint for epoch {epoch} in {model_dir}. Available epochs: {available}"
            )
        chosen = matches[-1]
        print(f"Using epoch {epoch} checkpoint: {chosen}")
        return chosen
    if checkpoints:
        latest_epoch, latest_path = checkpoints[-1]
        print(f"Using latest checkpoint: epoch {latest_epoch} ({latest_path})")
        return latest_path
    if (model_dir / "model.safetensors").exists() or (model_dir / "pytorch_model.bin").exists():
        return model_dir
    raise FileNotFoundError(
        f"No trained weights in {model_dir}. Wait for training to save a checkpoint."
    )


def load_model(model_dir: Path, epoch: int | None = None):
    weights_dir = resolve_model_dir(model_dir, epoch=epoch)
    device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(weights_dir)
    model.to(device)
    model.eval()
    print(f"Loaded model from {weights_dir} on {device}")
    return tokenizer, model, device


def score_tabs(tokenizer, model, device, opened_tabs: list[str], new_tab: str) -> float:
    text = serialize_for_bert(opened_tabs, new_tab)
    encoded = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}
    with torch.no_grad():
        logits = model(**encoded).logits
        probs = softmax(logits, dim=-1)[0]
    return float(probs[1].item())


def parse_tab_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def interactive_loop(tokenizer, model, device) -> None:
    print("Enter current tabs, then the new tab. Empty current-tabs line exits.")
    while True:
        raw_tabs = input("\nCurrent tabs (comma-separated): ").strip()
        if not raw_tabs:
            break
        opened_tabs = parse_tab_list(raw_tabs)
        if not opened_tabs:
            print("Need at least one current tab.")
            continue
        new_tab = input("New tab: ").strip()
        if not new_tab:
            print("Need a new tab title.")
            continue
        score = score_tabs(tokenizer, model, device, opened_tabs, new_tab)
        label = "on-task" if score >= 0.5 else "off-task"
        print(f"Score: {score:.4f}  ({label})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score whether a new tab is on-task.")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_DIR), help="Model or checkpoint directory")
    parser.add_argument(
        "--epoch",
        type=int,
        default=None,
        help="Checkpoint epoch to load (1, 2, ...). Defaults to the latest saved epoch.",
    )
    parser.add_argument("--tabs", default="", help="Comma-separated current tabs (skips interactive mode)")
    parser.add_argument("--new", default="", help="New tab title (used with --tabs)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tokenizer, model, device = load_model(Path(args.model), epoch=args.epoch)
    if args.tabs or args.new:
        if not args.tabs or not args.new:
            raise SystemExit("Pass both --tabs and --new, or neither for interactive mode.")
        score = score_tabs(tokenizer, model, device, parse_tab_list(args.tabs), args.new)
        print(f"{score:.4f}")
        return
    interactive_loop(tokenizer, model, device)


if __name__ == "__main__":
    main()
