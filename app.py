import streamlit as st
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title="Kilimo AI", page_icon="🌿", layout="centered", initial_sidebar_state="collapsed")
def render_header(show_avatar=True):
    name = ''
    if st.session_state.get('profile_data'):
        name = st.session_state['profile_data'].get('full_name', '')
    elif st.session_state.get('user'):
        name = st.session_state['user'].get('email', 'U')
    initials = get_initials(name) if name else 'G'
    avatar_html = f'<div class="kilimo-avatar">{initials}</div>' if show_avatar else ''
    st.markdown(f"""
    <div class="kilimo-header">
        <div class="kilimo-logo">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                <path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" fill="#40916C" stroke="#1B4332" stroke-width="1.5" stroke-linejoin="round"/>
            </svg>
            Kilimo <span>AI</span>
        </div>
        {avatar_html}
    </div>
    """, unsafe_allow_html=True)


def render_bottom_nav():
    page = st.session_state.get('page', 'home')
    def ic(p, active_color='#1B4332', inactive='#9CA3AF'):
        return active_color if page == p else inactive
    def nc(p):
        return 'nav-item active' if page == p else 'nav-item'
    st.markdown(f"""
    <div class="kilimo-bottom-nav">
        <div class="{nc('home')}">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M3 9.5L12 3L21 9.5V20C21 20.55 20.55 21 20 21H15V15H9V21H4C3.45 21 3 20.55 3 20V9.5Z" stroke="{ic('home')}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="nav-label">Home</span>
        </div>
        <div class="{nc('history')}">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="{ic('history')}" stroke-width="1.8"/>
                <path d="M12 7V12L15 14" stroke="{ic('history')}" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <span class="nav-label">History</span>
        </div>
        <div class="nav-item">
            <div class="nav-fab">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                    <path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" stroke="white" stroke-width="1.8" stroke-linejoin="round"/>
                    <path d="M12 9V15M9 12H15" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
                </svg>
            </div>
            <span class="nav-label">Scan</span>
        </div>
        <div class="{nc('vets')}">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="{ic('vets')}" stroke-width="1.8"/>
                <path d="M12 7V11M10 9H14" stroke="{ic('vets')}" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <span class="nav-label">Vets</span>
        </div>
        <div class="{nc('profile')}">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="4" stroke="{ic('profile')}" stroke-width="1.8"/>
                <path d="M4 20C4 17 7.58 14 12 14C16.42 14 20 17 20 20" stroke="{ic('profile')}" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <span class="nav-label">Profile</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(5)
    pages = [('home','Home'),('history','History'),('scan','Scan'),('vets','Vets'),('profile','Profile')]
    for i,(p,label) in enumerate(pages):
        with cols[i]:
            if st.button(label, key=f"nav_{p}", use_container_width=True):
                st.session_state['page'] = p
                st.rerun()


def get_initials(name):
    if not name:
        return "U"
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return parts[0][0].upper()

    st.session_state["page_config_set"] = True

from utils.advisory import get_supabase

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Serif+Display&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stAppViewContainer"]{font-family:'DM Sans',sans-serif;background:#FAFAF8;color:#1A1A1A;-webkit-font-smoothing:antialiased;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="collapsedControl"],section[data-testid="stSidebar"]{display:none!important;}
[data-testid="stAppViewContainer"]>.main{background:#FAFAF8;padding:0!important;}
.block-container{padding:0 0 88px 0!important;max-width:520px!important;margin:0 auto!important;}
@media(min-width:640px){.block-container{max-width:740px!important;padding:0 24px 88px 24px!important;}}
.kilimo-header{display:flex;justify-content:space-between;align-items:center;padding:16px 20px 12px;background:#FAFAF8;position:sticky;top:0;z-index:100;border-bottom:1px solid rgba(0,0,0,0.06);}
.kilimo-logo{font-family:'DM Serif Display',serif;font-size:1.4rem;color:#1B4332;letter-spacing:-0.02em;display:flex;align-items:center;gap:8px;}
.kilimo-logo span{color:#40916C;}
.kilimo-avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#1B4332,#40916C);color:white;display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:600;}
.kilimo-bottom-nav{position:fixed;bottom:0;left:0;right:0;background:white;border-top:1px solid rgba(0,0,0,0.08);display:flex;justify-content:space-around;align-items:center;padding:8px 0 20px;z-index:999;box-shadow:0 -4px 20px rgba(0,0,0,0.06);}
.nav-item{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;cursor:pointer;padding:4px 8px;min-width:52px;}
.nav-label{font-size:0.62rem;font-weight:500;color:#9CA3AF;}
.nav-item.active .nav-label{color:#1B4332;font-weight:700;}
.nav-fab{width:52px;height:52px;background:linear-gradient(135deg,#1B4332,#2D6A4F);border-radius:16px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(27,67,50,0.4);margin-top:-24px;}
.kilimo-card{background:white;border-radius:20px;padding:20px;margin:12px 16px;box-shadow:0 2px 12px rgba(0,0,0,0.06);border:1px solid rgba(0,0,0,0.04);}
.kilimo-card-hero{background:linear-gradient(135deg,#1B4332 0%,#2D6A4F 60%,#40916C 100%);border-radius:20px;padding:24px 20px;margin:12px 16px;color:white;position:relative;overflow:hidden;}
.kilimo-card-hero::before{content:'';position:absolute;top:-30px;right:-30px;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,0.07);}
.kilimo-stat{background:white;border-radius:16px;padding:16px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.05);}
.kilimo-stat-number{font-family:'DM Serif Display',serif;font-size:1.8rem;color:#1B4332;line-height:1;}
.kilimo-stat-label{font-size:0.7rem;color:#9CA3AF;margin-top:4px;text-transform:uppercase;letter-spacing:0.05em;font-weight:500;}
.badge-severe{background:#FEE2E2;color:#DC2626;display:inline-flex;align-items:center;padding:4px 10px;border-radius:20px;font-size:0.72rem;font-weight:600;}
.badge-moderate{background:#FEF3C7;color:#D97706;display:inline-flex;align-items:center;padding:4px 10px;border-radius:20px;font-size:0.72rem;font-weight:600;}
.badge-healthy{background:#D1FAE5;color:#059669;display:inline-flex;align-items:center;padding:4px 10px;border-radius:20px;font-size:0.72rem;font-weight:600;}
.kilimo-alert{background:#FFFBEB;border:1px solid #FDE68A;border-left:4px solid #F59E0B;border-radius:12px;padding:14px 16px;margin:8px 16px;}
.kilimo-upload-card{border:2px dashed #D1FAE5;border-radius:16px;padding:24px 16px;text-align:center;background:#F0FDF4;}
.kilimo-tip{background:white;border-radius:14px;padding:14px 10px;text-align:center;box-shadow:0 1px 6px rgba(0,0,0,0.05);}
.kilimo-tip-icon{font-size:1.5rem;margin-bottom:6px;}
.kilimo-tip-text{font-size:0.72rem;color:#6B7280;font-weight:500;line-height:1.3;}
.kilimo-result-card{background:white;border-radius:20px;padding:20px;margin:12px 16px;box-shadow:0 2px 12px rgba(0,0,0,0.08);}
.kilimo-disease-name{font-family:'DM Serif Display',serif;font-size:1.6rem;color:#1A1A1A;line-height:1.2;margin:4px 0 8px;}
.kilimo-confidence{font-family:'DM Serif Display',serif;font-size:2.4rem;line-height:1;}
.stButton>button{font-family:'DM Sans',sans-serif!important;font-weight:600!important;border-radius:14px!important;height:52px!important;font-size:0.95rem!important;letter-spacing:0.01em!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#1B4332,#2D6A4F)!important;border:none!important;box-shadow:0 4px 12px rgba(27,67,50,0.25)!important;}
.stButton>button[kind="secondary"]{background:white!important;border:2px solid #E5E7EB!important;color:#1A1A1A!important;}
.stTextInput>div>div>input{border-radius:12px!important;border:2px solid #E5E7EB!important;font-family:'DM Sans',sans-serif!important;font-size:0.95rem!important;}
.stTabs [data-baseweb="tab-list"]{background:#F3F4F6;border-radius:12px;padding:4px;gap:4px;}
.stTabs [data-baseweb="tab"]{border-radius:10px!important;font-family:'DM Sans',sans-serif!important;font-weight:500!important;font-size:0.85rem!important;color:#6B7280!important;padding:8px 16px!important;}
.stTabs [aria-selected="true"]{background:white!important;color:#1B4332!important;font-weight:600!important;box-shadow:0 1px 4px rgba(0,0,0,0.1)!important;}
.kilimo-profile-hero{background:linear-gradient(135deg,#1B4332,#2D6A4F);border-radius:20px;padding:24px 20px;margin:12px 16px;color:white;}
.kilimo-profile-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,0.15);border-radius:14px;overflow:hidden;margin-top:16px;}
.kilimo-profile-stat{background:rgba(255,255,255,0.08);padding:12px 8px;text-align:center;}
.kilimo-profile-stat-num{font-family:'DM Serif Display',serif;font-size:1.4rem;color:white;line-height:1;}
.kilimo-profile-stat-label{font-size:0.65rem;color:rgba(255,255,255,0.7);margin-top:3px;text-transform:uppercase;letter-spacing:0.05em;}
.kilimo-pill{display:inline-block;background:#F0FDF4;color:#166534;border-radius:20px;padding:3px 10px;font-size:0.7rem;font-weight:500;margin:2px;}
.kilimo-vet-card{background:white;border-radius:16px;padding:16px;margin:8px 16px;box-shadow:0 1px 6px rgba(0,0,0,0.05);border:1px solid rgba(0,0,0,0.04);}
.kilimo-landing{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 24px;text-align:center;background:#FAFAF8;}
.kilimo-landing-logo{font-family:'DM Serif Display',serif;font-size:3rem;color:#1B4332;letter-spacing:-0.03em;line-height:1;margin:20px 0 8px;}
.kilimo-landing-tag{font-size:0.8rem;color:#6B7280;letter-spacing:0.15em;text-transform:uppercase;}
.kilimo-leaf-mark{width:80px;height:80px;background:linear-gradient(135deg,#1B4332,#40916C);border-radius:24px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;box-shadow:0 8px 32px rgba(27,67,50,0.3);margin:0 auto;}
.main .block-container>div{padding:0!important;}

/* Hide duplicate streamlit nav buttons */
div[data-testid="stHorizontalBlock"] .stButton button {
    opacity: 0 !important;
    height: 60px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    position: absolute !important;
    width: 100% !important;
}
div[data-testid="stHorizontalBlock"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 1000 !important;
    height: 72px !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}
/* Background fix - make page grey so white cards pop */
[data-testid="stAppViewContainer"] > .main {
    background: #F0F2F0 !important;
}
.block-container {
    background: #F0F2F0 !important;
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
    main()
