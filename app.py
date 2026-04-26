import streamlit as st
st.set_page_config(page_title="Kilimo AI", page_icon="🌿", layout="centered", initial_sidebar_state="collapsed")

from utils.advisory import get_supabase

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Serif+Display&display=swap');
html,body{font-family:'DM Sans',sans-serif;background:#F2F4F3;color:#1A1A1A;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],section[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important;}
[data-testid="stAppViewContainer"]>.main{background:#F2F4F3!important;padding:0!important;}
.block-container{max-width:480px!important;margin:0 auto!important;padding:0 0 80px 0!important;background:#F2F4F3!important;}
@media(min-width:640px){.block-container{max-width:700px!important;padding:0 16px 80px!important;}}
.kheader{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;background:white;border-bottom:1px solid #E5E7EB;position:sticky;top:0;z-index:50;}
.klogo{font-family:'DM Serif Display',serif;font-size:1.3rem;color:#1B4332;display:flex;align-items:center;gap:6px;}
.klogo em{color:#40916C;font-style:normal;}
.kavatar{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#1B4332,#52B788);color:white;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;}
.kcard{background:white;border-radius:16px;padding:18px;margin:10px 12px;box-shadow:0 1px 8px rgba(0,0,0,0.07);}
.khero{background:linear-gradient(135deg,#1B4332,#2D6A4F,#40916C);border-radius:16px;padding:22px 18px;margin:10px 12px;color:white;}
.kstat{background:white;border-radius:14px;padding:14px 8px;text-align:center;box-shadow:0 1px 6px rgba(0,0,0,0.06);}
.kstat-n{font-family:'DM Serif Display',serif;font-size:1.7rem;color:#1B4332;line-height:1;}
.kstat-l{font-size:0.65rem;color:#9CA3AF;margin-top:3px;text-transform:uppercase;letter-spacing:0.05em;font-weight:500;}
.ktip{background:white;border-radius:12px;padding:12px 8px;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.ktip-i{font-size:1.3rem;margin-bottom:4px;}
.ktip-t{font-size:0.7rem;color:#6B7280;font-weight:500;}
.kscan-row{background:white;border-radius:14px;padding:12px 14px;margin:6px 12px;display:flex;align-items:center;gap:10px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.kvet{background:white;border-radius:14px;padding:14px;margin:6px 12px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.kpill{display:inline-block;background:#F0FDF4;color:#166534;border-radius:20px;padding:2px 8px;font-size:0.68rem;font-weight:500;margin:2px;}
.kalert{background:#FFFBEB;border-left:3px solid #F59E0B;border-radius:10px;padding:12px 14px;margin:6px 12px;}
.kdisease{font-family:'DM Serif Display',serif;font-size:1.5rem;color:#1A1A1A;line-height:1.2;}
.kconf{font-family:'DM Serif Display',serif;font-size:2.2rem;line-height:1;}
.bsevere{background:#FEE2E2;color:#DC2626;padding:3px 8px;border-radius:20px;font-size:0.7rem;font-weight:600;}
.bmoderate{background:#FEF3C7;color:#D97706;padding:3px 8px;border-radius:20px;font-size:0.7rem;font-weight:600;}
.bhealthy{background:#D1FAE5;color:#059669;padding:3px 8px;border-radius:20px;font-size:0.7rem;font-weight:600;}
.klanding{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:32px 20px;text-align:center;background:#F2F4F3;}
.klanding-logo{font-family:'DM Serif Display',serif;font-size:2.8rem;color:#1B4332;margin:16px 0 6px;}
.klanding-tag{font-size:0.78rem;color:#9CA3AF;letter-spacing:0.12em;text-transform:uppercase;}
.kleaf{width:72px;height:72px;background:linear-gradient(135deg,#1B4332,#52B788);border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:2rem;box-shadow:0 6px 24px rgba(27,67,50,0.28);margin:0 auto;}
.kprofile-hero{background:linear-gradient(135deg,#1B4332,#2D6A4F);border-radius:16px;padding:20px 16px;margin:10px 12px;color:white;}
.kprofile-stats{display:grid;grid-template-columns:repeat(3,1fr);background:rgba(255,255,255,0.12);border-radius:12px;overflow:hidden;margin-top:14px;}
.kprofile-stat{padding:10px 6px;text-align:center;}
.kprofile-stat-n{font-family:'DM Serif Display',serif;font-size:1.3rem;color:white;}
.kprofile-stat-l{font-size:0.6rem;color:rgba(255,255,255,0.65);text-transform:uppercase;letter-spacing:0.04em;}
.stButton>button{font-family:'DM Sans',sans-serif!important;font-weight:600!important;border-radius:12px!important;height:48px!important;font-size:0.9rem!important;transition:all 0.15s ease!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#1B4332,#2D6A4F)!important;border:none!important;box-shadow:0 3px 10px rgba(27,67,50,0.22)!important;color:white!important;}
.stButton>button[kind="secondary"]{background:white!important;border:1.5px solid #D1D5DB!important;color:#374151!important;}
.stTextInput>div>div>input,.stSelectbox>div>div{border-radius:10px!important;border:1.5px solid #E5E7EB!important;font-family:'DM Sans',sans-serif!important;}
.stTabs [data-baseweb="tab-list"]{background:#F3F4F6;border-radius:10px;padding:3px;}
.stTabs [data-baseweb="tab"]{border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-weight:500!important;font-size:0.82rem!important;color:#6B7280!important;}
.stTabs [aria-selected="true"]{background:white!important;color:#1B4332!important;font-weight:600!important;box-shadow:0 1px 3px rgba(0,0,0,0.08)!important;}
/* NAV */
.knav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:480px;background:white;border-top:1px solid #E5E7EB;display:flex;justify-content:space-around;align-items:center;padding:6px 0 18px;z-index:999;box-shadow:0 -2px 12px rgba(0,0,0,0.06);}
@media(min-width:640px){.knav{max-width:700px;}}
.knav-item{display:flex;flex-direction:column;align-items:center;gap:2px;cursor:pointer;padding:4px 10px;border-radius:10px;min-width:56px;}
.knav-label{font-size:0.6rem;font-weight:500;color:#9CA3AF;margin-top:1px;}
.knav-item.active .knav-label{color:#1B4332;font-weight:700;}
.knav-fab{width:48px;height:48px;background:linear-gradient(135deg,#1B4332,#2D6A4F);border-radius:14px;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 12px rgba(27,67,50,0.35);margin-top:-18px;}
/* Overlay invisible buttons on nav */
.knav-buttons{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:480px;height:72px;z-index:1000;display:flex;}
.knav-buttons .stButton{flex:1;}
.knav-buttons .stButton>button{height:72px!important;opacity:0!important;border-radius:0!important;border:none!important;background:transparent!important;box-shadow:none!important;width:100%!important;}
@media(min-width:640px){.knav-buttons{max-width:700px;}}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    defaults = {
        'authenticated': False, 'user': None, 'guest': False,
        'page': 'home', 'scan_result': None, 'uploaded_image': None,
        'show_landing': True, 'profile_data': None,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_initials(name):
    if not name: return 'U'
    parts = name.strip().split()
    if len(parts) >= 2: return f"{parts[0][0]}{parts[1][0]}".upper()
    return parts[0][0].upper()

def get_greeting():
    from datetime import datetime
    h = datetime.now().hour
    if h < 12: return "Good morning"
    elif h < 17: return "Good afternoon"
    return "Good evening"

def get_seasonal_alert():
    from datetime import datetime
    m = datetime.now().month
    if m in [3,4,5]: return {"season":"Long Rains","alert":"Late Blight & Bacterial Spot risk is elevated.","detail":"Fungal and bacterial diseases spread rapidly during long rains. Scout twice weekly and apply preventive fungicide at canopy closure."}
    elif m in [10,11,12]: return {"season":"Short Rains","alert":"Gray Leaf Spot & Early Blight risk is moderate.","detail":"Monitor lower leaves for early signs and remove infected material promptly."}
    elif m in [6,7,8,9]: return {"season":"Dry Season","alert":"Spider Mite risk is elevated.","detail":"Check leaf undersides for stippling and webbing. Increase irrigation frequency."}
    return None

def render_header(show_avatar=True):
    name = ''
    if st.session_state.get('profile_data'): name = st.session_state['profile_data'].get('full_name','')
    elif st.session_state.get('user'): name = st.session_state['user'].get('email','U')
    initials = get_initials(name) if name else 'G'
    av = f'<div class="kavatar">{initials}</div>' if show_avatar else ''
    st.markdown(f'''<div class="kheader"><div class="klogo"><svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" fill="#52B788" stroke="#1B4332" stroke-width="1.5" stroke-linejoin="round"/></svg>Kilimo <em>AI</em></div>{av}</div>''', unsafe_allow_html=True)

def render_bottom_nav():
    page = st.session_state.get('page','home')
    def c(p): return 'knav-item active' if page==p else 'knav-item'
    def s(p): return '#1B4332' if page==p else '#9CA3AF'
    st.markdown(f'''
    <div class="knav">
        <div class="{c('home')}">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M3 9.5L12 3L21 9.5V20C21 20.55 20.55 21 20 21H15V15H9V21H4C3.45 21 3 20.55 3 20V9.5Z" stroke="{s('home')}" stroke-width="2" stroke-linejoin="round"/>
            </svg>
            <span class="knav-label">Home</span>
        </div>
        <div class="{c('history')}">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="{s('history')}" stroke-width="2"/>
                <path d="M12 7V12L15 14" stroke="{s('history')}" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span class="knav-label">History</span>
        </div>
        <div class="knav-item">
            <div class="knav-fab">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
                    <path d="M12 9V15M9 12H15" stroke="white" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <span class="knav-label">Scan</span>
        </div>
        <div class="{c('vets')}">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="{s('vets')}" stroke-width="2"/>
                <path d="M12 7V11M10 9H14" stroke="{s('vets')}" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span class="knav-label">Vets</span>
        </div>
        <div class="{c('profile')}">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" stroke="{s('profile')}" stroke-width="2"/>
                <path d="M4 20C4 17 7.58 14 12 14C16.42 14 20 17 20 20" stroke="{s('profile')}" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span class="knav-label">Profile</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    cols = st.columns(5)
    pages = [('home','Home'),('history','History'),('scan','Scan'),('vets','Vets'),('profile','Profile')]
    for i,(p,label) in enumerate(pages):
        with cols[i]:
            if st.button(label, key=f"nav_{p}", use_container_width=True):
                st.session_state['page'] = p
                st.rerun()

def render_landing():
    st.markdown('''<div class="klanding">''', unsafe_allow_html=True)
    st.markdown('''<div class="kleaf">🌿</div>''', unsafe_allow_html=True)
    st.markdown('''<div class="klanding-logo">Kilimo AI</div>''', unsafe_allow_html=True)
    st.markdown('''<div class="klanding-tag">Diagnose · Treat · Protect</div>''', unsafe_allow_html=True)
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    if st.button("Get Started", use_container_width=True, type="primary"):
        st.session_state['show_landing'] = False
        st.session_state['auth_mode'] = 'signup'
        st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Log In", use_container_width=True):
        st.session_state['show_landing'] = False
        st.session_state['auth_mode'] = 'login'
        st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Continue as Guest", use_container_width=True):
        st.session_state['guest'] = True
        st.session_state['show_landing'] = False
        st.session_state['page'] = 'scan'
        st.rerun()
    st.markdown('''
    <div style="display:flex;justify-content:center;gap:20px;margin-top:28px;">
        <div style="text-align:center;font-size:0.72rem;color:#9CA3AF;">
            <div style="font-size:1.2rem;margin-bottom:4px;">🔒</div>Secure
        </div>
        <div style="text-align:center;font-size:0.72rem;color:#9CA3AF;">
            <div style="font-size:1.2rem;margin-bottom:4px;">🇰🇪</div>Kenya First
        </div>
        <div style="text-align:center;font-size:0.72rem;color:#9CA3AF;">
            <div style="font-size:1.2rem;margin-bottom:4px;">⚡</div>Instant AI
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_auth():
    render_header(show_avatar=False)
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    with tab1:
        st.markdown("<div style='padding:0 4px'>", unsafe_allow_html=True)
        st.markdown("### Welcome back")
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", use_container_width=True, type="primary", key="login_btn"):
            if email and password:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = response.user.__dict__
                    st.session_state['page'] = 'home'
                    profile = supabase.table('users').select('*').eq('id', response.user.id).execute()
                    if profile.data: st.session_state['profile_data'] = profile.data[0]
                    st.rerun()
                except Exception as e:
                    st.error("Invalid email or password.")
            else:
                st.warning("Please fill in all fields.")
        st.markdown("</div>", unsafe_allow_html=True)
    with tab2:
        st.markdown("<div style='padding:0 4px'>", unsafe_allow_html=True)
        st.markdown("### Create account")
        full_name = st.text_input("Full Name", key="signup_name", placeholder="John Kamau")
        email_s = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        phone = st.text_input("Phone", key="signup_phone", placeholder="+254 7XX XXX XXX")
        counties = ['Nairobi','Nakuru','Kisumu','Mombasa','Uasin Gishu','Nyeri','Kiambu','Kisii','Meru','Machakos','Kakamega','Embu','Kirinyaga','Other']
        region = st.selectbox("County", counties, key="signup_region")
        crops = st.multiselect("Crops you grow", ['Maize','Tomato','Potato','Pepper','Beans','Wheat'], key="signup_crops")
        password_s = st.text_input("Password", type="password", key="signup_password")
        confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
        if st.button("Create Account", use_container_width=True, type="primary", key="signup_btn"):
            if not all([full_name, email_s, phone, password_s, confirm]):
                st.warning("Please fill in all fields.")
            elif password_s != confirm:
                st.error("Passwords do not match.")
            elif len(password_s) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_up({"email": email_s, "password": password_s})
                    supabase.table('users').insert({'id': response.user.id, 'full_name': full_name, 'phone': phone, 'region': region, 'crops_grown': crops}).execute()
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = response.user.__dict__
                    st.session_state['profile_data'] = {'full_name': full_name, 'phone': phone, 'region': region, 'crops_grown': crops}
                    st.session_state['page'] = 'home'
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Continue as Guest", use_container_width=True, key="guest_auth"):
        st.session_state['guest'] = True
        st.session_state['page'] = 'scan'
        st.rerun()

def render_home():
    render_header()
    profile = st.session_state.get('profile_data', {}) or {}
    name = profile.get('full_name', 'Farmer')
    greeting = get_greeting()
    st.markdown(f"""
    <div style="padding:16px 16px 8px;">
        <div style="font-size:0.85rem;color:#9CA3AF;font-weight:400;">{greeting},</div>
        <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:#1A1A1A;line-height:1.1;">{name} 👋</div>
    </div>
    """, unsafe_allow_html=True)
    seasonal = get_seasonal_alert()
    if seasonal:
        st.markdown(f'''
        <div class="kalert">
            <div style="font-size:0.72rem;color:#92400E;font-weight:600;margin-bottom:3px;">🌦 {seasonal['season']} Season</div>
            <div style="font-size:0.82rem;color:#78350F;">{seasonal['alert']}</div>
        </div>
        ''', unsafe_allow_html=True)
        with st.expander("Learn more"):
            st.write(seasonal['detail'])
    st.markdown('''
    <div class="khero">
        <div style="font-size:0.8rem;opacity:0.8;margin-bottom:4px;">Ready to diagnose?</div>
        <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;margin-bottom:6px;">Scan a Plant</div>
        <div style="font-size:0.82rem;opacity:0.85;">Take a photo or upload an image to detect disease instantly</div>
    </div>
    ''', unsafe_allow_html=True)
    if st.button("Start Scanning →", use_container_width=True, type="primary"):
        st.session_state['page'] = 'scan'
        st.rerun()
    st.markdown("<div style='padding:4px 16px 8px;font-weight:600;font-size:0.85rem;color:#374151;'>Quick Tips</div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown('<div class="ktip"><div class="ktip-i">📸</div><div class="ktip-t">Clear photos</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="ktip"><div class="ktip-i">☀️</div><div class="ktip-t">Good lighting</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="ktip"><div class="ktip-i">🎯</div><div class="ktip-t">Focus on leaf</div></div>', unsafe_allow_html=True)
    if st.session_state.get('authenticated'):
        from utils.advisory import get_user_scans
        user_id = st.session_state['user'].get('id')
        scans = get_user_scans(user_id)
        if scans:
            total = len(scans)
            diseased = len([s for s in scans if 'healthy' not in s.get('disease','').lower()])
            crops_n = len(set([s.get('crop','') for s in scans]))
            st.markdown("<div style='padding:12px 16px 6px;font-weight:600;font-size:0.85rem;color:#374151;'>Farm Stats</div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kstat"><div class="kstat-n">{total}</div><div class="kstat-l">Scans</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kstat"><div class="kstat-n">{diseased}</div><div class="kstat-l">Diseases</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kstat"><div class="kstat-n">{crops_n}</div><div class="kstat-l">Crops</div></div>', unsafe_allow_html=True)
            last = scans[0]
            conf = last.get('confidence',0)
            badge = 'bsevere' if conf>=0.85 else 'bmoderate' if conf>=0.60 else 'bhealthy'
            st.markdown("<div style='padding:12px 16px 6px;font-weight:600;font-size:0.85rem;color:#374151;'>Last Scan</div>", unsafe_allow_html=True)
            st.markdown(f'''
            <div class="kscan-row">
                <div style="width:40px;height:40px;background:#F0FDF4;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🌿</div>
                <div style="flex:1;">
                    <div style="font-weight:600;font-size:0.88rem;">{last.get('disease','')}</div>
                    <div style="font-size:0.75rem;color:#9CA3AF;">{last.get('crop','')}</div>
                </div>
                <span class="{badge}">{int(conf*100)}%</span>
            </div>
            ''', unsafe_allow_html=True)
    render_bottom_nav()

def main():
    init_session_state()
    if st.session_state.get('show_landing') and not st.session_state.get('authenticated') and not st.session_state.get('guest'):
        render_landing()
        return
    if not st.session_state.get('authenticated') and not st.session_state.get('guest'):
        render_auth()
        return
    page = st.session_state.get('page','home')
    if page == 'home': render_home()
    elif page == 'scan':
        from pages.scan import render_scan
        render_scan()
    elif page == 'history':
        from pages.history import render_history
        render_history()
    elif page == 'vets':
        from pages.vets import render_vets
        render_vets()
    elif page == 'profile':
        from pages.profile import render_profile
        render_profile()

if __name__ == '__main__':
    main()
