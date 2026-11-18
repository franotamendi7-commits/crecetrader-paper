import json, time, requests, os, subprocess
from datetime import datetime

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
OLLAMA_URL = "http://localhost:11434"

MODELS = {
    "youtube_analyst": {
        "name": "qwen2.5vl:3b",
        "size_gb": 3.2,
        "function": "audiovisual_analysis",
        "capabilities": ["vision", "text"]
    },
    "memory_manager": {
        "name": "qwen3.5:9b-mlx",
        "size_gb": 8.9,
        "function": "memory_consolidation",
        "capabilities": ["text", "reasoning"]
    }
}

LOG_FILE = f"{BASE}/experimental/logs/model_manager.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_ram_usage():
    try:
        result = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split("\n")
        page_size = 16384
        for line in lines:
            if "page size" in line.lower():
                parts = line.split()
                for p in parts:
                    if p.isdigit():
                        page_size = int(p)
                        break
        free = 0
        inactive = 0
        for line in lines:
            if "Pages free" in line:
                free = int(line.split()[2].rstrip("."))
            elif "Pages inactive" in line:
                inactive = int(line.split()[2].rstrip("."))
        available_gb = round((free + inactive) * page_size / (1024**3), 1)
        total_gb = 24.0
        used_gb = round(total_gb - available_gb, 1)
        return {"total_gb": total_gb, "used_gb": used_gb, "available_gb": available_gb, "percent": round(used_gb/total_gb*100, 1)}
    except Exception:
        return {"total_gb": 24.0, "used_gb": 0, "available_gb": 24.0, "percent": 0}

def get_loaded_models():
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/ps", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("models", [])
            return [m.get("name", "") for m in models]
    except Exception as e:
        log(f"Error checking loaded models: {e}")
    return []

def unload_model(model_name):
    log(f"Unloading model: {model_name}")
    ram_before = get_ram_usage()
    try:
        payload = {"model": model_name, "keep_alive": 0}
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=30)
        log(f"Unload response: {resp.status_code}")
    except Exception as e:
        log(f"Unload error (may be normal): {e}")
    time.sleep(5)
    ram_after = get_ram_usage()
    log(f"RAM before: {ram_before['used_gb']}GB, after: {ram_after['used_gb']}GB (freed: {round(ram_before['used_gb'] - ram_after['used_gb'], 1)}GB)")
    loaded = get_loaded_models()
    if model_name in loaded:
        log(f"WARNING: {model_name} still loaded!")
        return False
    else:
        log(f"SUCCESS: {model_name} unloaded")
        return True

def load_model(model_name):
    log(f"Loading model: {model_name}")
    ram_before = get_ram_usage()
    t0 = time.time()
    try:
        payload = {"model": model_name, "prompt": "hi", "stream": False, "options": {"num_predict": 1}}
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        elapsed = time.time() - t0
        if resp.status_code == 200:
            ram_after = get_ram_usage()
            log(f"Model loaded in {elapsed:.1f}s. RAM: {ram_before['used_gb']}GB -> {ram_after['used_gb']}GB")
            return True
        else:
            log(f"Load failed: {resp.status_code} - {resp.text[:200]}")
            return False
    except Exception as e:
        log(f"Load error: {e}")
        return False

def ensure_model(model_key):
    target_model = MODELS[model_key]["name"]
    log(f"Ensuring model: {model_key} ({target_model})")
    loaded = get_loaded_models()
    log(f"Currently loaded: {loaded}")
    for key, info in MODELS.items():
        if key != model_key and info["name"] in loaded:
            log(f"Unloading {info['name']} (not needed)")
            unload_model(info["name"])
    loaded = get_loaded_models()
    if target_model not in loaded:
        success = load_model(target_model)
        if not success:
            log(f"FAILED to load {target_model}")
            return False
    else:
        log(f"{target_model} already loaded")
    return True

def get_model_status():
    loaded = get_loaded_models()
    status = {}
    for key, info in MODELS.items():
        status[key] = {
            "name": info["name"],
            "loaded": info["name"] in loaded,
            "function": info["function"],
            "size_gb": info["size_gb"]
        }
    return status

def run_with_model(model_key, task_func, *args, **kwargs):
    log(f"=== Starting task with {model_key} ===")
    ram_start = get_ram_usage()
    if not ensure_model(model_key):
        log(f"Failed to load {model_key}")
        return None
    t0 = time.time()
    try:
        result = task_func(*args, **kwargs)
        elapsed = time.time() - t0
        log(f"Task completed in {elapsed:.1f}s")
    except Exception as e:
        elapsed = time.time() - t0
        log(f"Task failed after {elapsed:.1f}s: {e}")
        result = None
    model_name = MODELS[model_key]["name"]
    unload_model(model_name)
    ram_end = get_ram_usage()
    log(f"RAM: {ram_start['used_gb']}GB -> {ram_end['used_gb']}GB")
    log(f"=== Task with {model_key} complete ===\n")
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: model_manager.py [status|load <model>|unload <model>|ensure <model>]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "status":
        status = get_model_status()
        for key, info in status.items():
            print(f"{key}: {info['name']} - {'LOADED' if info['loaded'] else 'not loaded'} ({info['size_gb']}GB)")
        ram = get_ram_usage()
        print(f"RAM: {ram['used_gb']}/{ram['total_gb']}GB ({ram['percent']}%)")
    elif cmd == "load" and len(sys.argv) > 2:
        load_model(sys.argv[2])
    elif cmd == "unload" and len(sys.argv) > 2:
        unload_model(sys.argv[2])
    elif cmd == "ensure" and len(sys.argv) > 2:
        ensure_model(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")