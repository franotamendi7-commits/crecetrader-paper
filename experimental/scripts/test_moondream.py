import moondream as md
import json
import time
from PIL import Image

model = md.vl(local=True, model="moondream2")
print("Model loaded")

img = Image.open("/Users/franciscootamendi/YouTubeTradingAgent/frames/scene_004_303.7s.jpg")
print("Image loaded:", img.size)

t0 = time.time()
enc = model.encode_image(img)
print("Image encoded in", round(time.time()-t0, 2), "s")

questions = [
    "What instrument is shown in this chart?",
    "What timeframe is visible?",
    "Are there candlesticks visible?",
    "Are there any horizontal lines?",
    "What price values can be read?",
]

for q in questions:
    t0 = time.time()
    ans = model.query(enc, q)["answer"]
    print(f"\nQ: {q}")
    print(f"A: {ans}")
    print(f"Time: {round(time.time()-t0, 2)}s")
PYEOF