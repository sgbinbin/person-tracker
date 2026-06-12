#!/usr/bin/env python3
"""
AI Leaders Tracker - Track public figures' news, appearances, and activities
Uses patchright (undetected Playwright) for anti-detection web scraping
Includes rule-based analysis for market impact and location inference
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Import analyzer
sys.path.insert(0, str(Path(__file__).parent))
from analyzer import generate_analysis_summary, format_for_display

# Data directory
DATA_DIR = Path.home() / "scripts" / "person-tracker" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# People to track
PEOPLE = [
    {
        "id": "jensen-huang",
        "name": "Jensen Huang",
        "name_ja": "黄仁勲",
        "name_zh": "黄仁勋",
        "title": "NVIDIA CEO & Co-founder",
        "queries": [
            "Jensen Huang June 2026",
            "Jensen Huang Seoul",
            "Jensen Huang visit",
            "黄仁勲 NVIDIA"
        ]
    },
    {
        "id": "masayoshi-son",
        "name": "Masayoshi Son",
        "name_ja": "孫正義",
        "name_zh": "孙正义",
        "title": "SoftBank Group CEO",
        "queries": [
            "Masayoshi Son June 2026",
            "Masayoshi Son Tokyo",
            "Masayoshi Son visit",
            "孫正義 ソフトバンク"
        ]
    },
    {
        "id": "elon-musk",
        "name": "Elon Musk",
        "name_ja": "イーロン・マスク",
        "name_zh": "埃隆·马斯克",
        "title": "Tesla, SpaceX & xAI CEO",
        "queries": [
            "Elon Musk June 2026",
            "Elon Musk Tesla",
            "Elon Musk xAI",
            "イーロン・マスク"
        ]
    },
    {
        "id": "sam-altman",
        "name": "Sam Altman",
        "name_ja": "サム・アルトマン",
        "name_zh": "萨姆·阿尔特曼",
        "title": "OpenAI CEO",
        "queries": [
            "Sam Altman June 2026",
            "Sam Altman OpenAI",
            "Sam Altman visit",
            "サム・アルトマン OpenAI"
        ]
    },
    {
        "id": "dario-amodei",
        "name": "Dario Amodei",
        "name_ja": "ダリオ・アモデイ",
        "name_zh": "达里奥·阿莫德伊",
        "title": "Anthropic CEO",
        "queries": [
            "Dario Amodei June 2026",
            "Dario Amodei Anthropic",
            "Dario Amodei Claude",
            "ダリオ・アモデイ Anthropic"
        ]
    },
    {
        "id": "mark-zuckerberg",
        "name": "Mark Zuckerberg",
        "name_ja": "マーク・ザッカーバーグ",
        "name_zh": "马克·扎克伯格",
        "title": "Meta CEO",
        "queries": [
            "Mark Zuckerberg June 2026",
            "Mark Zuckerberg Meta",
            "Mark Zuckerberg AI",
            "マーク・ザッカーバーグ Meta"
        ]
    },
    {
        "id": "sundar-pichai",
        "name": "Sundar Pichai",
        "name_ja": "サンダー・ピチャイ",
        "name_zh": "桑达尔·皮查伊",
        "title": "Google & Alphabet CEO",
        "queries": [
            "Sundar Pichai June 2026",
            "Sundar Pichai Google",
            "Sundar Pichai AI",
            "サンダー・ピチャイ Google"
        ]
    }
]


def fetch_news_google_rss(query: str, limit: int = 10) -> list:
    """Fetch news from Google News RSS (no browser needed)"""
    import urllib.request
    import xml.etree.ElementTree as ET
    
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; PersonTracker/1.0)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
        
        root = ET.fromstring(xml_data)
        articles = []
        
        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source = item.findtext("source", "")
            description = item.findtext("description", "")[:300]
            
            articles.append({
                "title": title,
                "url": link,
                "published": pub_date,
                "source": source,
                "snippet": description
            })
        
        return articles
    except Exception as e:
        print(f"  ⚠️ Google News RSS error for '{query}': {e}")
        return []


def fetch_news_with_browser(query: str, limit: int = 10) -> list:
    """Fetch news using patchright for sites that block RSS/requests"""
    try:
        from patchright.sync_api import sync_playwright
        
        articles = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Try Google News search
            url = f"https://news.google.com/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US"
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            
            # Extract articles
            items = page.query_selector_all("article")
            for item in items[:limit]:
                try:
                    link_el = item.query_selector("a")
                    title = link_el.text_content().strip() if link_el else ""
                    href = link_el.get_attribute("href") if link_el else ""
                    if href and href.startswith("./"):
                        href = f"https://news.google.com{href[1:]}"
                    
                    source_el = item.query_selector("time")
                    pub_date = source_el.text_content().strip() if source_el else ""
                    
                    if title:
                        articles.append({
                            "title": title,
                            "url": href,
                            "published": pub_date,
                            "source": "",
                            "snippet": ""
                        })
                except:
                    continue
            
            browser.close()
            return articles
    except Exception as e:
        print(f"  ⚠️ Browser scraping error for '{query}': {e}")
        return []


def track_person(person: dict) -> dict:
    """Track a single person and return their data"""
    print(f"\n🔍 Tracking: {person['name']} ({person['title']})")
    
    all_articles = []
    
    # Fetch from multiple queries
    for query in person["queries"]:
        print(f"  📰 Fetching: {query}")
        articles = fetch_news_google_rss(query, limit=5)
        all_articles.extend(articles)
    
    # Deduplicate by title
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title_key = article["title"][:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_articles.append(article)
    
    # Sort by date (most recent first)
    unique_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    
    # Run analysis
    print(f"  🧠 Running AI analysis...")
    analysis = generate_analysis_summary(person["name"], unique_articles)
    
    # Generate status
    status = f"📍 {analysis['inferred_location']}"
    if analysis["market_impacts"]:
        top_sector = analysis["market_impacts"][0]
        status += f" · {top_sector['impact']} {top_sector['sector']}"
    
    result = {
        "person_id": person["id"],
        "name": person["name"],
        "name_local": person.get("name_ja", person.get("name_zh", "")),
        "title": person["title"],
        "tracked_at": datetime.utcnow().isoformat() + "Z",
        "news_count": len(unique_articles),
        "recent_news": unique_articles[:10],
        "analysis": {
            "key_quotes": analysis["key_quotes"],
            "market_impacts": analysis["market_impacts"],
            "inferred_location": analysis["inferred_location"],
            "location_confidence": analysis["location_confidence"]
        },
        "status": status
    }
    
    # Print summary
    print(f"  ✅ Found {len(unique_articles)} articles")
    print(f"  📍 Location: {analysis['inferred_location']} ({analysis['location_confidence']:.0%})")
    if analysis["key_quotes"]:
        print(f"  🗣 Key quotes: {len(analysis['key_quotes'])}")
    if analysis["market_impacts"]:
        print(f"  📈 Market impacts: {len(analysis['market_impacts'])} sectors")
    
    return result


def save_data(person_id: str, data: dict):
    """Save tracking data to JSON file"""
    filepath = DATA_DIR / f"{person_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved to {filepath}")


def save_history(person_id: str, data: dict):
    """Append to history file for trend tracking"""
    history_file = DATA_DIR / f"{person_id}-history.jsonl"
    entry = {
        "timestamp": data["tracked_at"],
        "news_count": data["news_count"],
        "location": data["analysis"]["inferred_location"],
        "status": data["status"]
    }
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate_combined_dashboard():
    """Generate a combined dashboard JSON for the website"""
    dashboard = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "leaders": []
    }
    
    for person in PEOPLE:
        filepath = DATA_DIR / f"{person['id']}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            dashboard["leaders"].append(data)
    
    # Save combined dashboard
    dashboard_path = DATA_DIR / "dashboard.json"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Dashboard saved to {dashboard_path}")
    return dashboard


def main():
    """Main tracking function"""
    print("=" * 60)
    print("🤖 AI Leaders Tracker (with Analysis)")
    print(f"⏰ {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # Parse arguments
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    for person in PEOPLE:
        if target != "all" and person["id"] != target:
            continue
        
        data = track_person(person)
        save_data(person["id"], data)
        save_history(person["id"], data)
        
        # Print analysis summary
        print(f"\n{'─' * 40}")
        print(format_for_display({
            "summary": f"📍 {data['analysis']['inferred_location']}",
            "key_quotes": data["analysis"]["key_quotes"],
            "market_impacts": data["analysis"]["market_impacts"]
        }))
        print(f"{'─' * 40}")
    
    # Generate combined dashboard
    dashboard = generate_combined_dashboard()
    
    print("\n" + "=" * 60)
    print("✅ Tracking complete!")
    print(f"📁 Data saved to: {DATA_DIR}")
    print("=" * 60)
    
    return dashboard


if __name__ == "__main__":
    import urllib.parse
    main()
