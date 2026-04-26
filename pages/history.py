import streamlit as st
from datetime import datetime, timezone
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

def render_history():
    import json
    from utils.advisory import get_user_scans
    from utils.preprocessor import format_disease_name
    
    render_header()

    if not st.session_state.get('authenticated'):
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem;">🔒</div>
            <h3 style="color:#1B4332;">Login to view your history</h3>
            <p style="color:#6C757D;">Create a free account to save and track all your scans.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, type="primary"):
            st.session_state['guest'] = False
            st.session_state['auth_mode'] = 'signup'
            st.rerun()
        render_bottom_nav()
        return

    st.markdown("## History")

    user_id = st.session_state['user'].get('id')
    scans = get_user_scans(user_id)

    if not scans:
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem;">🌿</div>
            <h3 style="color:#1B4332;">No scans yet</h3>
            <p style="color:#6C757D;">Start scanning your crops to build your history.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Scanning", use_container_width=True, type="primary"):
            st.session_state['page'] = 'scan'
            st.rerun()
        render_bottom_nav()
        return

    search = st.text_input("🔍 Search scans", placeholder="Search by disease or crop...")

    st.markdown("**Filter by crop:**")
    crop_filters = ['All', 'Maize', 'Tomato', 'Potato', 'Pepper']
    selected_crop = st.radio("Crop", crop_filters, horizontal=True, label_visibility='collapsed')

    st.markdown("**Filter by result:**")
    result_filters = ['All', 'Diseases', 'Healthy']
    selected_result = st.radio("Result", result_filters, horizontal=True, label_visibility='collapsed')

    filtered = scans
    if search:
        filtered = [s for s in filtered if 
                   search.lower() in s.get('disease', '').lower() or 
                   search.lower() in s.get('crop', '').lower()]
    if selected_crop != 'All':
        filtered = [s for s in filtered if selected_crop.lower() in s.get('crop', '').lower()]
    if selected_result == 'Diseases':
        filtered = [s for s in filtered if 'healthy' not in s.get('disease', '').lower()]
    elif selected_result == 'Healthy':
        filtered = [s for s in filtered if 'healthy' in s.get('disease', '').lower()]

    if len(scans) > 1:
        st.markdown("### Disease Frequency (Last 30 days)")
        diseased_count = len([s for s in scans if 'healthy' not in s.get('disease', '').lower()])
        healthy_count = len([s for s in scans if 'healthy' in s.get('disease', '').lower()])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background:#FEE2E2; border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:1.5rem; font-weight:700; color:#DC2626;">{diseased_count}</div>
                <div style="font-size:0.75rem; color:#991B1B;">🔴 Diseased</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:#D1FAE5; border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:1.5rem; font-weight:700; color:#16A34A;">{healthy_count}</div>
                <div style="font-size:0.75rem; color:#166534;">🟢 Healthy</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"### {len(filtered)} Scan{'s' if len(filtered) != 1 else ''}")

    for scan in filtered:
        disease = scan.get('disease', 'Unknown')
        crop = scan.get('crop', 'Unknown')
        conf = scan.get('confidence', 0)
        timestamp = scan.get('timestamp', '')
        scan_id = scan.get('id', '')

        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime('%b %d, %Y • %I:%M %p')
        except Exception:
            date_str = timestamp[:10] if timestamp else 'Unknown date'

        badge_class = 'badge-high' if conf >= 0.85 else 'badge-medium' if conf >= 0.60 else 'badge-low'
        badge_label = 'High' if conf >= 0.85 else 'Medium' if conf >= 0.60 else 'Low'

        with st.expander(f"🌿 {disease} — {crop} | {date_str}"):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:700; font-size:1rem;">{disease}</div>
                    <div style="color:#6C757D; font-size:0.8rem;">{crop} • {date_str}</div>
                </div>
                <div class="disease-badge {badge_class}">{int(conf*100)}% {badge_label}</div>
            </div>
            """, unsafe_allow_html=True)

            treatment = scan.get('treatment', {})
            if treatment:
                if isinstance(treatment, str):
                    import json
                    try:
                        treatment = json.loads(treatment)
                    except Exception:
                        treatment = {}

                t1, t2, t3 = st.tabs(["⚡ Immediate", "💊 Treatment", "🛡️ Prevention"])
                with t1:
                    st.write(treatment.get('immediate_action', 'No data'))
                with t2:
                    st.write(treatment.get('treatment', 'No data'))
                with t3:
                    st.write(treatment.get('prevention', 'No data'))

            days_ago = 0
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_ago = (datetime.now(timezone.utc) - dt).days
            except Exception:
                pass

            if days_ago >= 7 and 'healthy' not in disease.lower():
                st.markdown("""
                <div style="background:#FFFBEB; border:1px solid #FDE68A; 
                            border-radius:10px; padding:0.75rem; margin-top:0.5rem;">
                    <div style="font-size:0.85rem; color:#92400E; font-weight:600;">
                        💬 Did the treatment work?
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Yes", key=f"yes_{scan_id}"):
                        from utils.advisory import update_feedback
                        update_feedback(scan_id, 'yes')
                        st.success("Thanks for the feedback!")
                with col2:
                    if st.button("⚠️ Partially", key=f"partial_{scan_id}"):
                        from utils.advisory import update_feedback
                        update_feedback(scan_id, 'partially')
                        st.info("Thanks! Consider consulting a vet.")
                with col3:
                    if st.button("❌ No", key=f"no_{scan_id}"):
                        from utils.advisory import update_feedback
                        update_feedback(scan_id, 'no')
                        st.warning("Sorry to hear that. Please consult a vet.")

    render_bottom_nav()
