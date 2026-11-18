import json
from collections import Counter

mem = json.load(open("/Users/franciscootamendi/YouTubeTradingAgent/experimental/memory/memory.json"))

print("=== MEMORY SUMMARY ===")
print(f"Version: {mem['version']}")
print(f"Created: {mem['created_at']}")
print()

for mod, data in mem["modules"].items():
    entries = data["entries"]
    print(f"[{mod}] {len(entries)} entradas:")
    for e in entries:
        print(f"  - {e['id']} | {e['clasificacion']} | {e['estado']} | {e['descripcion'][:70]}...")

print()
print("=== ESTADOS ===")
all_estados = []
for mod, data in mem["modules"].items():
    for e in data["entries"]:
        all_estados.append(e.get("estado", "?"))
print(Counter(all_estados))

print()
print("=== CLASIFICACIONES ===")
all_clas = []
for mod, data in mem["modules"].items():
    for e in data["entries"]:
        all_clas.append(e.get("clasificacion", "?"))
print(Counter(all_clas))

print()
print("=== ENTRADAS POR VIDEO ===")
video_count = {}
for mod, data in mem["modules"].items():
    for e in data["entries"]:
        vid = e.get("fuente_video_ids", [])
        for v in vid:
            video_count[v] = video_count.get(v, 0) + 1
print(video_count)
