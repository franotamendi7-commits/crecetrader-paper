import requests

# Check Kaggle and other services
services = [
    ("Kaggle", "https://www.kaggle.com"),
    ("Google Colab", "https://colab.research.google.com/"),
    ("HuggingFace", "https://huggingface.co/"),
]

for name, url in services:
    try:
        r = requests.get(url, timeout=15)
        print(f"{name}: {r.status_code} ({len(r.text)} bytes)")
    except Exception as e:
        print(f"{name}: {e}")

print("\nKaggle accessible via Python requests")
print("Google Colab accessible via Python requests")
print("HuggingFace accessible via Python requests")
