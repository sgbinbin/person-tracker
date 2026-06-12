#!/usr/bin/env python3
"""
AI News Analyzer - Rule-based analysis layer
Extracts key quotes, market impact, and location from news articles
"""

import re
from typing import Dict, List, Tuple


# Market impact mapping: keyword → (sector, impact_type, confidence)
MARKET_IMPACT_KEYWORDS = {
    # Semiconductors / HBM
    "hbm": ("存储芯片/HBM", "利好", 0.9),
    "hbm4": ("存储芯片/HBM", "利好", 0.95),
    "hbm3e": ("存储芯片/HBM", "利好", 0.9),
    "memory": ("存储芯片", "利好", 0.7),
    "dram": ("存储芯片/DRAM", "利好", 0.8),
    "nand": ("存储芯片/NAND", "利好", 0.7),
    "semiconductor": ("半导体", "利好", 0.8),
    "chip": ("芯片", "利好", 0.7),
    "芯片": ("芯片", "利好", 0.8),
    "半導体": ("半导体", "利好", 0.8),
    
    # AI / Compute
    "ai": ("AI/算力", "利好", 0.6),
    "artificial intelligence": ("AI/算力", "利好", 0.7),
    "gpu": ("GPU/算力", "利好", 0.85),
    "cuda": ("NVIDIA生态", "利好", 0.8),
    "inference": ("AI推理", "利好", 0.75),
    "training": ("AI训练", "利好", 0.75),
    "data center": ("数据中心", "利好", 0.8),
    "cloud": ("云计算", "利好", 0.7),
    "sovereign ai": ("主权AI", "利好", 0.85),
    "ai factory": ("AI工厂/算力", "利好", 0.9),
    "compute": ("算力", "利好", 0.7),
    "人工知能": ("AI", "利好", 0.6),
    "人工智能": ("AI", "利好", 0.6),
    
    # Robotics / Physical AI
    "robot": ("机器人", "利好", 0.75),
    "robotics": ("机器人", "利好", 0.8),
    "physical ai": ("物理AI/机器人", "利好", 0.85),
    "humanoid": ("人形机器人", "利好", 0.8),
    "自動運転": ("自动驾驶", "利好", 0.8),
    "autonomous": ("自动驾驶", "利好", 0.8),
    
    # Specific companies
    "nvidia": ("NVIDIA", "关注", 0.9),
    "samsung": ("三星", "关注", 0.85),
    "sk hynix": ("SK海力士", "关注", 0.85),
    "tsmc": ("台积电", "关注", 0.85),
    "台積電": ("台积电", "关注", 0.85),
    "intel": ("Intel", "关注", 0.7),
    "amd": ("AMD", "关注", 0.7),
    "microsoft": ("微软", "关注", 0.7),
    "google": ("Google", "关注", 0.7),
    "meta": ("Meta", "关注", 0.7),
    "amazon": ("Amazon/AWS", "关注", 0.7),
    "apple": ("苹果", "关注", 0.7),
    "naver": ("Naver", "关注", 0.8),
    "lg": ("LG", "关注", 0.7),
    "hyundai": ("现代", "关注", 0.7),
    "softbank": ("软银", "关注", 0.85),
    "ソフトバンク": ("软银", "关注", 0.85),
    
    # Partnerships / Deals
    "partner": ("合作", "利好", 0.7),
    "partnership": ("合作", "利好", 0.75),
    "deal": ("交易", "利好", 0.7),
    "collaborate": ("合作", "利好", 0.7),
    "提携": ("合作", "利好", 0.7),
    "合作": ("合作", "利好", 0.7),
    
    # Investment / Factory
    "invest": ("投资", "利好", 0.75),
    "investment": ("投资", "利好", 0.75),
    "factory": ("建厂", "利好", 0.8),
    "fab": ("晶圆厂", "利好", 0.85),
    "manufacturing": ("制造", "利好", 0.7),
    "投資": ("投资", "利好", 0.75),
    "工場": ("工厂", "利好", 0.7),
    
    # Negative signals
    "ban": ("制裁", "利空", 0.8),
    "restrict": ("限制", "利空", 0.7),
    "sanction": ("制裁", "利空", 0.8),
    "export control": ("出口管制", "利空", 0.85),
    "tariff": ("关税", "利空", 0.75),
    "war": ("地缘风险", "利空", 0.6),
    "tension": ("紧张局势", "利空", 0.6),
}

# Location keywords for inference
LOCATION_KEYWORDS = {
    # Cities
    "seoul": "Seoul, South Korea",
    "ソウル": "Seoul, South Korea",
    "首尔": "Seoul, South Korea",
    "tokyo": "Tokyo, Japan",
    "東京": "Tokyo, Japan",
    "东京": "Tokyo, Japan",
    "taipei": "Taipei, Taiwan",
    "台北": "Taipei, Taiwan",
    "beijing": "Beijing, China",
    "北京": "Beijing, China",
    "shanghai": "Shanghai, China",
    "上海": "Shanghai, China",
    "shenzhen": "Shenzhen, China",
    "深圳": "Shenzhen, China",
    "san francisco": "San Francisco, USA",
    "san jose": "San Jose, USA",
    "santa clara": "Santa Clara, USA",
    "las vegas": "Las Vegas, USA",
    "ラスベガス": "Las Vegas, USA",
    "new york": "New York, USA",
    "london": "London, UK",
    "パリ": "Paris, France",
    "paris": "Paris, France",
    "berlin": "Berlin, Germany",
    "シンガポール": "Singapore",
    "singapore": "Singapore",
    "mumbai": "Mumbai, India",
    "bangalore": "Bangalore, India",
    
    # Events
    "computex": "Taipei (Computex)",
    "台北国际电脑展": "Taipei (Computex)",
    "ces": "Las Vegas (CES)",
    "mwc": "Barcelona (MWC)",
    "gdc": "San Francisco (GDC)",
    "siggraph": "USA (SIGGRAPH)",
    "nvidia gtc": "San Jose (NVIDIA GTC)",
    "gtc": "San Jose (NVIDIA GTC)",
    
    # Landmarks
    "jamsil": "Seoul (Jamsil)",
    "蚕室": "Seoul (Jamsil)",
    "gangnam": "Seoul (Gangnam)",
    "江南": "Seoul (Gangnam)",
    "naver 1784": "Seongnam (Naver HQ)",
    "삼성": "Suwon/Seoul (Samsung)",
    "samsung": "Suwon/Seoul (Samsung)",
}

# Key quote patterns - sentences that contain important statements
QUOTE_INDICATORS = [
    r"(?:said|announced|stated|declared|revealed|confirmed|mentioned|told|shared)",
    r"(?:said|announced|stated|declared|revealed|confirmed|mentioned|told|shared)",
    r"(?:発表|表明|述べ|明らかに|確認|共有)",
    r"(?:表示|宣布|声明|透露|确认|分享|指出)",
    r"(?:plan|plan to|will|aims to|expects|intends)",
    r"(?:计划|将|打算|预计|目标)",
]


def extract_key_quotes(articles: List[dict], max_quotes: int = 3) -> List[str]:
    """Extract key quotes from article snippets"""
    quotes = []
    
    for article in articles[:10]:  # Check first 10 articles
        snippet = article.get("snippet", "")
        title = article.get("title", "")
        text = f"{title}. {snippet}"
        
        # Split into sentences
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Score sentences
        scored_sentences = []
        for sentence in sentences:
            score = 0
            
            # Higher score for sentences with quote indicators
            for pattern in QUOTE_INDICATORS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    score += 3
            
            # Higher score for sentences with numbers (statistics)
            if re.search(r'\d+%|\$\d+|billion|million|兆|億', sentence):
                score += 2
            
            # Higher score for sentences with company names
            company_names = ["nvidia", "samsung", "sk hynix", "tsmc", "intel", 
                           "amd", "microsoft", "google", "meta", "amazon",
                           "nvidia", "三星", "sk海力士", "台积电"]
            for company in company_names:
                if company.lower() in sentence.lower():
                    score += 1
            
            # Prefer medium-length sentences (not too short, not too long)
            if 30 < len(sentence) < 200:
                score += 1
            
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Sort by score and take top quotes
        scored_sentences.sort(reverse=True)
        for _, quote in scored_sentences[:2]:
            if quote not in quotes and len(quotes) < max_quotes:
                # Clean up the quote
                quote = re.sub(r'\s+', ' ', quote).strip()
                if len(quote) > 30:
                    quotes.append(quote)
    
    return quotes[:max_quotes]


def analyze_market_impact(articles: List[dict]) -> List[Dict]:
    """Analyze market impact from news articles"""
    sector_scores = {}
    
    for article in articles:
        text = f"{article.get('title', '')} {article.get('snippet', '')}".lower()
        
        for keyword, (sector, impact_type, confidence) in MARKET_IMPACT_KEYWORDS.items():
            if keyword in text:
                if sector not in sector_scores:
                    sector_scores[sector] = {
                        "sector": sector,
                        "impact": impact_type,
                        "confidence": 0,
                        "mentions": 0,
                        "keywords": []
                    }
                
                sector_scores[sector]["mentions"] += 1
                sector_scores[sector]["confidence"] = max(
                    sector_scores[sector]["confidence"], 
                    confidence
                )
                if keyword not in sector_scores[sector]["keywords"]:
                    sector_scores[sector]["keywords"].append(keyword)
    
    # Sort by confidence and mentions
    results = sorted(
        sector_scores.values(),
        key=lambda x: (x["confidence"], x["mentions"]),
        reverse=True
    )
    
    return results[:5]  # Top 5 sectors


def infer_location(articles: List[dict]) -> Tuple[str, float]:
    """Infer current location from articles"""
    location_scores = {}
    
    for article in articles:
        text = f"{article.get('title', '')} {article.get('snippet', '')}".lower()
        
        for keyword, location in LOCATION_KEYWORDS.items():
            if keyword in text:
                if location not in location_scores:
                    location_scores[location] = 0
                location_scores[location] += 1
    
    if not location_scores:
        return "Unknown", 0.0
    
    # Find location with highest score
    best_location = max(location_scores.items(), key=lambda x: x[1])
    
    # Calculate confidence (normalize by total mentions)
    total_mentions = sum(location_scores.values())
    confidence = best_location[1] / total_mentions if total_mentions > 0 else 0
    
    return best_location[0], min(confidence, 0.95)


def generate_analysis_summary(person_name: str, articles: List[dict]) -> dict:
    """Generate complete analysis for a person"""
    # Extract key quotes
    key_quotes = extract_key_quotes(articles)
    
    # Analyze market impact
    market_impacts = analyze_market_impact(articles)
    
    # Infer location
    location, location_confidence = infer_location(articles)
    
    # Generate summary text
    summary_parts = []
    
    if key_quotes:
        summary_parts.append("🗣 关键言论:")
        for i, quote in enumerate(key_quotes, 1):
            summary_parts.append(f"  {i}. {quote[:100]}...")
    
    if market_impacts:
        summary_parts.append("\n📈 市场影响预测:")
        for impact in market_impacts[:3]:
            emoji = "🟢" if impact["impact"] == "利好" else "🔴" if impact["impact"] == "利空" else "⚪"
            summary_parts.append(
                f"  {emoji} {impact['sector']}: {impact['impact']} "
                f"(置信度: {impact['confidence']:.0%}, 提及: {impact['mentions']}次)"
            )
    
    summary_parts.append(f"\n📍 推断位置: {location} (置信度: {location_confidence:.0%})")
    
    return {
        "person": person_name,
        "key_quotes": key_quotes,
        "market_impacts": market_impacts,
        "inferred_location": location,
        "location_confidence": location_confidence,
        "summary": "\n".join(summary_parts)
    }


def format_for_display(analysis: dict) -> str:
    """Format analysis for display"""
    return analysis["summary"]


# Test with sample data
if __name__ == "__main__":
    sample_articles = [
        {
            "title": "Samsung plans next-gen HBM4 supply to NVIDIA; verification progress in focus",
            "snippet": "Samsung Electronics is accelerating its HBM4 development for NVIDIA's next-generation AI chips. The company announced plans to begin mass production in Q3 2026."
        },
        {
            "title": "Naver, NVIDIA talk 'Global AI Factory' partnership; 1784 HQ is key stop",
            "snippet": "Naver and NVIDIA are discussing a strategic partnership to build AI factories. Jensen Huang visited Naver's 1784 headquarters in Seongnam."
        },
        {
            "title": "Jensen Huang Returns to SNU After 18 Years, Surprised by the Number of Female Students",
            "snippet": "NVIDIA CEO Jensen Huang visited Seoul National University for the first time in 18 years. He expressed surprise at the increase in female engineering students."
        }
    ]
    
    analysis = generate_analysis_summary("Jensen Huang", sample_articles)
    print(format_for_display(analysis))
