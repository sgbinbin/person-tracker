#!/usr/bin/env python3
"""
AI Leaders Tracker - Track public figures' news, appearances, and activities
Uses patchright (undetected Playwright) for anti-detection web scraping
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

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


def extract_location_info(articles: list) -> dict:
    """Extract location/activity information from news articles"""
    # Keywords that indicate location/travel
    location_keywords = {
        # Countries
        "japan": "Japan", "日本": "Japan",
        "korea": "South Korea", "韓国": "South Korea", "韩国": "South Korea",
        "taiwan": "Taiwan", "台湾": "Taiwan",
        "china": "China", "中国": "China",
        "usa": "USA", "united states": "USA", "美国": "USA", "米国": "USA",
        "singapore": "Singapore", "新加坡": "Singapore", "シンガポール": "Singapore",
        "india": "India", "印度": "India", "インド": "India",
        "europe": "Europe", "欧州": "Europe",
        "germany": "Germany", "ドイツ": "Germany",
        "uk": "UK", "イギリス": "UK",
        # Cities
        "taipei": "Taipei", "台北": "Taipei",
        "tokyo": "Tokyo", "東京": "Tokyo", "东京": "Tokyo",
        "seoul": "Seoul", "ソウル": "Seoul", "首尔": "Seoul",
        "beijing": "Beijing", "北京": "Beijing",
        "shanghai": "Shanghai", "上海": "Shanghai",
        "shenzhen": "Shenzhen", "深圳": "Shenzhen",
        "san jose": "San Jose", "サンノゼ": "San Jose",
        "santa clara": "Santa Clara",
        "las vegas": "Las Vegas", "ラスベガス": "Las Vegas",
        "computex": "Taipei (Computex)", "台北国际电脑展": "Taipei (Computex)",
        "ces": "Las Vegas (CES)",
        "mwc": "Barcelona (MWC)",
        "gdc": "San Francisco (GDC)",
        "siggraph": "USA (SIGGRAPH)",
    }
    
    # Activity keywords
    activity_keywords = {
        "keynote": "Keynote Speech",
        "演讲": "Keynote Speech", "基調講演": "Keynote Speech",
        "conference": "Conference", "会议": "Conference", "カンファレンス": "Conference",
        "visit": "Official Visit", "訪問": "Official Visit", "访问": "Official Visit",
        "meeting": "Meeting", "会談": "Meeting", "会见": "Meeting",
        "announce": "Product Announcement", "発表": "Product Announcement", "发布": "Product Announcement",
        "launch": "Product Launch", "発売": "Product Launch",
        "partner": "Partnership", "提携": "Partnership", "合作": "Partnership",
        "invest": "Investment", "投資": "Investment", "投资": "Investment",
        "factory": "Factory/Manufacturing", "工場": "Factory/Manufacturing", "工厂": "Factory/Manufacturing",
        "chip": "Semiconductor", "半導体": "Semiconductor", "芯片": "Semiconductor",
        "ai": "AI Development", "人工知能": "AI Development", "人工智能": "AI Development",
    }
    
    locations = []
    activities = []
    
    for article in articles:
        text = f"{article['title']} {article['snippet']}".lower()
        
        # Check for locations
        for keyword, location in location_keywords.items():
            if keyword in text and location not in locations:
                locations.append(location)
        
        # Check for activities
        for keyword, activity in activity_keywords.items():
            if keyword in text and activity not in activities:
                activities.append(activity)
    
    return {
        "locations": locations[:5],  # Top 5 locations
        "activities": activities[:5]  # Top 5 activities
    }


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
    
    # Extract location/activity info
    insights = extract_location_info(unique_articles)
    
    result = {
        "person_id": person["id"],
        "name": person["name"],
        "name_local": person.get("name_ja", person.get("name_zh", "")),
        "title": person["title"],
        "tracked_at": datetime.utcnow().isoformat() + "Z",
        "news_count": len(unique_articles),
        "recent_news": unique_articles[:10],
        "insights": insights,
        "status": generate_status(insights)
    }
    
    print(f"  ✅ Found {len(unique_articles)} articles")
    print(f"  📍 Locations: {', '.join(insights['locations'][:3]) or 'Unknown'}")
    print(f"  🎯 Activities: {', '.join(insights['activities'][:3]) or 'Unknown'}")
    
    return result


def generate_status(insights: dict) -> str:
    """Generate a human-readable status string"""
    location = insights["locations"][0] if insights["locations"] else "Unknown"
    activity = insights["activities"][0] if insights["activities"] else "Public Activities"
    
    return f"📍 {location} · {activity}"


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
        "locations": data["insights"]["locations"],
        "activities": data["insights"]["activities"],
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
    print("🤖 AI Leaders Tracker")
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
