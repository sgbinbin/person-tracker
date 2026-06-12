#!/usr/bin/env python3
"""
Convert tracker data to AI Footprints page format
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path.home() / "scripts" / "person-tracker" / "data"
OUTPUT_DIR = Path.home() / "scripts" / "person-tracker" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_tracker_data(person_id: str) -> dict:
    """Load tracker data for a person"""
    filepath = DATA_DIR / f"{person_id}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def convert_news_to_page_format(tracker_data: dict) -> list:
    """Convert tracker news to page news format"""
    if not tracker_data or "recent_news" not in tracker_data:
        return []
    
    news = []
    for article in tracker_data["recent_news"][:5]:  # Top 5 news
        # Parse date
        pub_date = article.get("published", "")
        time_str = "Recent"
        if pub_date:
            try:
                # Parse RFC 2822 date
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_date)
                now = datetime.now(dt.tzinfo)
                diff = now - dt
                
                if diff.days == 0:
                    hours = diff.seconds // 3600
                    if hours == 0:
                        minutes = diff.seconds // 60
                        time_str = f"{minutes} mins ago"
                    else:
                        time_str = f"{hours} hours ago"
                elif diff.days == 1:
                    time_str = "Yesterday"
                elif diff.days < 7:
                    time_str = f"{diff.days} days ago"
                else:
                    time_str = dt.strftime("%b %d")
            except:
                time_str = "Recent"
        
        # Extract topic from keywords
        topic = "AI News"
        title_lower = article.get("title", "").lower()
        if "nvidia" in title_lower or "chip" in title_lower or "semiconductor" in title_lower:
            topic = "Semiconductors"
        elif "ai" in title_lower or "artificial intelligence" in title_lower:
            topic = "AI Development"
        elif "stock" in title_lower or "invest" in title_lower:
            topic = "Investment"
        elif "robot" in title_lower:
            topic = "Robotics"
        
        news.append({
            "topic": {"en": topic, "ja": topic},
            "head": {
                "en": article.get("title", "")[:100],
                "ja": article.get("title", "")[:100]
            },
            "src": {"en": article.get("source", "News"), "ja": article.get("source", "News")},
            "time": {"en": time_str, "ja": time_str},
            "url": article.get("url", "")
        })
    
    return news

def convert_to_page_format(person_id: str) -> dict:
    """Convert tracker data to page format"""
    tracker_data = load_tracker_data(person_id)
    if not tracker_data:
        return None
    
    # Get insights
    insights = tracker_data.get("insights", {})
    locations = insights.get("locations", ["Unknown"])
    activities = insights.get("activities", ["Public Activities"])
    
    # Build location string
    location = locations[0] if locations else "Unknown"
    status = tracker_data.get("status", f"📍 {location}")
    
    # Get name mappings
    name_map = {
        "jensen-huang": {
            "ja": "ジェンスン・フアン",
            "zh": "黄仁勋",
            "en": "Jensen Huang",
            "ko": "젠슨 황",
            "role_ja": "NVIDIA 共同創業者 / CEO",
            "role_en": "NVIDIA Founder / CEO"
        },
        "masayoshi-son": {
            "ja": "孫正義",
            "zh": "孙正义",
            "en": "Masayoshi Son",
            "ko": "손정의",
            "role_ja": "ソフトバンクグループ 代表",
            "role_en": "SoftBank Group Chairman & CEO"
        }
    }
    
    names = name_map.get(person_id, {})
    
    result = {
        "person_id": person_id,
        "timezone": 9 if person_id == "masayoshi-son" else -7,
        "timezoneLabel": {
            "ja": "東京 JST" if person_id == "masayoshi-son" else "SF PDT",
            "en": "Tokyo JST" if person_id == "masayoshi-son" else "SF PDT"
        },
        "subject": {
            "ja": {
                "name": names.get("ja", tracker_data.get("name", "")),
                "role": names.get("role_ja", tracker_data.get("title", "")),
                "location": f"{location}",
                "status": status
            },
            "en": {
                "name": names.get("en", tracker_data.get("name", "")),
                "role": names.get("role_en", tracker_data.get("title", "")),
                "location": f"{location}",
                "status": status
            }
        },
        "news": convert_news_to_page_format(tracker_data),
        "tracked_at": tracker_data.get("tracked_at", ""),
        "news_count": tracker_data.get("news_count", 0)
    }
    
    return result

def generate_page_data():
    """Generate data for the AI Footprints page"""
    people = ["jensen-huang", "masayoshi-son"]
    
    page_data = {}
    for person_id in people:
        data = convert_to_page_format(person_id)
        if data:
            page_data[person_id] = data
    
    # Save to output
    output_file = OUTPUT_DIR / "page-data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(page_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated page data: {output_file}")
    return page_data

if __name__ == "__main__":
    generate_page_data()
