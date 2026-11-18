"""
Memory Initializer v1.0
Extrae conocimiento de los 4 videos procesados y lo carga en la memoria.
"""

import json
import os
import re
import sys
sys.path.insert(0, "/Users/franciscootamendi/YouTubeTradingAgent/experimental/scripts")
from memory_manager import load_memory, save_memory, add_entry, log, MODULES, CLASSIFICATIONS, STATES

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
hist_dir = f"{BASE}/experimental/results/historical"

# Cargar resultados
videos = {}
for f in os.listdir(hist_dir):
    if f.endswith("_analysis.json"):
        d = json.load(open(os.path.join(hist_dir, f)))
        videos[d["video_id"]] = d

# Extract structured info from frames
def extract_frame_info(vision_str):
    """Extrae estructura de una respuesta de visión"""
    if not vision_str or not isinstance(vision_str, str):
        return {}
    lines = vision_str.strip().split("\n")
    info = {}
    for line in lines:
        if line.startswith("INSTRUMENT:"):
            info["instrument"] = line.split(":",1)[1].strip()
        elif line.startswith("TIMEFRAME:"):
            info["timeframe"] = line.split(":",1)[1].strip()
        elif line.startswith("PRICES:"):
            p_str = line.split(":",1)[1].strip()
            p_str = p_str.strip("[]")
            info["prices"] = [p.strip() for p in p_str.split(",") if p.strip()]
        elif line.startswith("STRUCTURE:"):
            info["structure"] = line.split(":",1)[1].strip()
        elif line.startswith("INDICATORS:"):
            info["indicators"] = line.split(":",1)[1].strip()
    return info

# Extract price mentions from transcripts
def extract_prices_from_transcript(video_id):
    """Extrae precios mencionados en la transcripción"""
    t_path = f"{BASE}/data_hist/{video_id}/{video_id}_transcript.json"
    if not os.path.exists(t_path):
        return []
    text = open(t_path).read()
    # Remove VTT tags
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'<c>', ' ', text)
    # Find price patterns (numbers with thousands separators)
    prices = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', text)
    # Convert to floats (remove commas unless decimal)
    result = []
    for p in prices:
        p_clean = p.replace(".", "").replace(",", ".")
        try:
            result.append(float(p_clean))
        except:
            pass
    return result

def extract_asset_mentions(video_id):
    """Extrae instrumentos mencionados en la transcripción"""
    t_path = f"{BASE}/data_hist/{video_id}/{video_id}_transcript.json"
    if not os.path.exists(t_path):
        return []
    text = open(t_path).read()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'<c>', ' ', text)
    assets = re.findall(r'(Bitcoin|BTC|ETH|SP500|NASDAQ|QQQ|Oro|GOLD|AMD|Intel|Nvidia|XAU|Plata)', text)
    return list(set(assets))

# Build initial knowledge base
knowledge = []

# Reference videos
video_refs = {
    "subONxt5iag": {"title": "Bitcoin aguanta pese a las salidas de los ETFs", "date": "2026-11-10"},
    "rTtXDLq2kOQ": {"title": "Bitcoin y los futuros de Chicago", "date": "2026-11-09"},
    "o6n6UDNVtCk": {"title": "Bitcoin en zona de compras, pero yo no compro aquí", "date": "2026-11-07"},
    "0prmrS6nnRk": {"title": "Bitcoin cae un 5,9% y se frena en 75.518", "date": "2026-11-06"},
}

# Module 1: Filosofía
print("=== Módulo filosofía ===")
philosophy_entries = [
    {
        "descripcion": "CreceTrader acompaña tendencias y no fuerza operaciones en rangos prolongados",
        "categoria": "tendencias",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["subONxt5iag", "o6n6UDNVtCk"],
        "evidencia": "En subONxt5iag: 'Sigue estando en esa zona de compra'; en o6n6UDNVtCk: 'no compro aquí'",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
    {
        "descripcion": "Los analistas no se centran solo en un gráfico: consideran tiempo-frame, 4H, 5 min",
        "categoria": "filosofia",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["subONxt5iag", "rTtXDLq2kOQ", "0prmrS6nnRk"],
        "evidencia": "En subONxt5iag: 'time frames' mencionados; en rTtXDLq2kOQ: 'día, 4h o 5 minutos'",
        "confianza": "alta",
        "soporte": 3,
        "estado": "respaldado"
    },
]

# Module 2: Estructuras
print("=== Módulo estructuras ===")
estructura_entries = [
    {
        "descripcion": "Mínimos de BTC en 71.000-69.000 en temporalidad alta (subONxt5iag)",
        "categoria": "estructuras",
        "clasificacion": "OBSERVADO",
        "fuente_video_ids": ["subONxt5iag"],
        "evidencia": "Frames 12, 13 (Weekly): 83.422 a 50.000; Frame 15 (Daily): 88.775 a 62.000",
        "confianza": "media",
        "soporte": 1,
        "estado": "provisional"
    },
    {
        "descripcion": "Mínimo 75.518 como nivel de apoyo en BTC (0prmrS6nnRk)",
        "categoria": "estructuras",
        "clasificacion": "OBSERVADO",
        "fuente_video_ids": ["0prmrS6nnRk"],
        "evidencia": "Frame 17 (Daily): 75.885 a 77.241",
        "confianza": "media",
        "soporte": 1,
        "estado": "provisional"
    },
]

# Module 3: Tendencias
print("=== Módulo tendencias ===")
tendencia_entries = [
    {
        "descripcion": "BTC show trend in Weekly (subONxt5iag)",
        "categoria": "tendencias",
        "clasificacion": "OBSERVADO",
        "fuente_video_ids": ["subONxt5iag"],
        "evidencia": "Frame 12 (Weekly): 83.422 down to 50.000, structure: trend",
        "confianza": "media",
        "soporte": 1,
        "estado": "provisional"
    },
    {
        "descripcion": "BTC en range en temporalidades inferiores (0prmrS6nnRk)",
        "categoria": "tendencias",
        "clasificacion": "OBSERVADO",
        "fuente_video_ids": ["0prmrS6nnRk"],
        "evidencia": "Frames 7, 10 (Daily): 77-80k range; Frame 11 (4H): 80-83k",
        "confianza": "media",
        "soporte": 2,
        "estado": "provisional"
    },
    {
        "descripcion": "Subida de SP500 impulsada por compra de acciones (rTtXDLq2kOQ)",
        "categoria": "tendencias",
        "clasificacion": "OBSERVADO",
        "fuente_video_ids": ["rTtXDLq2kOQ"],
        "evidencia": "Transcript: 'compras de acciones que ha hecho subir al SP500 y al Nasdaq'",
        "confianza": "alta",
        "soporte": 1,
        "estado": "provisional"
    },
]

# Module 4: Operaciones
print("=== Módulo operaciones ===")
operacion_entries = [
    {
        "descripcion": "Condición de entrada: zona de compras con apoyo verificado",
        "categoria": "operaciones",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["subONxt5iag", "o6n6UDNVtCk"],
        "evidencia": "subONxt5iag: 'zona de compras'; o6n6UDNVtCk: 'no compro aquí'",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
    {
        "descripcion": "Condición de entrada: AMD con volumen por encima de su media (rTtXDLq2kOQ)",
        "categoria": "operaciones",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["rTtXDLq2kOQ"],
        "evidencia": "Frame 19 (Daily): AMD 2479.6; transcript: 'AMD con subida de 13%'",
        "confianza": "media",
        "soporte": 1,
        "estado": "provisional"
    },
]

# Module 5: Activos
print("=== Módulo activos ===")
activo_entries = [
    {
        "descripcion": "BTC spot vs CME futures: diferencias de comportamiento",
        "categoria": "activos",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["rTtXDLq2kOQ"],
        "evidencia": "Transcript: 'no ha tenido esa gran caída en el spot, pero sí en los futuros'",
        "confianza": "alta",
        "soporte": 1,
        "estado": "provisional"
    },
    {
        "descripcion": "S&P 500 (ES): refugio a mediano plazo en 7.592",
        "categoria": "activos",
        "clasificacion": "OBSERVADO",
        "fuente_video_ids": ["rTtXDLq2kOQ"],
        "evidencia": "Frames 12, 14 (Daily): 7.592, 7.794, 7.691, 7.482, 7.371",
        "confianza": "media",
        "soporte": 1,
        "estado": "provisional"
    },
]

# Module 6: Compara
print("=== Módulo comparaciones ===")
comparacion_entries = [
    {
        "descripcion": "Patrón: BTC en range en temporalidad diaria, en trend en semanal",
        "categoria": "comparaciones",
        "clasificacion": "INFERIDO",
        "fuente_video_ids": ["subONxt5iag", "0prmrS6nnRk"],
        "evidencia": "subONxt5iag: Weekly trend (83.4k-50k), Daily range; 0prmrS6nnRk: Daily range, Weekly missing",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
    {
        "descripcion": "Cambio de niveles: 75.518 era soporte en 06/11, ya no mencionado en 07/11",
        "categoria": "comparaciones",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["0prmrS6nnRk", "o6n6UDNVtCk"],
        "evidencia": "0prmrS6nnRk: 'se frena en 75.518'; o6n6UDNVtCk: no menciona 75.518",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
    {
        "descripcion": "AMD: activo de corto plazo con volumen por encima de media",
        "categoria": "comparaciones",
        "clasificacion": "INFERIDO",
        "fuente_video_ids": ["rTtXDLq2kOQ", "0prmrS6nnRk"],
        "evidencia": "rTtXDLq2kOQ: AMD subida 13% y mantenimiento; 0prmrS6nnRk: AMD frame references",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
]

# Add all entries to memory
id_map = {}
for mod, entries in [
    ("filosofia", philosophy_entries),
    ("estructuras", estructura_entries),
    ("tendencias", tendencia_entries),
    ("operaciones", operacion_entries),
    ("activos", activo_entries),
    ("comparaciones", comparacion_entries),
]:
    for e in entries:
        eid = add_entry(mod, e)
        id_map[mod] = id_map.get(mod, {})
        id_map[mod][e["descripcion"][:50]] = eid

# Add multitemporal module entries
print("=== Módulo multitemporal ===")
multitemporal_entries = [
    {
        "descripcion": "Temporalidad semanal: contexto de tendencia principal",
        "categoria": "multitemporal",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["subONxt5iag", "o6n6UDNVtCk"],
        "evidencia": "subONxt5iag: Frame 12 (Weekly); o6n6UDNVtCk: Frame 10 (Weekly)",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
    {
        "descripcion": "Temporalidad diaria: desarrollo de la tendencia y niveles",
        "categoria": "multitemporal",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["subONxt5iag", "0prmrS6nnRk"],
        "evidencia": "subONxt5iag: Frames 14-19 (Daily); 0prmrS6nnRk: Frames 12-19 (Daily)",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
    {
        "descripcion": "Temporalidad 4H: estructura operativa y confirmaciones",
        "categoria": "multitemporal",
        "clasificacion": "DICHO",
        "fuente_video_ids": ["0prmrS6nnRk", "rTtXDLq2kOQ"],
        "evidencia": "0prmrS6nnRk: Frame 11 (4H); rTtXDLq2kOQ: Frames 11-15 (4H)",
        "confianza": "media",
        "soporte": 2,
        "estado": "respaldado"
    },
]
for e in multitemporal_entries:
    add_entry("multitemporal", e)

# Save memory
memory = load_memory()
with open(f"{BASE}/experimental/memory/memory.json", "w") as f:
    json.dump(memory, f, indent=2, ensure_ascii=False)

# Summary
print(f"\n=== RESUMEN ===")
for mod in MODULES:
    count = len(memory["modules"][mod]["entries"])
    print(f"  {mod}: {count} entradas")
total = sum(len(m["entries"]) for m in memory["modules"].values())
print(f"  TOTAL: {total} entradas")
print(f"\nMemoria guardada en: {BASE}/experimental/memory/memory.json")
