import json, os, time, subprocess, base64, requests

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
PROGRESS_FILE = f"{BASE}/experimental/results/historical_progress.json"
PROCESSED_DIR = f"{BASE}/experimental/results/historical"
RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UC4DOPLw9NRRBFW4wYjcWxiA"

os.makedirs(PROCESSED_DIR, exist_ok=True)

# Load progress
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        return json.load(open(PROGRESS_FILE))
    return {"processed": [], "pending": [], "last_check": None}

def save_progress(p):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2, ensure_ascii=False)

def fetch_rss_videos():
    import xml.etree.ElementTree as ET
    import urllib.request
    try:
        with urllib.request.urlopen(RSS_URL, timeout=15) as resp:
            root = ET.fromstring(resp.read())
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        videos = []
        for e in root.findall('atom:entry', ns):
            id_el = e.find('atom:id', ns)
            title_el = e.find('atom:title', ns)
            pub_el = e.find('atom:published', ns)
            vid = id_el.text.replace('yt:video:', '') if id_el is not None and id_el.text else ''
            title = title_el.text if title_el is not None and title_el.text else ''
            published = pub_el.text if pub_el is not None and pub_el.text else ''
            videos.append({"id": vid, "title": title, "published": published})
        return videos
    except Exception as e:
        print(f"RSS error: {e}")
        return []

def download_video(video_id):
    """Download video and extract frames"""
    video_dir = f"{BASE}/data_hist/{video_id}"
    frames_dir = f"{BASE}/frames_hist/{video_id}"
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)
    
    video_path = f"{video_dir}/{video_id}.mp4"
    if not os.path.exists(video_path):
        subprocess.run(["yt-dlp", "-f", "best[height<=720]", "-o", video_path, 
            f"https://www.youtube.com/watch?v={video_id}"], capture_output=True, timeout=300)
    
    if not os.path.exists(video_path):
        return None, None
    
    # Extract frames at 1/30s (fewer frames for historical)
    frame_count = len(os.listdir(frames_dir)) if os.path.exists(frames_dir) else 0
    if frame_count == 0:
        subprocess.run(["ffmpeg", "-i", video_path, "-vf", "fps=1/30", "-q:v", "2", 
            f"{frames_dir}/frame_%04d.jpg"], capture_output=True, timeout=120)
    
    return video_path, frames_dir

def extract_transcript(video_id):
    """Extract transcript using yt-dlp"""
    transcript_path = f"{BASE}/data_hist/{video_id}/{video_id}_transcript.json"
    if os.path.exists(transcript_path):
        return json.load(open(transcript_path))
    
    # Try yt-dlp subtitle extraction
    subprocess.run(["yt-dlp", "--write-auto-sub", "--sub-lang", "es,en", "--skip-download",
        "-o", f"{BASE}/data_hist/{video_id}/{video_id}", 
        f"https://www.youtube.com/watch?v={video_id}"], capture_output=True, timeout=120)
    
    # Parse subtitle file if exists
    sub_files = [f for f in os.listdir(f"{BASE}/data_hist/{video_id}") if f.endswith('.vtt') or f.endswith('.srt')]
    if sub_files:
        # Simple VTT to text conversion
        with open(f"{BASE}/data_hist/{video_id}/{sub_files[0]}") as f:
            lines = f.readlines()
        text = "\n".join(l.strip() for l in lines if l.strip() and not l.startswith('WEBVTT') and '-->' not in l)
        transcript = {"segments": [{"text": text}], "full_text": text}
        with open(transcript_path, "w") as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        return transcript
    return None

def analyze_frame(img_path):
    """Analyze a single frame with qwen2.5vl (vision-only, no transcription)"""
    import base64
    prompt = """Analyze this trading chart. Return ONLY:
INSTRUMENT: (BTCUSD, ETHUSD, ES, NQ, XAUUSD, AMD, or UNKNOWN)
TIMEFRAME: (Weekly, Daily, 4H, 1H, 15m, 5m, or UNKNOWN)
PRICES: [list visible prices or null]
STRUCTURE: (trend, range, support, resistance, or UNKNOWN)
INDICATORS: (MA, Fibonacci, Volume, or none)"""
    
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    payload = {"model": "qwen2.5vl:3b", "messages": [
        {"role": "user", "content": prompt, "images": [img_b64]}
    ], "stream": False, "options": {"temperature": 0.1}}
    
    try:
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        if resp.status_code == 200:
            return resp.json()["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"
    return "ERROR: unknown"

def process_video(video_id, title, published):
    """Process a single historical video"""
    print(f"\n{'='*60}")
    print(f"Processing: {title} ({video_id})")
    print(f"Published: {published}")
    print(f"{'='*60}")
    
    result_file = f"{PROCESSED_DIR}/{video_id}_analysis.json"
    if os.path.exists(result_file):
        print("Already processed, skipping.")
        return json.load(open(result_file))
    
    # Download video
    print("Downloading video...")
    video_path, frames_dir = download_video(video_id)
    if not video_path:
        print("Failed to download video")
        return None
    
    # Extract transcript
    print("Extracting transcript...")
    transcript = extract_transcript(video_id)
    
    # Process frames (max 20 per video to save time)
    frames = sorted(os.listdir(frames_dir))[:20]
    frame_results = []
    for i, frame in enumerate(frames):
        img_path = os.path.join(frames_dir, frame)
        print(f"  Frame {i+1}/{len(frames)}: {frame}...")
        vision = analyze_frame(img_path)
        frame_results.append({
            "frame": frame,
            "frame_idx": i,
            "vision": vision
        })
        time.sleep(2)
    
    # Build result
    result = {
        "video_id": video_id,
        "title": title,
        "published": published,
        "processed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "frames_processed": len(frame_results),
        "frame_results": frame_results,
        "transcript_available": transcript is not None,
        "transcript_segments": len(transcript.get("segments", [])) if transcript else 0
    }
    
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(frame_results)} frames. Saved to {result_file}")
    return result

def main():
    progress = load_progress()
    processed_ids = set(progress.get("processed", []))
    
    # Fetch RSS videos
    videos = fetch_rss_videos()
    print(f"Found {len(videos)} videos in RSS feed")
    
    # Filter unprocessed
    pending = [v for v in videos if v["id"] not in processed_ids]
    print(f"Pending: {len(pending)} (already processed: {len(processed_ids)})")
    
    # Sort by published date (newest first)
    pending.sort(key=lambda x: x["published"], reverse=True)
    
    # Process up to 3 videos per run (to avoid overloading)
    MAX_VIDEOS_PER_RUN = 3
    for video in pending[:MAX_VIDEOS_PER_RUN]:
        result = process_video(video["id"], video["title"], video["published"])
        if result:
            progress["processed"].append(video["id"])
            save_progress(progress)
            print(f"Progress saved: {len(progress['processed'])} processed")
    
    progress["last_check"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
    save_progress(progress)
    
    print(f"\n{'='*60}")
    print(f"Run complete. Processed: {len(progress['processed'])}")
    print(f"Pending: {len(pending) - min(MAX_VIDEOS_PER_RUN, len(pending))}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()