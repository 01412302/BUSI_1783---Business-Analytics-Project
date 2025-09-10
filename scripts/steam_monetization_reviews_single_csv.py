#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
steam_monetization_reviews_single_csv.py

Collect Steam user reviews for popular monetization-heavy games
and save EVERYTHING into a single CSV.

- Uses Steam public "appreviews" endpoint (no API key needed)
- Cursor-based pagination
- Adds a monetization_flag column using the same keyword regex
- Includes app metadata columns (appid, app_name, monetization_model)
- Writes exactly ONE CSV

Usage:
  python steam_monetization_reviews_single_csv.py \\
    --per-game 4000 --lang english --outpath data/steam_reviews/all_reviews.csv
"""

import os
import time
import argparse
import json
import html
import re
from datetime import datetime
from dateutil import tz

import requests
import pandas as pd
from tqdm import tqdm

STEAM_APPREVIEWS_URL = "https://store.steampowered.com/appreviews/{appid}"

# Curated list of monetization-heavy, popular F2P titles on Steam.
APP_LIST = [
    {"appid": 570, "name": "Dota 2", "model": "cosmetics, battle pass, event monetization"},
    {"appid": 730, "name": "Counter-Strike 2", "model": "cosmetics (cases/skins), keys"},
    {"appid": 440, "name": "Team Fortress 2", "model": "cosmetics, crates/keys"},
    {"appid": 230410, "name": "Warframe", "model": "cosmetics, boosters, premium currency"},
    {"appid": 238960, "name": "Path of Exile", "model": "cosmetics, stash tabs, MTX"},
    {"appid": 1085660, "name": "Destiny 2", "model": "expansions, season pass, cosmetics, silver"},
    {"appid": 1172470, "name": "Apex Legends", "model": "battle pass, cosmetics, event packs"},
    {"appid": 578080, "name": "PUBG: BATTLEGROUNDS", "model": "cosmetics, passes, crates"},
    {"appid": 1599340, "name": "Lost Ark", "model": "cosmetics, boosters, crystalline aura"},
]

# Monetization keywords
MONETIZATION_KEYWORDS = [
    r"\bloot\s*box(es)?\b",
    r"\bgacha\b",
    r"\bmicro[-\s]?transaction(s)?\b",
    r"\bmtx\b",
    r"\bbattle\s*pass(es)?\b",
    r"\bseason\s*pass(es)?\b",
    r"\bpay\s*to\s*win\b",
    r"\bp2w\b",
    r"\bmonetiz(e|ation|ed|ing)\b",
    r"\bcosmetic(s)?\b",
    r"\bskins?\b",
    r"\bcrates?\b",
    r"\bkeys?\b",
    r"\bpremium\s*(currency|shop)\b",
    r"\bstore\b",
]
MONETIZATION_REGEX = re.compile("|".join(MONETIZATION_KEYWORDS), re.IGNORECASE)

HEADERS = {
    "User-Agent": "MonetizationResearchBot/1.0 (contact: your_email@example.com)"
}

def ensure_dir_for_file(path: str):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

def fmt_ts(ts):
    if not ts:
        return None
    return datetime.utcfromtimestamp(ts).replace(tzinfo=tz.UTC).isoformat()

def fetch_reviews_for_app(
    appid: int,
    max_reviews: int = 4000,
    language: str = "english",
    purchase_type: str = "all",
    filter_type: str = "recent",
    sleep_sec: float = 1.0,
    timeout: int = 20,
) -> list:
    """Retrieve up to max_reviews reviews for a given appid via cursor pagination."""
    cursor = "*"
    grabbed = 0
    all_reviews = []

    with tqdm(total=max_reviews, desc=f"Fetching {appid}", unit="rev") as pbar:
        while grabbed < max_reviews:
            params = {
                "json": 1,
                "language": language,
                "purchase_type": purchase_type,
                "filter": filter_type,
                "num_per_page": 100,
                "cursor": cursor,
            }
            try:
                resp = requests.get(
                    STEAM_APPREVIEWS_URL.format(appid=appid),
                    params=params,
                    headers=HEADERS,
                    timeout=timeout,
                )
                if resp.status_code != 200:
                    time.sleep(2.5)
                    continue
                data = resp.json()
            except Exception:
                time.sleep(2.5)
                continue

            reviews = (data or {}).get("reviews", [])
            if not reviews:
                break

            all_reviews.extend(reviews)
            grabbed += len(reviews)
            pbar.update(len(reviews))

            new_cursor = (data or {}).get("cursor")
            if not new_cursor or new_cursor == cursor:
                break
            cursor = new_cursor
            time.sleep(sleep_sec)

            if grabbed >= max_reviews:
                break

    return all_reviews[:max_reviews]

def normalize_review_record(app_meta: dict, r: dict) -> dict:
    """Flatten + clean fields for analysis and add app metadata."""
    author = r.get("author", {}) or {}
    raw_text = r.get("review", "") or ""
    text = html.unescape(raw_text).replace("\r\n", "\n").strip()

    row = {
        "platform": "steam",
        "appid": app_meta["appid"],
        "app_name": app_meta["name"],
        "monetization_model": app_meta.get("model", ""),
        "recommendation_id": r.get("recommendationid"),
        "language": r.get("language"),
        "review_text": text,
        "timestamp_created": fmt_ts(r.get("timestamp_created")),
        "timestamp_updated": fmt_ts(r.get("timestamp_updated")),
        "voted_up": r.get("voted_up"),
        "votes_up": r.get("votes_up"),
        "votes_funny": r.get("votes_funny"),
        "weighted_vote_score": r.get("weighted_vote_score"),
        "steam_purchase": r.get("steam_purchase"),
        "received_for_free": r.get("received_for_free"),
        "written_during_early_access": r.get("written_during_early_access"),
        "author_steamid": author.get("steamid"),
        "author_num_games_owned": author.get("num_games_owned"),
        "author_num_reviews": author.get("num_reviews"),
        "author_playtime_forever_m": author.get("playtime_forever"),
        "author_playtime_last_two_weeks_m": author.get("playtime_last_two_weeks"),
        "author_playtime_at_review_m": author.get("playtime_at_review"),
        "author_last_played": author.get("last_played"),
    }
    row["monetization_flag"] = bool(MONETIZATION_REGEX.search(text)) if text else False
    return row

def main():
    ap = argparse.ArgumentParser(description="Download Steam reviews into a SINGLE CSV file.")
    ap.add_argument("--per-game", type=int, default=4000, help="Max reviews per game.")
    ap.add_argument("--lang", type=str, default="english", help="Language (e.g., english, all).")
    ap.add_argument("--purchase-type", type=str, default="all", choices=["all", "steam"], help="Purchase type filter.")
    ap.add_argument("--filter-type", type=str, default="recent", choices=["recent", "updated", "all"], help="Review filter.")
    ap.add_argument("--sleep", type=float, default=1.0, help="Seconds between requests.")
    ap.add_argument("--outpath", type=str, default="data/steam_reviews/all_reviews.csv", help="Single CSV output path.")
    ap.add_argument("--save-metadata-json", type=str, default=None, help="Optional: path to save metadata JSON.")
    args = ap.parse_args()

    ensure_dir_for_file(args.outpath)
    all_rows = []

    metadata = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "platform": "steam",
        "language": args.lang,
        "purchase_type": args.purchase_type,
        "filter_type": args.filter_type,
        "per_game_max": args.per_game,
        "apps": [],
        "notes": "Single-file dataset for research on ethical & profitable monetization models.",
    }

    for app in APP_LIST:
        appid, app_name = app["appid"], app["name"]
        print(f"\n=== {app_name} ({appid}) ===")
        raw = fetch_reviews_for_app(
            appid=appid,
            max_reviews=args.per_game,
            language=args.lang,
            purchase_type=args.purchase_type,
            filter_type=args.filter_type,
            sleep_sec=args.sleep,
        )
        rows = [normalize_review_record(app, r) for r in raw]
        all_rows.extend(rows)

        metadata["apps"].append({
            "appid": appid,
            "name": app_name,
            "monetization_model": app.get("model", ""),
            "rows_collected": len(rows),
        })

        time.sleep(max(1.0, args.sleep))

    df = pd.DataFrame(all_rows)
    df.to_csv(args.outpath, index=False, encoding="utf-8")
    print(f"\nSaved single CSV: {args.outpath} ({len(df)} rows)")

    if args.save_metadata_json:
        ensure_dir_for_file(args.save_metadata_json)
        with open(args.save_metadata_json, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"Saved metadata JSON: {args.save_metadata_json}")

    print("\nDone. Next steps:")
    print("- EDA across app_name and monetization_flag.")
    print("- Sentiment & topic modeling; compare by monetization_flag, game, and time.")
    print("- Optionally drop/anonymize author_steamid before sharing.")

if __name__ == "__main__":
    main()
