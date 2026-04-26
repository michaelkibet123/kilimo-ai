import json
from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase():
    return create_client(st.secrets['SUPABASE_URL'], st.secrets['SUPABASE_KEY'])

def get_advisory(disease_name):
    try:
        supabase = get_supabase()
        response = supabase.table('advisory_cache')\
            .select('*')\
            .eq('disease', disease_name)\
            .execute()
        
        if response.data:
            raw = response.data[0]['compiled_summary']
            if isinstance(raw, str):
                return json.loads(raw)
            return raw
        return get_default_advisory()
    except Exception as e:
        return get_default_advisory()

def get_default_advisory():
    return {
        'description': 'No description available for this disease.',
        'immediate_action': 'Consult a local agronomist for advice.',
        'treatment': 'Visit your nearest agrovet for treatment options.',
        'prevention': 'Practice good crop hygiene and regular scouting.'
    }

def save_scan_to_db(user_id, crop, disease, confidence, top3, 
                     image_url, heatmap_url, treatment):
    try:
        supabase = get_supabase()
        supabase.table('scans').insert({
            'user_id': user_id,
            'crop': crop,
            'disease': disease,
            'confidence': confidence,
            'top3': top3,
            'image_url': image_url,
            'heatmap_url': heatmap_url,
            'treatment': treatment
        }).execute()
        return True
    except Exception as e:
        return False

def get_user_scans(user_id):
    try:
        supabase = get_supabase()
        response = supabase.table('scans')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('timestamp', desc=True)\
            .execute()
        return response.data
    except Exception:
        return []

def get_user_profile(user_id):
    try:
        supabase = get_supabase()
        response = supabase.table('users')\
            .select('*')\
            .eq('id', user_id)\
            .execute()
        if response.data:
            return response.data[0]
        return None
    except Exception:
        return None

def get_vets(county=None):
    try:
        supabase = get_supabase()
        query = supabase.table('vets_directory').select('*')
        if county and county != 'All Counties':
            query = query.eq('county', county)
        response = query.order('name').execute()
        return response.data
    except Exception:
        return []

def update_feedback(scan_id, feedback):
    try:
        supabase = get_supabase()
        supabase.table('scans')\
            .update({'feedback': feedback})\
            .eq('id', scan_id)\
            .execute()
        return True
    except Exception:
        return False
