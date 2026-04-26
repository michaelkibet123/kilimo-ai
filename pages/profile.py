import streamlit as st
from utils.advisory import get_supabase, get_user_scans

def render_profile():
    from utils.ui_helpers import render_header, render_bottom_nav
    render_header()

    if not st.session_state.get('authenticated'):
        st.markdown("""
        <div style="text-align:center; padding:3rem 1rem;">
            <div style="font-size:3rem;">👤</div>
            <h3 style="color:#1B4332;">Login to view your profile</h3>
            <p style="color:#6C757D;">Create a free account to access all features.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, type="primary"):
            st.session_state['guest'] = False
            st.session_state['auth_mode'] = 'signup'
            st.rerun()
        render_bottom_nav()
        return

    supabase = get_supabase()
    user_id = st.session_state['user'].get('id')
    profile = st.session_state.get('profile_data', {})

    full_name = profile.get('full_name', 'Farmer') if profile else 'Farmer'
    email = st.session_state['user'].get('email', '')
    phone = profile.get('phone', '') if profile else ''
    region = profile.get('region', '') if profile else ''
    crops = profile.get('crops_grown', []) if profile else []

    initials = ''.join([p[0].upper() for p in full_name.split()[:2]]) if full_name else 'F'

    scans = get_user_scans(user_id)
    total_scans = len(scans)
    diseases_found = len([s for s in scans if 'healthy' not in s.get('disease', '').lower()])
    crops_monitored = len(set([s.get('crop', '') for s in scans]))

    st.markdown(f"""
    <div style="background:#1B4332; border-radius:16px; padding:1.5rem; 
                color:white; margin-bottom:1rem;">
        <div style="display:flex; align-items:center; gap:1rem;">
            <div style="width:60px; height:60px; border-radius:50%; background:white; 
                        color:#1B4332; display:flex; align-items:center; justify-content:center;
                        font-size:1.4rem; font-weight:700;">{initials}</div>
            <div>
                <div style="font-size:1.2rem; font-weight:700;">{full_name}</div>
                <div style="font-size:0.85rem; opacity:0.85;">{email}</div>
                <div style="font-size:0.8rem; opacity:0.7; margin-top:0.2rem;">📍 {region}</div>
            </div>
        </div>
        <div style="display:flex; gap:1rem; margin-top:1rem; 
                    background:rgba(255,255,255,0.1); border-radius:10px; padding:0.75rem;">
            <div style="flex:1; text-align:center;">
                <div style="font-size:1.3rem; font-weight:700;">{total_scans}</div>
                <div style="font-size:0.7rem; opacity:0.8;">Total Scans</div>
            </div>
            <div style="flex:1; text-align:center; border-left:1px solid rgba(255,255,255,0.2);">
                <div style="font-size:1.3rem; font-weight:700;">{diseases_found}</div>
                <div style="font-size:0.7rem; opacity:0.8;">Diseases Found</div>
            </div>
            <div style="flex:1; text-align:center; border-left:1px solid rgba(255,255,255,0.2);">
                <div style="font-size:1.3rem; font-weight:700;">{crops_monitored}</div>
                <div style="font-size:0.7rem; opacity:0.8;">Crops Monitored</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Edit Profile")
    with st.expander("✏️ Edit your information"):
        new_name = st.text_input("Full Name", value=full_name, key="edit_name")
        new_phone = st.text_input("Phone", value=phone, key="edit_phone")
        
        counties = ['Nairobi', 'Nakuru', 'Kisumu', 'Mombasa', 'Uasin Gishu',
                   'Nyeri', 'Kiambu', 'Kisii', 'Meru', 'Machakos', 
                   'Kakamega', 'Embu', 'Kirinyaga', 'Other']
        current_idx = counties.index(region) if region in counties else 0
        new_region = st.selectbox("County", counties, index=current_idx, key="edit_region")
        
        new_crops = st.multiselect(
            "Crops you grow",
            ['Maize', 'Tomato', 'Potato', 'Pepper', 'Beans', 'Wheat'],
            default=crops if crops else [],
            key="edit_crops"
        )

        if st.button("Save Changes", use_container_width=True, type="primary", key="save_profile"):
            try:
                supabase.table('users').update({
                    'full_name': new_name,
                    'phone': new_phone,
                    'region': new_region,
                    'crops_grown': new_crops
                }).eq('id', user_id).execute()
                
                st.session_state['profile_data'] = {
                    'full_name': new_name,
                    'phone': new_phone,
                    'region': new_region,
                    'crops_grown': new_crops
                }
                st.success("Profile updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

    st.markdown("### Profile Photo")
    with st.expander("📷 Upload profile photo"):
        photo_option = st.radio("Choose source", ["Upload from gallery", "Use camera"], 
                               key="photo_source")
        if photo_option == "Upload from gallery":
            photo_file = st.file_uploader("Choose photo", type=['jpg', 'jpeg', 'png'],
                                         label_visibility='collapsed', key="photo_upload")
        else:
            photo_file = st.camera_input("Take photo", label_visibility='collapsed', 
                                        key="photo_camera")
        
        if photo_file:
            if st.button("Upload Photo", use_container_width=True, key="upload_photo_btn"):
                try:
                    photo_bytes = photo_file.read()
                    filename = f"profile_{user_id}.jpg"
                    supabase.storage.from_('scan-images').upload(
                        filename, photo_bytes,
                        {'content-type': 'image/jpeg', 'upsert': 'true'}
                    )
                    st.success("Profile photo updated!")
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

    st.markdown("### Account Settings")
    
    settings = [
        ("🔔", "Notification Preferences"),
        ("💾", "Saved Results"),
        ("📥", "Download Reports"),
        ("❓", "Help & Support"),
        ("ℹ️", "About Kilimo AI"),
    ]
    
    for icon, label in settings:
        with st.expander(f"{icon} {label}"):
            if label == "Notification Preferences":
                notif = st.toggle("Enable push notifications", 
                                 value=st.session_state.get('notification_permission', False),
                                 key="notif_toggle")
                st.session_state['notification_permission'] = notif
                if notif:
                    st.success("Push notifications enabled")
                else:
                    st.info("You will receive in-app notifications only")
            
            elif label == "About Kilimo AI":
                st.markdown("""
                **Kilimo AI v1.0**  
                AI-powered crop disease diagnosis for Kenyan farmers.
                
                Built with MobileNetV2 trained on 26,639 images across 19 disease classes.
                Model accuracy: **98.12%**
                
                Developed to support smallholder farmers with limited access to agricultural extension services.
                """)
            
            elif label == "Help & Support":
                st.markdown("""
                **How to use Kilimo AI:**
                1. Select your crop on the Scan page
                2. Upload a clear photo of the affected leaf
                3. Tap Analyse Leaf
                4. Review diagnosis and follow treatment plan
                
                **For best results:**
                - Use natural lighting
                - Focus clearly on the affected area
                - Avoid blurry or dark images
                """)
            
            elif label == "Saved Results":
                if scans:
                    st.write(f"You have {total_scans} saved scans.")
                    if st.button("View History", key="goto_history"):
                        st.session_state['page'] = 'history'
                        st.rerun()
                else:
                    st.write("No saved scans yet.")
            
            elif label == "Download Reports":
                st.write("Download reports from individual scans in your History page.")

    st.markdown("### Change Password")
    with st.expander("🔑 Change your password"):
        new_password = st.text_input("New Password", type="password", key="new_pass")
        confirm_new = st.text_input("Confirm New Password", type="password", key="confirm_new_pass")
        if st.button("Update Password", use_container_width=True, key="update_pass_btn"):
            if new_password != confirm_new:
                st.error("Passwords do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    supabase.auth.update_user({"password": new_password})
                    st.success("Password updated successfully!")
                except Exception as e:
                    st.error(f"Failed to update password: {str(e)}")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    
    if st.button("🚪 Log Out", use_container_width=True, key="logout_btn"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    render_bottom_nav()
