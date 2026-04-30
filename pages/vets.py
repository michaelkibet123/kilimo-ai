import streamlit as st

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
    def bg(p): return "linear-gradient(135deg,#1B4332,#2D6A4F)" if p=="scan" else "transparent"
    def tc(p): return "white" if p=="scan" else (active if page==p else muted)
    def mt(p): return "margin-top:-10px;" if p=="scan" else ""
    def br(p): return "border-radius:12px;" if p=="scan" else ""
    def bs(p): return "box-shadow:0 3px 10px rgba(27,67,50,0.3);" if p=="scan" else ""
    icons = {"home":"🏠","history":"🕐","scan":"🌿","vets":"📍","profile":"👤"}
    labels = {"home":"Home","history":"History","scan":"Scan","vets":"Vets","profile":"Profile"}
    st.markdown(
        "<div style='position:sticky;bottom:0;left:0;right:0;z-index:999;background:"+card+";border-top:1px solid "+border+";box-shadow:0 -2px 12px rgba(0,0,0,0.06);padding:0;'>"
        "<div style='display:flex;width:100%;'>",
        unsafe_allow_html=True)
    pages = ["home","history","scan","vets","profile"]
    for p in pages:
        clicked = st.button(
            icons[p]+"\n"+labels[p],
            key="nav_"+p+"_vets",
            use_container_width=True
        )
        if clicked:
            st.session_state["page"] = p
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_vets():
    from utils.advisory import get_vets
    dark = st.session_state.get("dark_mode", False)
    text = "#F5F5F5" if dark else "#1A1A1A"
    muted = "#9CA3AF"
    card = "#242424" if dark else "#FFFFFF"
    border = "#333333" if dark else "#E5E7EB"

    render_header()

    st.markdown("<div style='padding:14px 16px 8px;font-family:DM Serif Display,serif;font-size:1.3rem;color:"+text+";'>Vets & Agrovets</div>", unsafe_allow_html=True)

    counties = ["All Counties","Nairobi","Nakuru","Kisumu","Mombasa","Uasin Gishu","Nyeri","Kiambu","Kisii","Meru","Machakos","Kakamega","Embu","Kirinyaga"]
    selected = st.selectbox("Select County", counties, key="county_filter")
    county = None if selected == "All Counties" else selected
    vets = get_vets(county)

    if not vets:
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;'>"
            "<div style='font-size:3rem;margin-bottom:12px;'>🏪</div>"
            "<div style='font-family:DM Serif Display,serif;font-size:1.4rem;color:"+text+";'>No vets found</div>"
            "<div style='font-size:0.85rem;color:"+muted+";margin-top:6px;'>Try selecting a different county.</div>"
            "</div>", unsafe_allow_html=True)
        render_bottom_nav()
        return

    st.markdown("<div style='padding:4px 16px 8px;font-size:0.78rem;font-weight:600;color:"+muted+";'>"+str(len(vets))+" LOCATION"+"S" if len(vets)!=1 else ""+" FOUND</div>", unsafe_allow_html=True)

    for vet in vets:
        name = vet.get("name","")
        county_name = vet.get("county","")
        phone = vet.get("phone","")
        services = vet.get("services",[]) or []
        pills = "".join(["<span class='kpill'>"+s+"</span>" for s in services])
        st.markdown(
            "<div class='kvet' style='background:"+card+";border:1px solid "+border+";'>"
            "<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
            "<div style='flex:1;'>"
            "<div style='font-weight:700;font-size:0.95rem;color:"+text+";'>"+name+"</div>"
            "<div style='font-size:0.78rem;color:"+muted+";margin:3px 0;'>📍 "+county_name+"</div>"
            "<div style='margin-top:6px;'>"+pills+"</div>"
            "<div style='font-size:0.78rem;color:"+muted+";margin-top:6px;'>"+phone+"</div>"
            "</div>"
            "<a href='tel:"+phone+"' style='text-decoration:none;margin-left:10px;flex-shrink:0;'>"
            "<div style='width:42px;height:42px;background:#1B4332;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;'>📞</div>"
            "</a></div></div>", unsafe_allow_html=True)

    render_bottom_nav()
