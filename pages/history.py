import streamlit as st
import json
from datetime import datetime, timezone

def render_header():
    dark = st.session_state.get("dark_mode", False)
    card = "#242424" if dark else "#FFFFFF"
    border = "#333333" if dark else "#E5E7EB"
    st.markdown(
        '<div class="kheader" style="background:'+card+';border-bottom:1px solid '+border+';">'
        '<div class="klogo"><svg width="24" height="24" viewBox="0 0 24 24" fill="none">'
        '<path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" fill="#52B788" stroke="#1B4332" stroke-width="1.5" stroke-linejoin="round"/>'
        '</svg>Kilimo <em>AI</em></div></div>',
        unsafe_allow_html=True)

def render_bottom_nav():
    dark = st.session_state.get("dark_mode", False)
    page = st.session_state.get("page", "home")
    card = "#242424" if dark else "#FFFFFF"
    border = "#333333" if dark else "#E5E7EB"
    muted = "#9CA3AF"
    active = "#1B4332"
    def s(p): return active if page==p else muted
    def nc(p): return "knav-item active" if page==p else "knav-item"
    st.markdown(
        '<div class="knav" style="background:'+card+';border-top:1px solid '+border+';">'
        '<div class="'+nc("home")+'">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">'
        '<path d="M3 9.5L12 3L21 9.5V20C21 20.55 20.55 21 20 21H15V15H9V21H4C3.45 21 3 20.55 3 20V9.5Z" stroke="'+s("home")+'" stroke-width="2" stroke-linejoin="round"/>'
        '</svg><span class="knav-label">Home</span></div>'
        '<div class="'+nc("history")+'">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">'
        '<circle cx="12" cy="12" r="9" stroke="'+s("history")+'" stroke-width="2"/>'
        '<path d="M12 7V12L15 14" stroke="'+s("history")+'" stroke-width="2" stroke-linecap="round"/>'
        '</svg><span class="knav-label">History</span></div>'
        '<div class="knav-item"><div class="knav-fab">'
        '<svg width="24" height="24" viewBox="0 0 24 24" fill="none">'
        '<path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>'
        '<path d="M12 9V15M9 12H15" stroke="white" stroke-width="2" stroke-linecap="round"/>'
        '</svg></div><span class="knav-label">Scan</span></div>'
        '<div class="'+nc("vets")+'">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">'
        '<path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="'+s("vets")+'" stroke-width="2"/>'
        '<path d="M12 7V11M10 9H14" stroke="'+s("vets")+'" stroke-width="2" stroke-linecap="round"/>'
        '</svg><span class="knav-label">Vets</span></div>'
        '<div class="'+nc("profile")+'">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">'
        '<circle cx="12" cy="8" r="4" stroke="'+s("profile")+'" stroke-width="2"/>'
        '<path d="M4 20C4 17 7.58 14 12 14C16.42 14 20 17 20 20" stroke="'+s("profile")+'" stroke-width="2" stroke-linecap="round"/>'
        '</svg><span class="knav-label">Profile</span></div>'
        '</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i,(p,label) in enumerate([("home","Home"),("history","History"),("scan","Scan"),("vets","Vets"),("profile","Profile")]):
        with cols[i]:
            if st.button(label, key="nav_"+p+"_hist", use_container_width=True):
                st.session_state["page"] = p
                st.rerun()

def render_history():
    from utils.advisory import get_user_scans, update_feedback
    dark = st.session_state.get("dark_mode", False)
    text = "#F5F5F5" if dark else "#1A1A1A"
    muted = "#9CA3AF"
    card = "#242424" if dark else "#FFFFFF"
    border = "#333333" if dark else "#E5E7EB"

    render_header()

    if not st.session_state.get("authenticated"):
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;'>"
            "<div style='font-size:3rem;margin-bottom:12px;'>🔒</div>"
            "<div style='font-family:DM Serif Display,serif;font-size:1.4rem;color:"+text+";margin-bottom:8px;'>Login to view history</div>"
            "<div style='font-size:0.85rem;color:"+muted+";'>Create a free account to save and track all your scans.</div>"
            "</div>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, type="primary"):
            st.session_state["guest"] = False
            st.session_state["auth_mode"] = "signup"
            st.rerun()
        render_bottom_nav()
        return

    st.markdown("<div style='padding:14px 16px 8px;font-family:DM Serif Display,serif;font-size:1.3rem;color:"+text+";'>History</div>", unsafe_allow_html=True)

    user_id = st.session_state["user"].get("id")
    scans = get_user_scans(user_id)

    if not scans:
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;'>"
            "<div style='font-size:3rem;margin-bottom:12px;'>🌿</div>"
            "<div style='font-family:DM Serif Display,serif;font-size:1.4rem;color:"+text+";margin-bottom:8px;'>No scans yet</div>"
            "<div style='font-size:0.85rem;color:"+muted+";'>Start scanning your crops to build your history.</div>"
            "</div>", unsafe_allow_html=True)
        if st.button("Start Scanning", use_container_width=True, type="primary"):
            st.session_state["page"] = "scan"
            st.rerun()
        render_bottom_nav()
        return

    search = st.text_input("🔍 Search scans", placeholder="Search by disease or crop...", key="hist_search")
    filter_tabs = st.tabs(["All","Diseases","Healthy"])

    diseased = [s for s in scans if "healthy" not in s.get("disease","").lower()]
    healthy = [s for s in scans if "healthy" in s.get("disease","").lower()]

    c1,c2 = st.columns(2)
    with c1:
        st.markdown(
            "<div style='background:#FEE2E2;border-radius:12px;padding:12px;text-align:center;margin:4px 0;'>"
            "<div style='font-family:DM Serif Display,serif;font-size:1.5rem;color:#DC2626;'>"+str(len(diseased))+"</div>"
            "<div style='font-size:0.65rem;color:#991B1B;text-transform:uppercase;letter-spacing:0.05em;margin-top:2px;'>🔴 Diseased</div>"
            "</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(
            "<div style='background:#D1FAE5;border-radius:12px;padding:12px;text-align:center;margin:4px 0;'>"
            "<div style='font-family:DM Serif Display,serif;font-size:1.5rem;color:#059669;'>"+str(len(healthy))+"</div>"
            "<div style='font-size:0.65rem;color:#166534;text-transform:uppercase;letter-spacing:0.05em;margin-top:2px;'>🟢 Healthy</div>"
            "</div>", unsafe_allow_html=True)

    selected_tab = 0
    with filter_tabs[0]:
        filtered = scans
        selected_tab = 0
    with filter_tabs[1]:
        filtered = diseased
        selected_tab = 1
    with filter_tabs[2]:
        filtered = healthy
        selected_tab = 2

    if search:
        filtered = [s for s in filtered if
            search.lower() in s.get("disease","").lower() or
            search.lower() in s.get("crop","").lower()]

    st.markdown("<div style='padding:10px 16px 6px;font-size:0.8rem;font-weight:600;color:"+muted+";'>"+str(len(filtered))+" SCAN"+"S" if len(filtered)!=1 else ""+"</div>", unsafe_allow_html=True)

    for scan in filtered:
        disease = scan.get("disease","Unknown")
        crop = scan.get("crop","Unknown")
        conf = scan.get("confidence",0)
        timestamp = scan.get("timestamp","")
        scan_id = scan.get("id","")
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z","+00:00"))
            date_str = dt.strftime("%b %d, %Y • %I:%M %p")
            days_ago = (datetime.now(timezone.utc)-dt).days
        except:
            date_str = timestamp[:10] if timestamp else ""
            days_ago = 0
        badge = "bsevere" if conf>=0.85 else "bmoderate" if conf>=0.60 else "bhealthy"

        with st.expander("🌿 "+disease+" — "+crop+" | "+date_str):
            st.markdown(
                "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
                "<div><div style='font-weight:700;font-size:0.95rem;color:"+text+";'>"+disease+"</div>"
                "<div style='font-size:0.78rem;color:"+muted+";'>"+crop+" • "+date_str+"</div></div>"
                "<span class='"+badge+"'>"+str(int(conf*100))+"%</span>"
                "</div>", unsafe_allow_html=True)

            treatment = scan.get("treatment",{})
            if isinstance(treatment,str):
                try: treatment = json.loads(treatment)
                except: treatment = {}

            if treatment:
                t1,t2,t3 = st.tabs(["⚡ Immediate","💊 Treatment","🛡️ Prevention"])
                with t1: st.write(treatment.get("immediate_action","No data"))
                with t2: st.write(treatment.get("treatment","No data"))
                with t3: st.write(treatment.get("prevention","No data"))

            if days_ago >= 7 and "healthy" not in disease.lower():
                st.markdown(
                    "<div style='background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:10px;margin-top:8px;'>"
                    "<div style='font-size:0.82rem;color:#92400E;font-weight:600;margin-bottom:6px;'>💬 Did the treatment work?</div>"
                    "</div>", unsafe_allow_html=True)
                c1,c2,c3 = st.columns(3)
                with c1:
                    if st.button("✅ Yes", key="yes_"+str(scan_id)):
                        update_feedback(scan_id,"yes")
                        st.success("Thanks!")
                with c2:
                    if st.button("⚠️ Partly", key="partial_"+str(scan_id)):
                        update_feedback(scan_id,"partially")
                        st.info("Consider consulting a vet.")
                with c3:
                    if st.button("❌ No", key="no_"+str(scan_id)):
                        update_feedback(scan_id,"no")
                        st.warning("Please consult a vet.")

    render_bottom_nav()
