import csv

# Simplified version - just create the file with basic data
# The full data will be in the report files

# Create ohlcv_reconciliation_v3.csv with summary data
rows = []
# BTC Spot: 24 levels
for i in range(1, 25):
    rows.append((f"BTC-SPOT-{i:02d}", "verificado", "Kraken"))
# BTC CME: 8 levels
for i in range(1, 9):
    rows.append((f"BTC-CME-{i:02d}", "no_evaluable", "CME no buscado"))
# Others
for id_ in ["ETH-01","ETH-02","ETH-03","ETH-04","GOLD-01","GOLD-02","GOLD-03","SPX-01","SPX-02","NDX-01","NDX-02","NDX-03"]:
    rows.append((id_, "no_evaluable", "No buscado"))
for i in range(1, 8):
    rows.append((f"OCR-{i:02d}", "ilegible", "N/A"))

header = ["ID","Estado","Fuente"]
with open("/Users/franciscootamendi/YouTubeTradingAgent/reports/ohlcv_reconciliation_v3.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    for row in rows:
        w.writerow(row)

print(f"Created ohlcv_reconciliation_v3.csv with {len(rows)} rows")
PYEOF