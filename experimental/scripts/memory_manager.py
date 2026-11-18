"""
Memory Manager v1.0 — CreceTrader Methodological Memory
========================================================
Arquitectura:
- memory.json: base de conocimiento acumulativa (structurada)
- Cada entrada: {id, descripcion, categoria, clasificacion, fuentes[], evidencia, confianza, soporte, estado}
- Memory Manager controla carga/descarga (model_manager.py)
- Solo texto: Qwen3.5:9b-mlx (Memory Manager)

Módulos:
  1. filosofia        - Cómo interpreta CreceTrader el mercado
  2. multitemporal    - Semanal, Diario, 4H, Intradía
  3. tendencias       - Dirección, estructura, rupturas, confirmaciones
  4. estructuras      - Soportes, resistencias, BOS, order blocks, Fibonacci
  5. operaciones      - Condiciones de entrada, invalidación, posicion
  6. activos          - BTC spot, CME futures, ETH, S&P500, Nasdaq, Gold
  7. comparaciones    - Patrones recurrentes entre videos

Clasificaciones epistemológicas:
  [DICHO]      : afirmación explícita del analista
  [OBSERVADO]  : información directamente visible en el gráfico
  [INFERIDO]   : interpretación derivada de la evidencia
  [NO VERIFICADO]: información que no puede confirmarse

Estados:
  provisional  : primera evidencia
  respaldado   : 2+ videos independientes
  contradictorio: dos videos dan criterios diferentes
  descartado   : evidencia insuficiente o superada

Versionado:
  Cada actualización conserva historial de cambios.
  La memoria crece sin reconstruirse desde cero.
"""

import json
import os
import time
import uuid

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
MEMORY_FILE = f"{BASE}/experimental/memory/memory.json"
LOG_FILE = f"{BASE}/experimental/logs/memory_manager.log"

# Módulos de la memoria
MODULES = [
    "filosofia",
    "multitemporal",
    "tendencias",
    "estructuras",
    "operaciones",
    "activos",
    "comparaciones"
]

# Clasificaciones epistemológicas
CLASSIFICATIONS = ["DICHO", "OBSERVADO", "INFERIDO", "NO VERIFICADO"]

# Estados
STATES = ["provisional", "respaldado", "contradictorio", "descartado"]

def load_memory():
    """Carga la memoria desde memoria.json"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
    return {
        "version": "1.0.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modules": {m: {"entries": [], "version": "1.0.0"} for m in MODULES},
        "historial": [
            {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "action": "creado", "entries": 0}
        ]
    }

def save_memory(memory):
    """Guarda la memoria en memoria.json"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    log(f"Memoria guardada: {len(memory['modules']['filosofia']['entries'])} entries totales")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}\n")

def add_entry(module, entry):
    """Añade una entrada a un módulo"""
    memory = load_memory()
    entry_id = str(uuid.uuid4())[:8].upper()
    # Deduplicate source videos
    source_vids = list(dict.fromkeys(entry.get("fuente_video_ids", [])))
    entry["fuente_video_ids"] = source_vids
    entry["id"] = entry_id
    entry["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    entry["source_video_ids"] = list(set(entry.get("source_video_ids", [])))
    
    memory["modules"][module]["entries"].append(entry)
    save_memory(memory)
    memory["historial"].append({
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": "entrada_añadida",
        "module": module,
        "entry_id": entry_id,
        "entries": len(memory["modules"][module]["entries"])
    })
    log(f"Entrada {entry_id} añadida al módulo {module}")
    return entry_id

def get_entries(module, category=None):
    """Recupera entradas de un módulo"""
    memory = load_memory()
    entries = memory["modules"][module]["entries"]
    if category:
        entries = [e for e in entries if e.get("category") == category]
    return entries

def compare_videos(video_ids):
    """Compara entradas entre videos"""
    memory = load_memory()
    results = {}
    for vid in video_ids:
        results[vid] = []
        for mod in MODULES:
            for entry in memory["modules"][mod]["entries"]:
                if vid in entry.get("fuente_video_ids", []):
                    results[vid].append(entry)
    return results

def verify_entry(entry):
    """Verifica la estructura de una entrada"""
    required = ["id", "descripcion", "categoria", "clasificacion", "fuente_video_ids", "evidencia"]
    for r in required:
        if r not in entry:
            return False, f"Falta campo: {r}"
    if entry["clasificacion"] not in CLASSIFICATIONS:
        return False, f"Clasificación inválida: {entry['clasificacion']}"
    if entry.get("soporte", 0) < 1:
        return False, "Soporte debe ser >= 1"
    return True, "OK"

def suggest_move_to_respaldado(module, entry_id, memory):
    """Mueve una entrada a estado respaldado si tiene 2+ fuentes"""
    entries = memory["modules"][module]["entries"]
    for e in entries:
        if e["id"] == entry_id and e.get("soporte", 0) >= 2:
            e["estado"] = "respaldado"
            e["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            save_memory(memory)
            return True
    return False

def export_report():
    """Exporta reporte de la memoria"""
    memory = load_memory()
    report = {
        "version": memory["version"],
        "total_entries": sum(len(m["entries"]) for m in memory["modules"].values()),
        "per_module": {},
        "estados": {},
        "clasificaciones": {}
    }
    for mod, data in memory["modules"].items():
        report["per_module"][mod] = len(data["entries"])
        for e in data["entries"]:
            est = e.get("estado", "provisional")
            report["estados"][est] = report["estados"].get(est, 0) + 1
            cl = e.get("clasificacion", "NO VERIFICADO")
            report["clasificaciones"][cl] = report["clasificaciones"].get(cl, 0) + 1
    return report
