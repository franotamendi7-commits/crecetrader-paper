#!/usr/bin/env python3
"""
Fetch BTC/USD OHLCV data from Kraken API.

Fetches daily (interval 1440) and 4-hour (interval 240) bars for the XBTUSD pair.
Saves the data to data/ohlcv_daily.json and data/ohlcv_4h.json.

Usage:
    python src/fetch_ohlcv.py

Dependencies:
    - Uses only stdlib (urllib.request). No external dependencies required.
"""

import datetime
import json
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# Kraken API endpoint for OHLCV data
KRAKEN_API_URL = "https://api.kraken.com/0/public/OHLC"

# Trading pair and intervals
# Kraken uses XXBTZUSD as the pair symbol (XBT = Bitcoin, ZUSD = USD with Z prefix)
PAIR = "XXBTZUSD"
INTERVAL_DAILY = 1440  # 1 day = 24 hours, in minutes
INTERVAL_4H = 240      # 4 hours, in minutes

# Output paths
BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DAILY_FILE = DATA_DIR / "ohlcv_daily.json"
FOUR_H_FILE = DATA_DIR / "ohlcv_4h.json"


def fetch_ohlcv(interval: int) -> list[dict]:
    """
    Fetch OHLCV data from Kraken API for a given interval.

    Args:
        interval: Trading interval in minutes (1440 for daily, 240 for 4H).

    Returns:
        A list of dictionaries with keys: timestamp, open, high, low, close, volume.

    Raises:
        SystemExit: If the API request fails or data is unavailable.
    """
    url = f"{KRAKEN_API_URL}?pair={PAIR}&interval={interval}"

    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as e:
        print(f"❌ HTTP error fetching {interval}-min data: {e.code} {e.reason}")
        sys.exit(1)
    except URLError as e:
        print(f"❌ URL error fetching {interval}-min data: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error fetching {interval}-min data: {e}")
        sys.exit(1)

    # Parse JSON response
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        sys.exit(1)

    # Check for API errors
    if "error" in data and data["error"]:
        print(f"❌ Kraken API returned errors: {data['error']}")
        sys.exit(1)

    # Extract the pair result from Kraken's response
    pair_data = data.get("result", {}).get(PAIR)

    if not pair_data:
        print(f"❌ No OHLCV data found for {PAIR} with interval {interval}")
        sys.exit(1)

    # Kraken returns candles as: [timestamp, open, high, low, close, volume, ...]
    # We keep: timestamp, open, high, low, close, volume
    candles = []
    for candle in pair_data:
        if len(candle) < 6:
            print(f"⚠️  Unexpected candle format: {candle}")
            continue
        ts = candle[0]
        # Convert Unix timestamp (milliseconds) to ISO format string
        try:
            # Kraken returns timestamps in seconds (some endpoints use ms)
            # We'll handle both: if > 1e12, treat as ms; otherwise as seconds
            if ts > 1e12:
                dt = datetime.datetime.fromtimestamp(ts / 1000.0)
            else:
                dt = datetime.datetime.fromtimestamp(ts)
            timestamp_str = dt.isoformat()
        except (ValueError, OSError) as e:
            print(f"⚠️  Could not parse timestamp {ts}: {e}")
            continue

        candle_dict = {
            "timestamp": timestamp_str,
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
        }
        candles.append(candle_dict)

    return candles


def save_to_json(data: list[dict], filepath) -> None:
    """Save OHLCV data to a JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Data saved to {filepath}")
    except Exception as e:
        print(f"❌ Failed to save data to {filepath}: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point: fetch daily and 4H OHLCV data and save to JSON files."""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Fetching BTC/USD OHLCV data from Kraken API")
    print("=" * 60)

    # Fetch daily bars (interval 1440 = 1 day)
    print(f"\n📡 Fetching daily (interval={INTERVAL_DAILY}) bars for {PAIR}...")
    daily_data = fetch_ohlcv(INTERVAL_DAILY)
    save_to_json(daily_data, DAILY_FILE)

    # Fetch 4H bars (interval 240 = 4 hours)
    print(f"\n📡 Fetching 4H (interval={INTERVAL_4H}) bars for {PAIR}...")
    four_h_data = fetch_ohlcv(INTERVAL_4H)
    save_to_json(four_h_data, FOUR_H_FILE)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Pair: {PAIR}")
    print(f"Daily bars fetched: {len(daily_data)}")
    print(f"  - First candle: {daily_data[0]['timestamp'] if daily_data else 'N/A'}")
    print(f"  - Last candle: {daily_data[-1]['timestamp'] if daily_data else 'N/A'}")
    print(f"4H bars fetched: {len(four_h_data)}")
    print(f"  - First candle: {four_h_data[0]['timestamp'] if four_h_data else 'N/A'}")
    print(f"  - Last candle: {four_h_data[-1]['timestamp'] if four_h_data else 'N/A'}")
    print(f"\nFiles saved:")
    print(f"  - {DAILY_FILE}")
    print(f"  - {FOUR_H_FILE}")
    print(f"\n✅ Done!")


if __name__ == "__main__":
    main()