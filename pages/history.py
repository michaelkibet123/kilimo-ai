import streamlit as st
import json
from datetime import datetime, timezone

def render_bottom_nav():
    dark = st.session_state.get("dark_mode", False)
    page = st.session_state.get("page", "home")
    cols = st.columns(5)
    for i,(p,label) in enumerate([("home","🏠\nHome"),("history","🕐\nHistory"),("scan","🌿\nScan"),("vets","📍\nVets"),("profile","👤\nProfile")]):
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

    st.markdown("<div style='padding:14px 16px 8px;font-family:DM Serif Display,serif;font-size:1.3rem;color:"+text+";'>My Scan History</div>", unsafe_allow_html=True)

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

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        show_all = st.button("All", use_container_width=True, key="filter_all",
            type="primary" if st.session_state.get("hist_filter","all")=="all" else "secondary")
    with filter_col2:
        show_dis = st.button("Diseases", use_container_width=True, key="filter_dis",
            type="primary" if st.session_state.get("hist_filter","all")=="diseases" else "secondary")
    with filter_col3:
        show_hlt = st.button("Healthy", use_container_width=True, key="filter_hlt",
            type="primary" if st.session_state.get("hist_filter","all")=="healthy" else "secondary")

    if show_all: st.session_state["hist_filter"] = "all"
    if show_dis: st.session_state["hist_filter"] = "diseases"
    if show_hlt: st.session_state["hist_filter"] = "healthy"

    current_filter = st.session_state.get("hist_filter","all")

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

    if current_filter == "all": filtered = scans
    elif current_filter == "diseases": filtered = diseased
    else: filtered = healthy

    if search:
        filtered = [s for s in filtered if
            search.lower() in s.get("disease","").lower() or
            search.lower() in s.get("crop","").lower()]

    st.markdown(
        "<div style='padding:10px 16px 6px;font-size:0.78rem;font-weight:600;color:"+muted+";'>"+
        str(len(filtered))+" SCAN"+("S" if len(filtered)!=1 else "")+"</div>",
        unsafe_allow_html=True)

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
            date_str = timestamp[:10] if timestamp else "Unknown date"
            days_ago = 0

        badge = "bsevere" if conf>=0.85 else "bmoderate" if conf>=0.60 else "bhealthy"

        with st.expander("🌿 "+disease+" — "+crop+" | "+date_str):
            st.markdown(
                "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>"
                "<div>"
                "<div style='font-family:DM Serif Display,serif;font-size:1.1rem;color:"+text+";'>"+disease+"</div>"
                "<div style='font-size:0.78rem;color:"+muted+";margin-top:2px;'>"+crop+" • "+date_str+"</div>"
                "</div>"
                "<span class='"+badge+"'>"+str(int(conf*100))+"%</span>"
                "</div>", unsafe_allow_html=True)

            treatment = scan.get("treatment",{})
            if isinstance(treatment,str):
                try: treatment = json.loads(treatment)
                except: treatment = {}

            if treatment:
                st.markdown("<div style='font-size:0.78rem;font-weight:600;color:"+muted+";margin-bottom:6px;'>TREATMENT PLAN</div>", unsafe_allow_html=True)
                t1,t2,t3 = st.tabs(["⚡ Immediate","💊 Treatment","🛡️ Prevention"])
                with t1: st.write(treatment.get("immediate_action","No data"))
                with t2: st.write(treatment.get("treatment","No data"))
                with t3: st.write(treatment.get("prevention","No data"))

            if days_ago >= 7 and "healthy" not in disease.lower():
                st.markdown(
                    "<div style='background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:10px;margin-top:10px;'>"
                    "<div style='font-size:0.82rem;color:#92400E;font-weight:600;margin-bottom:8px;'>💬 Did the treatment work?</div>"
                    "</div>", unsafe_allow_html=True)
                fb1,fb2,fb3 = st.columns(3)
                with fb1:
                    if st.button("✅ Yes", key="yes_"+str(scan_id)):
                        update_feedback(scan_id,"yes")
                        st.success("Thanks!")
                with fb2:
                    if st.button("⚠️ Partly", key="partial_"+str(scan_id)):
                        update_feedback(scan_id,"partially")
                        st.info("Consider a vet.")
                with fb3:
                    if st.button("❌ No", key="no_"+str(scan_id)):
                        update_feedback(scan_id,"no")
                        st.warning("Please consult a vet.")

    render_bottom_nav()
