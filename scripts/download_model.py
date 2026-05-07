import config
import torch
from transformers import pipeline

device = 0 if torch.cuda.is_available() else -1

print("======================================")
print(" Downloading / Loading LLM Model")
print("======================================")
print(f"Model: {config.LLM_MODEL}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Device: {'GPU' if device == 0 else 'CPU'}")

generator = pipeline(
    "text-generation",
    model=config.LLM_MODEL,
    device=device
)

print("======================================")
print(" Model Loaded Successfully")
print("======================================")

output = generator(
    "Hello, this is a test.",
    max_new_tokens=10,
    pad_token_id=generator.tokenizer.eos_token_id
)

print(output)