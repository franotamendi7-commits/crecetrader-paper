import os
import sys
from huggingface_hub import hf_hub_download

print(f"Python: {sys.version}")
print("=== Qwen3-VL-2B-Instruct ===")
model_path = hf_hub_download(
    repo_id="Qwen/Qwen3-VL-2B-Instruct",
    filename="model.safetensors",
    local_dir="./models/qwen3vl_2b",
    local_dir_use_symlinks=False
)
print(f"Model file: {model_path}")
print(f"Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")

license_path = hf_hub_download(
    repo_id="Qwen/Qwen3-VL-2B-Instruct",
    filename="LICENSE",
    local_dir="./models/qwen3vl_2b",
    local_dir_use_symlinks=False
)
print(f"License exists: {os.path.exists(license_path)}")
print(f"License: {open(license_path).read()[:200]}")

print("\n=== RESUMEN ===")
print(f"Qwen3-VL-2B: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
print("Descarga completada correctamente.")
