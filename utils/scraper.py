import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import streamlit as st
from utils.advisory import get_supabase

SCRAPE_SOURCES = [
    'https://www.plantwise.org/knowledgebank/',
    'https://www.agriculture.go.ke/',
    'https://www.fao.org/kenya/en/',
]

def should_refresh(last_updated_str):
    try:
        if not last_updated_str:
            return True
        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - last_updated
        return diff.total_seconds() > 86400
    except Exception:
        return True

def scrape_disease_info(disease_name):
    clean_name = disease_name.split('___')[-1].replace('_', ' ').strip()
    query = f"{clean_name} tomato maize potato pepper treatment Kenya"
    
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        
        snippets = []
        for div in soup.find_all('div', class_='BNeawe'):
            text = div.get_text()
            if len(text) > 50 and clean_name.lower() in text.lower():
                snippets.append(text)
            if len(snippets) >= 3:
                break
        
        if snippets:
            compiled = f"Latest information on {clean_name}:\n\n"
            compiled += '\n\n'.join(snippets[:3])
            return compiled
        return None
    except Exception:
        return None

def get_latest_advisory(disease_name):
    try:
        supabase = get_supabase()
        response = supabase.table('advisory_cache')\
            .select('compiled_summary, last_updated')\
            .eq('disease', disease_name)\
            .execute()

        if response.data:
            record = response.data[0]
            if not should_refresh(record.get('last_updated')):
                return None, False

        scraped = scrape_disease_info(disease_name)
        
        if scraped:
            supabase.table('advisory_cache')\
                .update({'last_updated': datetime.now(timezone.utc).isoformat()})\
                .eq('disease', disease_name)\
                .execute()
            return scraped, True
        
        return None, False
    except Exception:
        return None, False
