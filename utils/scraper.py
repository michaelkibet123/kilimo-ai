import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import streamlit as st

def should_refresh(last_updated_str):
    try:
        if not last_updated_str: return True
        last_updated = datetime.fromisoformat(last_updated_str.replace("Z","+00:00"))
        now = datetime.now(timezone.utc)
        return (now - last_updated).total_seconds() > 86400
    except: return True

def scrape_disease_info(disease_name):
    clean = disease_name.split("___")[-1].replace("_"," ").strip()
    sources = [
        f"https://www.plantwise.org/knowledgebank/datasheet/{clean.lower().replace(' ','-')}",
        f"https://extension.umn.edu/search#q={clean.replace(' ','%20')}&t=All",
        f"https://www.agriculture.go.ke/?s={clean.replace(' ','+')}",
    ]
    headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"}
    for url in sources:
        try:
            r = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(r.text, "lxml")
            for tag in soup(["script","style","nav","footer","header"]):
                tag.decompose()
            paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 80]
            relevant = [p for p in paragraphs if any(w in p.lower() for w in [clean.lower().split()[0], "disease","symptom","treatment","fungicide","spray"])]
            if relevant:
                return "Latest advisory for "+clean+":\n\n" + "\n\n".join(relevant[:3])
        except: continue
    return None

def get_latest_advisory(disease_name):
    from utils.advisory import get_supabase
    try:
        supabase = get_supabase()
        response = supabase.table("advisory_cache").select("compiled_summary,last_updated").eq("disease",disease_name).execute()
        if response.data:
            record = response.data[0]
            if not should_refresh(record.get("last_updated")):
                existing = record.get("compiled_summary","")
                if isinstance(existing, dict):
                    import json
                    existing = json.dumps(existing)
                return existing, True
        scraped = scrape_disease_info(disease_name)
        if scraped:
            supabase.table("advisory_cache").update({"last_updated":datetime.now(timezone.utc).isoformat()}).eq("disease",disease_name).execute()
            return scraped, True
        return None, False
    except Exception as e:
        return None, False
