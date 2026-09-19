import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, TrainerCallback
from datasets import load_dataset
import evaluate

#check hardware 
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Training on apple silicon GPU.")
else:
    device = torch.device("cpu")
    print("Falling back to CPU training.")


MODEL_NAME = "distilbert-base-uncased"  # 6 layers, 768 hidden dimensions (~66M params)
DATASET_PATH = "data_creator/general/general_dataset.txt"
OUTPUT_DIR = "./general_model"
ONNX_DIR = "./onnx_browser_model"


if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(f"Missing '{DATASET_PATH}'.") 

print("Loading raw data files...")
dataset = load_dataset("csv", data_files=DATASET_PATH, delimiter="\t", column_names=["text", "label"])
dataset = dataset["train"].train_test_split(test_size=0.2, seed=42)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

print("🔤 Tokenizing dataset arrays...")
tokenized_datasets = dataset.map(tokenize_function, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
model.to(device) #push model weights to unified memory

#eval
accuracy_metric = evaluate.load("accuracy")
NUM_EPOCHS = 4

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy_metric.compute(predictions=predictions, references=labels)

class AccuracyPrinter(TrainerCallback):
    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics and "eval_accuracy" in metrics:
            print(f"\nEpoch {state.epoch:.2f} eval accuracy: {metrics['eval_accuracy']:.4f}\n")

#fine tuning params
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=NUM_EPOCHS,
    weight_decay=0.01,
    logging_steps=5,
    load_best_model_at_end=True,
    metric_for_best_model="eval_accuracy",
    greater_is_better=True,
    use_cpu=False if torch.backends.mps.is_available() else True,
    disable_tqdm=False,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    compute_metrics=compute_metrics,
    callbacks=[AccuracyPrinter()],
)

print(f"Launching training for {NUM_EPOCHS} epochs. Accuracy is reported after each epoch.")
trainer.train()

print("\nAccuracy by epoch:")
for entry in trainer.state.log_history:
    if "eval_accuracy" in entry:
        print(f"  epoch {entry.get('epoch', '?'):.0f}: {entry['eval_accuracy']:.4f}")

final_metrics = trainer.evaluate()
print(f"\nFinal eval accuracy: {final_metrics.get('eval_accuracy', float('nan')):.4f}")

print(f"Exporting trained PyTorch configurations to: {OUTPUT_DIR}")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Initiating hugging face optimum compilation pipeline for browser deployment...")
try:
    import optimum  # noqa: F401
    export_cmd = (
        f"optimum-cli export onnx --model {OUTPUT_DIR} "
        f"--task text-classification --optimize O2 {ONNX_DIR}"
    )
    exit_code = os.system(export_cmd)
    if exit_code == 0:
        print(f"Successful. Drop the optimized binary folders from '{ONNX_DIR}' straight into your Chrome Extension directory.")
    else:
        print(f"ONNX export failed with exit code {exit_code}. PyTorch weights are still in '{OUTPUT_DIR}'.")
except ImportError:
    print("\n'optimum' library not installed. Native weights are saved.")
    print("To compile to browser-ready ONNX weights, run: pip install optimum[onnxruntime]")