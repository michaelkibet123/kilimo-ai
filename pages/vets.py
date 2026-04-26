import streamlit as st
from utils.advisory import get_vets
def render_header():
    st.markdown('<div class="kilimo-header"><div class="kilimo-logo">🌿 Kilimo AI</div></div>', unsafe_allow_html=True)

def render_bottom_nav():
    cols = st.columns(5)
    pages = [('home','🏠','Home'),('scan','📷','Scan'),('history','🕐','History'),('vets','🏪','Vets'),('profile','👤','Profile')]
    for i,(p,icon,label) in enumerate(pages):
        with cols[i]:
            if st.button(f"{icon}\n{label}",key=f"nav_{p}",use_container_width=True):
                st.session_state['page']=p
                st.rerun()

def render_vets():
    
    render_header()

    st.markdown("## Vets & Agrovets")

    counties = ['All Counties', 'Nairobi', 'Nakuru', 'Kisumu', 'Mombasa', 
                'Uasin Gishu', 'Nyeri', 'Kiambu', 'Kisii', 'Meru', 
                'Machakos', 'Kakamega', 'Embu', 'Kirinyaga']
    
    selected_county = st.selectbox("Select County", counties, key="county_filter")
    
    county = None if selected_county == 'All Counties' else selected_county
    vets = get_vets(county)

    if not vets:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem;">🏪</div>
            <h3 style="color:#1B4332;">No vets found</h3>
            <p style="color:#6C757D;">Try selecting a different county.</p>
        </div>
        """, unsafe_allow_html=True)
        render_bottom_nav()
        return

    st.markdown(f"**{len(vets)} location{'s' if len(vets) != 1 else ''} found**")

    for vet in vets:
        name = vet.get('name', '')
        county_name = vet.get('county', '')
        phone = vet.get('phone', '')
        services = vet.get('services', [])

        services_html = ''.join([
            f'<span style="background:#F0FDF4; color:#166534; padding:0.15rem 0.5rem; '
            f'border-radius:20px; font-size:0.7rem; margin-right:0.3rem;">{s}</span>'
            for s in services
        ])

        st.markdown(f"""
        <div style="background:white; border:1px solid #F0F0F0; border-radius:12px; 
                    padding:1rem; margin:0.5rem 0; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:0.95rem; color:#212529;">{name}</div>
                    <div style="color:#6C757D; font-size:0.8rem; margin:0.2rem 0;">
                        📍 {county_name}
                    </div>
                    <div style="margin-top:0.4rem;">{services_html}</div>
                </div>
                <a href="tel:{phone}" style="text-decoration:none;">
                    <div style="background:#1B4332; color:white; border-radius:50%; 
                                width:40px; height:40px; display:flex; align-items:center; 
                                justify-content:center; font-size:1.1rem; margin-left:0.5rem;">
                        📞
                    </div>
                </a>
            </div>
            <div style="font-size:0.8rem; color:#6C757D; margin-top:0.5rem;">
                {phone}
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_bottom_nav()
