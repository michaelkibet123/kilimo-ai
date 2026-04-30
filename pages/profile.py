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
    
    cols = st.columns(5)
    for i,(p,label) in enumerate([("home","Home"),("history","History"),("scan","Scan"),("vets","Vets"),("profile","Profile")]):
        with cols[i]:
            if st.button(label, key="nav_"+p+"_prof", use_container_width=True):
                st.session_state["page"] = p
                st.rerun()


def render_profile():
    from utils.advisory import get_supabase, get_user_scans
    dark = st.session_state.get("dark_mode", False)
    text = "#F5F5F5" if dark else "#1A1A1A"
    muted = "#9CA3AF"
    card = "#242424" if dark else "#FFFFFF"
    border = "#333333" if dark else "#E5E7EB"
    bg = "#1A1A1A" if dark else "#EEF2EE"

    render_header()

    if not st.session_state.get("authenticated"):
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;'>"
            "<div style='font-size:3rem;margin-bottom:12px;'>👤</div>"
            "<div style='font-family:DM Serif Display,serif;font-size:1.4rem;color:"+text+";margin-bottom:8px;'>Login to view profile</div>"
            "<div style='font-size:0.85rem;color:"+muted+";'>Create a free account to access all features.</div>"
            "</div>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, type="primary"):
            st.session_state["guest"] = False
            st.session_state["auth_mode"] = "signup"
            st.rerun()
        render_bottom_nav()
        return

    supabase = get_supabase()
    user_id = st.session_state["user"].get("id")
    profile = st.session_state.get("profile_data") or {}
    full_name = profile.get("full_name","Farmer")
    email = st.session_state["user"].get("email","")
    phone = profile.get("phone","")
    region = profile.get("region","")
    crops = profile.get("crops_grown",[]) or []
    initials = (full_name[0] if full_name else "F").upper()
    if len(full_name.split()) >= 2:
        initials = (full_name.split()[0][0]+full_name.split()[1][0]).upper()

    scans = get_user_scans(user_id)
    total = len(scans)
    diseased = len([s for s in scans if "healthy" not in s.get("disease","").lower()])
    crops_n = len(set([s.get("crop","") for s in scans]))

    st.markdown(
        "<div class='kprofile-hero' style='margin:10px 12px;'>"
        "<div style='display:flex;align-items:center;gap:14px;'>"
        "<div style='width:56px;height:56px;border-radius:16px;background:rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;font-family:DM Serif Display,serif;font-size:1.3rem;color:white;flex-shrink:0;'>"+initials+"</div>"
        "<div>"
        "<div style='font-family:DM Serif Display,serif;font-size:1.2rem;color:white;'>"+full_name+"</div>"
        "<div style='font-size:0.78rem;color:rgba(255,255,255,0.75);'>"+email+"</div>"
        "<div style='font-size:0.72rem;color:rgba(255,255,255,0.6);margin-top:2px;'>📍 "+region+"</div>"
        "</div></div>"
        "<div class='kprofile-stats'>"
        "<div class='kprofile-stat'><div class='kprofile-stat-n'>"+str(total)+"</div><div class='kprofile-stat-l'>Scans</div></div>"
        "<div class='kprofile-stat' style='border-left:1px solid rgba(255,255,255,0.15);border-right:1px solid rgba(255,255,255,0.15);'>"
        "<div class='kprofile-stat-n'>"+str(diseased)+"</div><div class='kprofile-stat-l'>Diseases</div></div>"
        "<div class='kprofile-stat'><div class='kprofile-stat-n'>"+str(crops_n)+"</div><div class='kprofile-stat-l'>Crops</div></div>"
        "</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='padding:12px 16px 4px;font-size:0.78rem;font-weight:600;color:"+muted+";'>ACCOUNT SETTINGS</div>", unsafe_allow_html=True)

    with st.expander("✏️  Edit Profile"):
        new_name = st.text_input("Full Name", value=full_name, key="edit_name")
        new_phone = st.text_input("Phone", value=phone, key="edit_phone")
        counties = ["Nairobi","Nakuru","Kisumu","Mombasa","Uasin Gishu","Nyeri","Kiambu","Kisii","Meru","Machakos","Kakamega","Embu","Kirinyaga","Other"]
        idx = counties.index(region) if region in counties else 0
        new_region = st.selectbox("County", counties, index=idx, key="edit_region")
        new_crops = st.multiselect("Crops", ["Maize","Tomato","Potato","Pepper","Beans","Wheat"], default=crops, key="edit_crops")
        if st.button("Save Changes", use_container_width=True, type="primary", key="save_profile"):
            try:
                supabase.table("users").update({"full_name":new_name,"phone":new_phone,"region":new_region,"crops_grown":new_crops}).eq("id",user_id).execute()
                st.session_state["profile_data"] = {"full_name":new_name,"phone":new_phone,"region":new_region,"crops_grown":new_crops}
                st.success("Profile updated!")
                st.rerun()
            except Exception as e:
                st.error("Update failed: "+str(e))

    with st.expander("📷  Profile Photo"):
        photo_src = st.radio("Source", ["Upload from gallery","Use camera"], key="photo_src")
        if photo_src == "Upload from gallery":
            photo_file = st.file_uploader("Photo", type=["jpg","jpeg","png"], label_visibility="collapsed", key="photo_upload")
        else:
            photo_file = st.camera_input("Photo", label_visibility="collapsed", key="photo_cam")
        if photo_file:
            if st.button("Upload Photo", use_container_width=True, key="upload_photo"):
                try:
                    pb = photo_file.read()
                    fname = "profile_"+str(user_id)+".jpg"
                    supabase.storage.from_("scan-images").upload(fname, pb, {"content-type":"image/jpeg","upsert":"true"})
                    st.success("Photo updated!")
                except Exception as e:
                    st.error("Upload failed: "+str(e))

    with st.expander("🔑  Change Password"):
        new_pw = st.text_input("New Password", type="password", key="new_pw")
        confirm_pw = st.text_input("Confirm Password", type="password", key="confirm_pw")
        if st.button("Update Password", use_container_width=True, key="update_pw"):
            if new_pw != confirm_pw: st.error("Passwords do not match.")
            elif len(new_pw) < 6: st.error("Min 6 characters.")
            else:
                try:
                    supabase.auth.update_user({"password":new_pw})
                    st.success("Password updated!")
                except Exception as e:
                    st.error("Failed: "+str(e))

    with st.expander("🔔  Notifications"):
        notif = st.toggle("Enable push notifications", value=st.session_state.get("notification_permission",False), key="notif_toggle")
        st.session_state["notification_permission"] = notif
        if notif: st.success("Push notifications enabled")
        else: st.info("In-app notifications only")

    with st.expander("🌙  Dark Mode"):
        dark_toggle = st.toggle("Enable dark mode", value=dark, key="dark_toggle")
        if dark_toggle != dark:
            st.session_state["dark_mode"] = dark_toggle
            st.rerun()

    with st.expander("ℹ️  About Kilimo AI"):
        st.markdown(
            "<div style='font-size:0.85rem;color:"+text+";line-height:1.6;'>"
            "<b>Kilimo AI v1.0</b><br>"
            "AI-powered crop disease diagnosis for Kenyan farmers.<br><br>"
            "Model: MobileNetV2 trained on 26,639 images<br>"
            "Accuracy: <b>97%</b> across 19 disease classes<br>"
            "Crops: Maize, Tomato, Potato, Pepper<br><br>"
            "Built to support smallholder farmers with limited access to agricultural extension services."
            "</div>", unsafe_allow_html=True)

    with st.expander("❓  Help & Support"):
        st.markdown(
            "<div style='font-size:0.85rem;color:"+text+";line-height:1.6;'>"
            "<b>How to use Kilimo AI:</b><br>"
            "1. Select your crop on the Scan tab<br>"
            "2. Upload a clear photo of the affected leaf<br>"
            "3. Tap Analyse Leaf<br>"
            "4. Follow the treatment plan<br><br>"
            "<b>For best results:</b><br>"
            "• Use natural lighting<br>"
            "• Focus clearly on the affected area<br>"
            "• Avoid blurry or dark images"
            "</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🚪  Log Out", use_container_width=True, key="logout"):
        try: supabase.auth.sign_out()
        except: pass
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    render_bottom_nav()
