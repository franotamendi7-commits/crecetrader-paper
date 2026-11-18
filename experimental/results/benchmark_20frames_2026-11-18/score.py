#!/usr/bin/env python3
"""Scorer del benchmark de lectura de graficos.

Lee manifest.json + results.jsonl y calcula por modelo:
- JSON valido
- instrumento y timeframe correctos
- error de precio actual (crudo y normalizado por escala)
- recall de niveles (match dentro de tolerancia)
- niveles alucinados (sin match)
- latencia, tokens y costo estimado

Uso:
  python3 score.py
  python3 score.py --out results.jsonl
"""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

BASE = Path("/Users/franciscootamendi/YouTubeTradingAgent")
OUT = BASE / "experimental/results/benchmark_20frames_2026-11-18"

# Precios publicos aproximados (USD por 1M tokens), Gemini 2.5 Flash.
COST_IN = 0.30
COST_OUT = 2.50

INSTRUMENT_ALIASES = {
    "BTCUSD": "BTCUSD",
    "BTC": "BTCUSD",
    "BTCUSDT": "BTCUSD",
    "ETHUSD": "ETHUSD",
    "ETH": "ETHUSD",
    "ETHUSDT": "ETHUSD",
    "ES1!": "ES1!",
    "ES": "ES1!",
    "SPX": "ES1!",
    "US500": "ES1!",
    "GC1!": "GC1!",
    "GC": "GC1!",
    "GOLD": "GC1!",
    "XAUUSD": "GC1!",
    "VX1!": "VX1!",
    "VIX": "VX1!",
    "USTECH": "USTECH",
    "NAS100": "USTECH",
    "NDX": "USTECH",
}


def norm_instrument(x):
    if not isinstance(x, str):
        return None
    return INSTRUMENT_ALIASES.get(x.strip().upper(), x.strip().upper())


def norm_timeframe(x):
    if not isinstance(x, str):
        return None
    t = x.strip().upper().replace(" ", "")
    if t in ("MULTI", "MULTIPLE", "MULTITF"):
        return "multi"
    if t in ("1D", "D", "DAILY", "1DAY"):
        return "1D"
    if t in ("4H", "240", "240M"):
        return "4H"
    if t in ("1H", "60", "60M"):
        return "1H"
    if t in ("1W", "W", "WEEKLY", "1WEEK"):
        return "1W"
    if t in ("5M", "5MIN"):
        return "5m"
    return t


def safe_float(x):
    if isinstance(x, (int, float)) and math.isfinite(x):
        return float(x)
    return None


def rel_err(actual, expected):
    a = safe_float(actual)
    if a is None or not expected:
        return None
    return abs(a - expected) / abs(expected)


def scale_normalized_err(actual, expected):
    """Error ignorando potencia de 10 (detecta 'decimal mal puesto')."""
    a = safe_float(actual)
    if a is None or not expected or a == 0:
        return None
    r = abs(a) / abs(expected)
    k = 10 ** round(math.log10(r))
    return abs(a / k - expected) / abs(expected)


def level_matches(levels, expected_levels, tol):
    """Devuelve (recall, precision, alucinados, faltantes)."""
    got = [float(x) for x in (levels or []) if safe_float(x) is not None]
    exp = [float(x) for x in (expected_levels or []) if safe_float(x) is not None]
    if not exp:
        return None, None, [], []
    used = set()
    hits = 0
    for e in exp:
        best = None
        for i, g in enumerate(got):
            if i in used:
                continue
            # match exacto o por escala (decimal movido)
            r = abs(g - e) / abs(e) if e else 1
            rs = scale_normalized_err(g, e)
            if r <= tol:
                best = i
                break
            if rs is not None and rs <= tol and best is None:
                best = i
        if best is not None:
            used.add(best)
            hits += 1
    matched = len(used)
    halluc = [g for i, g in enumerate(got) if i not in used]
    missing = [e for e in exp if not any(
        (abs(g - e) / abs(e) <= tol if e else False) or
        (scale_normalized_err(g, e) is not None and scale_normalized_err(g, e) <= tol)
        for g in got
    )]
    recall = matched / len(exp)
    precision = matched / len(got) if got else 0.0
    return recall, precision, halluc, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT / "results.jsonl"))
    ap.add_argument("--tol", type=float, default=0.01,
                    help="tolerancia relativa para niveles (default 1%%)")
    ap.add_argument("--json", default=str(OUT / "scores.json"))
    args = ap.parse_args()

    manifest = json.loads((OUT / "manifest.json").read_text())
    frames = {f["id"]: f for f in manifest["frames"]}

    records = []
    for line in Path(args.out).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except Exception:
            pass

    by_model = defaultdict(list)
    for r in records:
        by_model[r["model"]].append(r)

    summary = {}
    print(f"{'modelo':24s} {'n':>2s} {'json%':>6s} {'instr%':>7s} {'tf%':>5s} "
          f"{'err_med':>8s} {'err_norm':>9s} {'recall':>7s} {'aluc':>5s} "
          f"{'lat_s':>7s} {'tok_in':>7s} {'tok_out':>8s} {'usd':>6s}")
    for model, recs in sorted(by_model.items()):
        n = len(recs)
        valid = [r for r in recs if r.get("parsed")]
        nvalid = len(valid)
        instr_ok = tf_ok = 0
        price_errs, price_norm_errs, recalls, halluc_counts = [], [], [], []
        lat = tok_in = tok_out = 0.0
        cost = 0.0
        fails = []
        for r in recs:
            fr = frames.get(r["frame_id"])
            if not fr:
                continue
            exp = fr["expected"]
            m = r.get("parsed") or {}
            lat += r.get("latency_s") or 0
            u = r.get("usage") or {}
            if r["model"].startswith("gemini"):
                ti = u.get("promptTokenCount") or 0
                to = u.get("candidatesTokenCount") or 0
                cost += (ti * COST_IN + to * COST_OUT) / 1e6
            else:
                ti = u.get("prompt_eval_count") or 0
                to = u.get("eval_count") or 0
            tok_in += ti
            tok_out += to
            if not m:
                fails.append((r["frame_id"], "json", None))
                continue
            if norm_instrument(m.get("instrument")) == norm_instrument(exp["instrument"]):
                instr_ok += 1
            else:
                fails.append((r["frame_id"], "instrumento",
                              f"{m.get('instrument')} != {exp['instrument']}"))
            if norm_timeframe(m.get("timeframe")) == norm_timeframe(exp["timeframe"]):
                tf_ok += 1
            else:
                fails.append((r["frame_id"], "tf",
                              f"{m.get('timeframe')} != {exp['timeframe']}"))
            pe = rel_err(m.get("current_price"), exp["current_price"])
            pne = scale_normalized_err(m.get("current_price"), exp["current_price"])
            if pe is not None:
                price_errs.append(pe)
            if pne is not None:
                price_norm_errs.append(pne)
                if pe is not None and pe > 0.01:
                    fails.append((r["frame_id"], "precio",
                                  f"{m.get('current_price')} vs {exp['current_price']}"
                                  f" (norm_err={pne:.4f})"))
            rec, prec, hall, miss = level_matches(m.get("levels"), exp.get("levels"), args.tol)
            if rec is not None:
                recalls.append(rec)
                halluc_counts.append(len(hall))
                if rec < 0.5:
                    fails.append((r["frame_id"], "niveles",
                                  f"recall={rec:.2f}, faltan={miss[:4]}"))
        def med(xs):
            if not xs:
                return float("nan")
            xs = sorted(xs)
            mid = len(xs) // 2
            return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2
        s = {
            "n": n,
            "json_valid": nvalid,
            "json_valid_pct": round(100 * nvalid / n, 1) if n else 0,
            "instrument_acc_pct": round(100 * instr_ok / n, 1) if n else 0,
            "timeframe_acc_pct": round(100 * tf_ok / n, 1) if n else 0,
            "price_median_rel_err": round(med(price_errs), 4) if price_errs else None,
            "price_scale_norm_median_err": round(med(price_norm_errs), 4) if price_norm_errs else None,
            "price_within_1pct_pct": round(100 * sum(1 for e in price_errs if e <= 0.01) / n, 1) if n else 0,
            "levels_recall_median": round(med(recalls), 3) if recalls else None,
            "hallucinated_levels_avg": round(sum(halluc_counts) / len(halluc_counts), 2) if halluc_counts else None,
            "latency_s_avg": round(lat / n, 2) if n else 0,
            "tokens_in_avg": round(tok_in / n, 0) if n else 0,
            "tokens_out_avg": round(tok_out / n, 0) if n else 0,
            "est_usd_total": round(cost, 4),
            "fails": fails,
        }
        summary[model] = s
        print(f"{model:24s} {n:2d} {s['json_valid_pct']:6.1f} "
              f"{s['instrument_acc_pct']:7.1f} {s['timeframe_acc_pct']:5.1f} "
              f"{(s['price_median_rel_err'] or 0):8.4f} "
              f"{(s['price_scale_norm_median_err'] or 0):9.4f} "
              f"{(s['levels_recall_median'] or 0):7.2f} "
              f"{(s['hallucinated_levels_avg'] or 0):5.1f} "
              f"{s['latency_s_avg']:7.2f} {s['tokens_in_avg']:7.0f} "
              f"{s['tokens_out_avg']:8.0f} {s['est_usd_total']:6.3f}")

    Path(args.json).write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nDetalle por frame en {args.json}")
    for model, s in summary.items():
        if s["fails"]:
            print(f"\nFallos {model}:")
            for fid, kind, det in s["fails"]:
                print(f"  {fid:30s} {kind:12s} {det}")


if __name__ == "__main__":
    main()
