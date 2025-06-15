# stats.py
import json
import os

STATS_FILE = "user_stats.json"
user_stats = {}

def load_stats():
    global user_stats
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            user_stats = json.load(f)

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(user_stats, f, ensure_ascii=False, indent=2)

def get_user_stats(user_id: int) -> dict:
    uid = str(user_id)
    if uid not in user_stats:
        user_stats[uid] = {
            "miner": 0,
            "coin": 0,
            "guess": 0,
            "rps": 0
        }
    return user_stats[uid]