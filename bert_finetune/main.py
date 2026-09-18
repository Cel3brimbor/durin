import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
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
OUTPUT_DIR = "./pytorch_distilbert_model"
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

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy_metric.compute(predictions=predictions, references=labels)

#fine tuning params
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=4,
    weight_decay=0.01,
    logging_steps=5,
    load_best_model_at_end=True,
    use_cpu=False if torch.backends.mps.is_available() else True,
    #logging_steps=1,
    disable_tqdm=False,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    compute_metrics=compute_metrics,
)

print("Launching local pytorch neural network training runtime...")
trainer.train()

print(f"Exporting trained PyTorch configurations to: {OUTPUT_DIR}")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("Initiating hugging face optimum compilation pipeline for browser deployment...")
try:
    import optimum
    # Using O2 optimization tags tells Optimum to explicitly output a browser-ready quantized web format
    os.system(f"optimum-cli export onnx --model {OUTPUT_DIR} --optimize O2 {ONNX_DIR}")
    print(f"Successful. Drop the optimized binary folders from '{ONNX_DIR}' straight into your Chrome Extension directory.")
except ImportError:
    print("\n'optimum' library not installed. Native weights are saved.")
    print("To compile to browser-ready ONNX weights, run: pip install optimum[onnxruntime]")