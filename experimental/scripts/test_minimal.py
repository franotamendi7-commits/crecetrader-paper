import json, base64, time, requests

img_path = "/Users/franciscootamendi/YouTubeTradingAgent/frames/scene_004_303.7s.jpg"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {
    "model": "qwen3.5:9b-mlx",
    "messages": [{"role": "user", "content": "What do you see?", "images": [img_b64]}],
    "stream": False
}

t0 = time.time()
resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=600)
elapsed = time.time() - t0
print(f"Time: {elapsed:.1f}s")
if resp.status_code == 200:
    print(resp.json().get("message", {}).get("content", "")[:300])
else:
    print(f"Error: {resp.status_code}")