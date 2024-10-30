import torch
from transformers import AutoModelForCausalLM

model_id = "mistralai/Mistral-Nemo-Instruct-2407"

# Add this before creating device_map to print model structure
model_test = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype=torch.float16,
)

# Print layer structure
for name, _ in model_test.named_modules():
    print(name)

# Delete test model to free memory
del model_test
torch.cuda.empty_cache()