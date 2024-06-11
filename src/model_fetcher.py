import os
from pathlib import Path
from huggingface_hub import snapshot_download, login
from transformers import AutoTokenizer, AutoModelForCausalLM
from .config import huggingface_token

# Log in to Hugging Face using your API key
login(token=huggingface_token)

# Define the paths where models will be saved
codestral_model_path = Path.home().joinpath('models', 'Codestral-22B-v0.1')
mistral_model_path = Path.home().joinpath('models', 'Mistral-7B-Instruct-v0.3')

# Ensure directories exist
codestral_model_path.mkdir(parents=True, exist_ok=True)
mistral_model_path.mkdir(parents=True, exist_ok=True)

# Download Codestral-22B model and tokenizer
print("Downloading Codestral-22B model and tokenizer...")
AutoTokenizer.from_pretrained("mistralai/Codestral-22B-v0.1", cache_dir=codestral_model_path)
AutoModelForCausalLM.from_pretrained("mistralai/Codestral-22B-v0.1", cache_dir=codestral_model_path)

# Download Mistral-7B model files
print("Downloading Mistral-7B model files...")
snapshot_download(repo_id="mistralai/Mistral-7B-Instruct-v0.3", local_dir=mistral_model_path)

print("Download complete.")
