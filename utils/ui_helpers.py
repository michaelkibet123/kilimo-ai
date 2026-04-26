import streamlit as st

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
            if st.button(f"{icon}\n{label}", key=f"nav_{p}", use_container_width=True):
                st.session_state['page'] = p
                st.rerun()

def get_initials(name):
    if not name:
        return 'U'
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return parts[0][0].upper()
