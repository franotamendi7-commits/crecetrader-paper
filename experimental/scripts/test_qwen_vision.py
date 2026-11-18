import json, base64, time, requests

img_path = "/Users/franciscootamendi/YouTubeTradingAgent/frames/scene_004_303.7s.jpg"
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

prompt = "Describe this trading chart image. What instrument, timeframe, indicators, and price levels are visible?"

payload = {
    "model": "qwen3.5:9b-mlx",
    "messages": [{"role": "user", "content": prompt, "images": [img_b64]}],
    "stream": False
}

t0 = time.time()
resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=300)
elapsed = time.time() - t0

if resp.status_code == 200:
    answer = resp.json().get("message", {}).get("content", "")
    print(f"Time: {elapsed:.1f}s")
    print(f"Response:\n{answer}")
else:
    print(f"Error: {resp.status_code} - {resp.text}")
PYEOF