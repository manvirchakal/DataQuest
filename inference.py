import torch
from transformers import pipeline, BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer

# Use GPU and verify
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

model_id = "meta-llama/Llama-3.2-1B-Instruct"

# Load model and tokenizer separately
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16,
    quantization_config=quantization_config,
)
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Create pipeline with pre-loaded model and tokenizer
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto",
)

# Verify model device
print(f"Model is on: {next(pipe.model.parameters()).device}")

# Format the prompt correctly for Llama
prompt = """<s>[INST] <<SYS>>
You are a pirate chatbot who always responds in pirate speak!
<</SYS>>

Who are you? [/INST]
"""

outputs = pipe(
    prompt,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)
print(outputs[0]["generated_text"])
