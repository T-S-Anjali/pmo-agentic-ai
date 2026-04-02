"""
LoRA Fine-tuning Script for Hugging Face Transformers

This script demonstrates how to fine-tune a base model with LoRA on your own data.
Update the DATA_PATH, MODEL_NAME, and output_dir as needed.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, TextDataset, DataCollatorForLanguageModeling
from peft import get_peft_model, LoraConfig, TaskType

# --- CONFIG ---
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"  # or any compatible base model
DATA_PATH = "./data/finetune.txt"  # Your training data (plain text)
OUTPUT_DIR = "./lora_adapter_out"

# LoRA config
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, device_map="auto")

# Prepare dataset
train_dataset = TextDataset(
    tokenizer=tokenizer,
    file_path=DATA_PATH,
    block_size=128,
)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False
)

# Apply LoRA
model = get_peft_model(model, lora_config)

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=1,
    per_device_train_batch_size=2,
    save_steps=100,
    save_total_limit=2,
    logging_steps=10,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=data_collator,
)

trainer.train()

print(f"LoRA adapter saved to {OUTPUT_DIR}")
