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
    def nc(p): return "active" if page==p else ""
    st.markdown(
        '<div class="knav" style="background:'+card+';border-bottom:1px solid '+border+';">' 
        '<div class="knav-icons">' 
        '<div class="knav-item '+nc("home")+'">' 
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">' 
        '<path d="M3 9.5L12 3L21 9.5V20C21 20.55 20.55 21 20 21H15V15H9V21H4C3.45 21 3 20.55 3 20V9.5Z" stroke="'+s("home")+'" stroke-width="2" stroke-linejoin="round"/>' 
        '</svg><span class="knav-label">Home</span></div>' 
        '<div class="knav-item '+nc("history")+'">' 
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">' 
        '<circle cx="12" cy="12" r="9" stroke="'+s("history")+'" stroke-width="2"/>' 
        '<path d="M12 7V12L15 14" stroke="'+s("history")+'" stroke-width="2" stroke-linecap="round"/>' 
        '</svg><span class="knav-label">History</span></div>' 
        '<div class="knav-item knav-scan '+nc("scan")+'">' 
        '<div class="knav-fab">' 
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none">' 
        '<path d="M12 3C10.5 6 7 7.5 3 7.5C3 14 7 19.5 12 21C17 19.5 21 14 21 7.5C17 7.5 13.5 6 12 3Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>' 
        '<path d="M12 9V15M9 12H15" stroke="white" stroke-width="2" stroke-linecap="round"/>' 
        '</svg></div><span class="knav-label">Scan</span></div>' 
        '<div class="knav-item '+nc("vets")+'">' 
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">' 
        '<path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="'+s("vets")+'" stroke-width="2"/>' 
        '<path d="M12 7V11M10 9H14" stroke="'+s("vets")+'" stroke-width="2" stroke-linecap="round"/>' 
        '</svg><span class="knav-label">Vets</span></div>' 
        '<div class="knav-item '+nc("profile")+'">' 
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none">' 
        '<circle cx="12" cy="8" r="4" stroke="'+s("profile")+'" stroke-width="2"/>' 
        '<path d="M4 20C4 17 7.58 14 12 14C16.42 14 20 17 20 20" stroke="'+s("profile")+'" stroke-width="2" stroke-linecap="round"/>' 
        '</svg><span class="knav-label">Profile</span></div>' 
        '</div></div>',
        unsafe_allow_html=True)
    cols = st.columns(5)
    for i,(p,label) in enumerate([("home","Home"),("history","History"),("scan","Scan"),("vets","Vets"),("profile","Profile")]):
        with cols[i]:
            if st.button(label, key="nav_"+p+suffix, use_container_width=True):
                st.session_state["page"] = p
                st.rerun()


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
