"""
Memory Manager - tests for CREARETRATOR memory
Tests: recover, consistency, contradictions, classification
"""

import json
import sys
sys.path.insert(0, "/Users/franciscootamendi/YouTubeTradingAgent/experimental/scripts")
from memory_manager import load_memory, save_memory, get_entries, verify_entry, compare_videos, export_report

memory = load_memory()

print("=" * 60)
print("TEST 1: RECUPERAR UNA REGLA Y MOSTRAR SUS FUENTES")
print("=" * 60)
for mod in ["filosofia", "tendencias", "activos"]:
    entries = get_entries(mod)
    for e in entries:
        print(f"\n  {e['id']} | {e['categoria']} | {e['clasificacion']} | {e['descripcion'][:80]}...")
        print(f"    Fuente: {e.get('fuente_video_ids', [])}")
        print(f"    Evidencia: {e.get('evidencia', '')[:100]}...")
        print(f"    Estado: {e.get('estado')} | Soporte: {e.get('soporte', 0)}")

print("\n" + "=" * 60)
print("TEST 2: COMPARAR DOS VIDEOS")
print("=" * 60)
results = compare_videos(["subONxt5iag", "o6n6UDNVtCk"])
print(f"\n  Videos comparados: subONxt5iag, o6n6UDNVtCk")
for vid, entries in results.items():
    print(f"\n    {vid}: {len(entries)} entradas")
    for e in entries[:2]:
        print(f"      - {e['id']}: {e['descripcion'][:70]}... [{e.get('estado','?')}]")

print("\n" + "=" * 60)
print("TEST 3: IDENTIFICAR CONTRADICCIONES")
print("=" * 60)
# Check: o6n6UDNVtCk vs 0prmrS6nnRk - different price levels for BTC
for mod in ["tendencias", "activos"]:
    entries = get_entries(mod)
    for e in entries:
        if e.get("fuente_video_ids") and len(e["fuente_video_ids"]) >= 2:
            print(f"\n  {mod} -> {e['id']}: {e['descripcion'][:80]}")
            print(f"    Fuente: {e.get('fuente_video_ids')}")
            print(f"    Estado: {e.get('estado')} | Soporte: {e.get('soporte', 0)}")

print("\n" + "=" * 60)
print("TEST 4: DIFERENCIAR OBSERVACIÓN ISALTADA DE PATRÓN RECURRENTE")
print("=" * 60)
# subONxt5iag appears 6 times, o6n6UDNVtCk appears 3 times
# Patterns: subONxt5iag + 0prmrS6nnRk = 2 videos = respaldado
for mod in ["comparaciones"]:
    entries = get_entries(mod)
    print(f"\n  {[mod]} - {len(entries)} entradas")
    for e in entries:
        print(f"    - {e['id']}: {e['descripcion'][:80]}... [{e.get('estado','?')}]")
        print(f"      Fuente: {e.get('fuente_video_ids')}")

print("\n" + "=" * 60)
print("TEST 5: VOLVER A CARGAR Y VERIFICAR CONSISTENCIA")
print("=" * 60)
memory2 = load_memory()
total = sum(len(m["entries"]) for m in memory2["modules"].values())
print(f"  Total entries after reload: {total}")
print(f"  All modules present: {all(m in memory2['modules'] for m in ['filosofia','multitemporal','tendencias','estructuras','operaciones','activos','comparaciones'])}")

print("\n" + "=" * 60)
print("TEST 6: VISA DE FUENTES DUPLICADAS")
print("=" * 60)
violations = 0
for mod, data in memory2["modules"].items():
    seen = set()
    for e in data["entries"]:
        for vid in e.get("fuente_video_ids", []):
            if vid in seen:
                print(f"  WARNING: {e['id']} references {vid} twice in {mod}")
                violations += 1
            seen.add(vid)
print(f"  Duplications: {violations}")

print("\n" + "=" * 60)
print("TEST 7: VISA DE HISTORIAL DE CAMBIOS")
print("=" * 60)
print(f"\n  Historial de cambios:")
for h in memory2["historial"]:
    print(f"    {h['at']}: {h['action']} ({h.get('entries',0)} entries)")

print("\n" + "=" * 60)
print("TEST 8: VISA DE EXPORTACION")
print("=" * 60)
report = export_report()
print(f"\n  Total entradas: {report['total_entries']}")
print(f"  Por módulo: {report['per_module']}")
print(f"  Estados: {report['estados']}")
print(f"  Clasificaciones: {report['clasificaciones']}")
