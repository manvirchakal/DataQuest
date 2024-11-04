import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
from trl import SFTTrainer

# Load dataset
dataset = load_dataset("gretelai/synthetic_text_to_sql")

# Print all columns
print(dataset['train'].column_names)

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load base model with quantization
base_model_id = "meta-llama/Llama-3.2-3B-Instruct"

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Prepare model for k-bit training
model = prepare_model_for_kbit_training(model)

# Get PEFT model
peft_config = LoraConfig(
    r=64,  # Rank
    lora_alpha=16,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)
model = get_peft_model(model, peft_config)

# Format dataset - simplified instruction format
def format_instruction_with_context(example):
    return {
        "text": f"""[INST]SQL Context: {example['sql_context']}
Question: {example['sql_prompt']}[/INST]
```sql
{example['sql']}
```
"""
    }

# Format the dataset
formatted_dataset = dataset.map(format_instruction_with_context)

# Training arguments with reduced learning rate for fine-tuning
training_args = TrainingArguments(
    output_dir="./sql-assistant-gretel",
    num_train_epochs=2,  # Reduced epochs since model is already finetuned
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    gradient_checkpointing=True,
    optim="paged_adamw_32bit",
    logging_steps=10,
    learning_rate=1e-4,  # Reduced learning rate
    fp16=True,
    max_grad_norm=0.3,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    save_strategy="epoch",
)

# Initialize trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=formatted_dataset["train"],
    args=training_args,
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=2048,
)

# Train
trainer.train()

# Save the model
trainer.save_model("sql-assistant-gretel") 