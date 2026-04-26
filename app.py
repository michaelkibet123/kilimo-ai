import streamlit as st
from utils.advisory import get_supabase

st.set_page_config(
    page_title="Kilimo AI",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 1rem 5rem 1rem; max-width: 480px; margin: auto; }

.kilimo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid #F0F0F0;
    margin-bottom: 1rem;
}
.kilimo-logo { font-size: 1.4rem; font-weight: 700; color: #1B4332; }
.avatar {
    width: 36px; height: 36px; border-radius: 50%;
    background: #1B4332; color: white;
    display: flex; align-items: center; justify-content: center;
    font-weight: 600; font-size: 0.9rem;
}
.bottom-nav {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: white; border-top: 1px solid #F0F0F0;
    display: flex; justify-content: space-around;
    padding: 0.5rem 0; z-index: 999;
}
.nav-item {
    display: flex; flex-direction: column;
    align-items: center; font-size: 0.65rem;
    color: #6C757D; text-decoration: none;
    gap: 2px; cursor: pointer;
}
.nav-item.active { color: #1B4332; font-weight: 600; }
.hero-card {
    background: #1B4332; color: white;
    border-radius: 16px; padding: 1.5rem;
    display: flex; justify-content: space-between;
    align-items: center; margin: 1rem 0;
}
.hero-card h3 { margin: 0; font-size: 1.1rem; }
.hero-card p { margin: 0.3rem 0 0 0; font-size: 0.85rem; opacity: 0.85; }
.stat-card {
    background: #F8F9FA; border-radius: 12px;
    padding: 1rem; text-align: center;
}
.stat-number { font-size: 1.5rem; font-weight: 700; color: #1B4332; }
.stat-label { font-size: 0.75rem; color: #6C757D; margin-top: 2px; }
.scan-card {
    background: white; border: 1px solid #F0F0F0;
    border-radius: 12px; padding: 1rem;
    display: flex; align-items: center; gap: 1rem;
    margin: 0.5rem 0;
}
.disease-badge {
    padding: 0.2rem 0.6rem; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
}
.badge-high { background: #FEE2E2; color: #DC2626; }
.badge-medium { background: #FEF3C7; color: #F59E0B; }
.badge-low { background: #D1FAE5; color: #16A34A; }
.tip-card {
    background: #F8F9FA; border-radius: 10px;
    padding: 0.75rem; text-align: center;
    font-size: 0.8rem; color: #495057;
}
.tip-icon { font-size: 1.2rem; margin-bottom: 0.3rem; }
.seasonal-card {
    background: #FFFBEB; border: 1px solid #FDE68A;
    border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
}
.btn-primary {
    background: #1B4332; color: white;
    border: none; border-radius: 10px;
    padding: 0.75rem 1.5rem; font-size: 0.95rem;
    font-weight: 600; width: 100%; cursor: pointer;
}
.btn-outline {
    background: white; color: #1B4332;
    border: 2px solid #1B4332; border-radius: 10px;
    padding: 0.75rem 1.5rem; font-size: 0.95rem;
    font-weight: 600; width: 100%; cursor: pointer;
}
.landing-hero {
    min-height: 100vh;
    background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 50%, #40916C 100%);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 2rem; color: white; text-align: center;
}
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    height: 3rem !important;
}
.stButton > button[kind="primary"] {
    background: #1B4332 !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    defaults = {
        'authenticated': False,
        'user': None,
        'guest': False,
        'page': 'home',
        'scan_result': None,
        'uploaded_image': None,
        'show_landing': True,
        'profile_data': None,
        'notification_permission': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_initials(name):
    if not name:
        return 'U'
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return parts[0][0].upper()

def get_greeting():
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    return "Good evening"

def get_seasonal_alert():
    from datetime import datetime
    month = datetime.now().month
    if month in [3, 4, 5]:
        return {
            'season': 'Long Rains',
            'alert': 'Late Blight and Bacterial Spot risk is elevated.',
            'detail': 'During long rains, fungal and bacterial diseases spread rapidly. Scout your crops twice weekly and apply preventive fungicide at canopy closure. Avoid overhead irrigation and ensure good drainage.'
        }
    elif month in [10, 11, 12]:
        return {
            'season': 'Short Rains',
            'alert': 'Gray Leaf Spot and Early Blight risk is moderate.',
            'detail': 'Short rains create favorable conditions for foliar diseases in maize and tomato. Monitor lower leaves for early signs and remove infected material promptly.'
        }
    elif month in [6, 7, 8, 9]:
        return {
            'season': 'Dry Season',
            'alert': 'Spider Mite risk is elevated in dry conditions.',
            'detail': 'Hot dry weather favors rapid spider mite reproduction. Check leaf undersides for stippling and fine webbing. Increase irrigation frequency and apply miticide if populations are high.'
        }
    return None

def render_header(show_avatar=True):
    name = ''
    if st.session_state.get('profile_data'):
        name = st.session_state['profile_data'].get('full_name', '')
    elif st.session_state.get('user'):
        name = st.session_state['user'].get('email', 'U')
    
    initials = get_initials(name) if name else 'G'
    st.markdown(f"""
    <div class="kilimo-header">
        <div class="kilimo-logo">🌿 Kilimo AI</div>
        {'<div class="avatar">' + initials + '</div>' if show_avatar else ''}
    </div>
    """, unsafe_allow_html=True)

def render_bottom_nav():
    page = st.session_state.get('page', 'home')
    cols = st.columns(5)
    pages = [
        ('home', '🏠', 'Home'),
        ('scan', '📷', 'Scan'),
        ('history', '🕐', 'History'),
        ('vets', '🏪', 'Vets'),
        ('profile', '👤', 'Profile'),
    ]
    for i, (p, icon, label) in enumerate(pages):
        with cols[i]:
            active = 'active' if page == p else ''
            if st.button(f"{icon}\n{label}", key=f"nav_{p}", use_container_width=True):
                st.session_state['page'] = p
                st.rerun()

def render_landing():
    st.markdown("""
    <div style="text-align:center; padding: 3rem 1rem 2rem 1rem;">
        <div style="font-size:4rem;">🌿</div>
        <h1 style="color:#1B4332; font-size:2.2rem; font-weight:700; margin:0.5rem 0;">Kilimo AI</h1>
        <p style="color:#6C757D; font-size:1rem; margin-bottom:0.5rem;">Diagnose. Treat. Protect.</p>
        <p style="color:#6C757D; font-size:0.85rem;">AI-powered crop disease diagnosis for Kenyan farmers</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    
    if st.button("🚀 Get Started", use_container_width=True, type="primary"):
        st.session_state['show_landing'] = False
        st.session_state['auth_mode'] = 'signup'
        st.rerun()
    
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    
    if st.button("🔑 Log In", use_container_width=True):
        st.session_state['show_landing'] = False
        st.session_state['auth_mode'] = 'login'
        st.rerun()
    
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    
    if st.button("👁️ Continue as Guest", use_container_width=True):
        st.session_state['guest'] = True
        st.session_state['show_landing'] = False
        st.session_state['page'] = 'scan'
        st.rerun()

    st.markdown("""
    <div style="text-align:center; margin-top:2rem; color:#6C757D; font-size:0.8rem;">
        🔒 Your data is safe with us
    </div>
    <div style="display:flex; justify-content:center; gap:2rem; margin-top:1.5rem;">
        <div style="text-align:center; font-size:0.8rem; color:#6C757D;">
            <div style="font-size:1.5rem;">🔬</div>AI Powered
        </div>
        <div style="text-align:center; font-size:0.8rem; color:#6C757D;">
            <div style="font-size:1.5rem;">🇰🇪</div>Kenya First
        </div>
        <div style="text-align:center; font-size:0.8rem; color:#6C757D;">
            <div style="font-size:1.5rem;">⚡</div>Instant Results
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_auth():
    mode = st.session_state.get('auth_mode', 'login')
    
    render_header(show_avatar=False)
    
    tab1, tab2 = st.tabs(["Log In", "Sign Up"])
    
    with tab1:
        st.markdown("### Welcome back")
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
        
        if st.button("Log In", use_container_width=True, type="primary", key="login_btn"):
            if email and password:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = response.user.__dict__
                    st.session_state['page'] = 'home'
                    st.session_state['show_landing'] = False
                    
                    profile = supabase.table('users').select('*').eq('id', response.user.id).execute()
                    if profile.data:
                        st.session_state['profile_data'] = profile.data[0]
                    st.rerun()
                except Exception as e:
                    st.error("Invalid email or password. Please try again.")
            else:
                st.warning("Please enter your email and password.")
        
        if st.button("Forgot Password?", key="forgot_btn"):
            st.session_state['auth_mode'] = 'forgot'
            st.rerun()
    
    with tab2:
        st.markdown("### Create your account")
        full_name = st.text_input("Full Name", key="signup_name", placeholder="John Kamau")
        email_s = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        phone = st.text_input("Phone Number", key="signup_phone", placeholder="+254 7XX XXX XXX")
        
        counties = ['Nairobi', 'Nakuru', 'Kisumu', 'Mombasa', 'Uasin Gishu', 
                   'Nyeri', 'Kiambu', 'Kisii', 'Meru', 'Machakos', 'Kakamega', 
                   'Embu', 'Kirinyaga', 'Other']
        region = st.selectbox("County", counties, key="signup_region")
        
        crops = st.multiselect("Crops you grow", 
                               ['Maize', 'Tomato', 'Potato', 'Pepper', 'Beans', 'Wheat'],
                               key="signup_crops")
        
        password_s = st.text_input("Password", type="password", key="signup_password", placeholder="Min 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Repeat password")
        
        if st.button("Create Account", use_container_width=True, type="primary", key="signup_btn"):
            if not all([full_name, email_s, phone, password_s, confirm_password]):
                st.warning("Please fill in all fields.")
            elif password_s != confirm_password:
                st.error("Passwords do not match.")
            elif len(password_s) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    supabase = get_supabase()
                    response = supabase.auth.sign_up({
                        "email": email_s,
                        "password": password_s
                    })
                    
                    supabase.table('users').insert({
                        'id': response.user.id,
                        'full_name': full_name,
                        'phone': phone,
                        'region': region,
                        'crops_grown': crops
                    }).execute()
                    
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = response.user.__dict__
                    st.session_state['profile_data'] = {
                        'full_name': full_name,
                        'phone': phone,
                        'region': region,
                        'crops_grown': crops
                    }
                    st.session_state['page'] = 'home'
                    st.success("Account created successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
    
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("Continue as Guest instead", key="guest_from_auth"):
        st.session_state['guest'] = True
        st.session_state['page'] = 'scan'
        st.rerun()

def render_home():
    render_header()
    
    profile = st.session_state.get('profile_data', {})
    name = profile.get('full_name', 'Farmer') if profile else 'Farmer'
    greeting = get_greeting()
    
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1rem 0;">
        <h2 style="margin:0; font-size:1.6rem; font-weight:700;">{greeting},</h2>
        <h2 style="margin:0; font-size:1.6rem; font-weight:700; color:#1B4332;">{name} 👋</h2>
    </div>
    """, unsafe_allow_html=True)

    seasonal = get_seasonal_alert()
    if seasonal:
        with st.container():
            st.markdown(f"""
            <div class="seasonal-card">
                <div style="font-size:0.75rem; color:#92400E; font-weight:600;">
                    🌦️ {seasonal['season']} Season Alert
                </div>
                <div style="font-size:0.85rem; color:#78350F; margin-top:0.3rem;">
                    {seasonal['alert']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Learn More", key="seasonal_more"):
                st.info(seasonal['detail'])

    st.markdown("""
    <div class="hero-card">
        <div>
            <h3>Scan a plant</h3>
            <p>Take a photo or upload an image to diagnose disease</p>
        </div>
        <div style="font-size:2.5rem;">📷</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Start Scanning →", use_container_width=True, type="primary"):
        st.session_state['page'] = 'scan'
        st.rerun()

    st.markdown("### Quick Tips")
    cols = st.columns(3)
    tips = [
        ("📸", "Use clear photos"),
        ("☀️", "Good lighting"),
        ("🎯", "Focus on affected area")
    ]
    for i, (icon, tip) in enumerate(tips):
        with cols[i]:
            st.markdown(f"""
            <div class="tip-card">
                <div class="tip-icon">{icon}</div>
                {tip}
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.get('authenticated'):
        from utils.advisory import get_user_scans, get_supabase
        user_id = st.session_state['user'].get('id')
        scans = get_user_scans(user_id)
        
        if scans:
            total = len(scans)
            diseased = len([s for s in scans if 'healthy' not in s.get('disease', '').lower()])
            crops_set = len(set([s.get('crop', '') for s in scans]))
            
            st.markdown("### Your Farm Stats")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{total}</div><div class="stat-label">Total Scans</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{diseased}</div><div class="stat-label">Diseases Found</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{crops_set}</div><div class="stat-label">Crops Monitored</div></div>', unsafe_allow_html=True)

            st.markdown("### Recent Scan")
            last = scans[0]
            crop, disease = last.get('crop', ''), last.get('disease', '')
            conf = last.get('confidence', 0)
            badge = 'badge-high' if conf >= 0.85 else 'badge-medium' if conf >= 0.60 else 'badge-low'
            st.markdown(f"""
            <div class="scan-card">
                <div style="font-size:2rem;">🌿</div>
                <div style="flex:1;">
                    <div style="font-weight:600;">{disease}</div>
                    <div style="font-size:0.8rem; color:#6C757D;">{crop}</div>
                </div>
                <div class="disease-badge {badge}">{int(conf*100)}%</div>
            </div>
            """, unsafe_allow_html=True)

    render_bottom_nav()

def main():
    init_session_state()
    
    if st.session_state.get('show_landing') and not st.session_state.get('authenticated') and not st.session_state.get('guest'):
        render_landing()
        return
    
    if not st.session_state.get('authenticated') and not st.session_state.get('guest'):
        render_auth()
        return
    
    page = st.session_state.get('page', 'home')
    
    if page == 'home':
        render_home()
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
    main()import streamlit as st
st.title("Kilimo AI")
st.write("Coming soon.")
