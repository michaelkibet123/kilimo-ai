import streamlit as st
import json

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
            key="nav_"+p+"_scan",
            use_container_width=True
        )
        if clicked:
            st.session_state["page"] = p
            st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)


def generate_pdf_report(result):
    try:
        from fpdf import FPDF
        from datetime import datetime
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica","B",20)
        pdf.cell(0,10,"Kilimo AI - Scan Report",ln=True,align="C")
        pdf.set_font("Helvetica","",10)
        pdf.cell(0,8,"Generated: "+datetime.now().strftime("%B %d, %Y"),ln=True,align="C")
        pdf.ln(5)
        pdf.set_font("Helvetica","B",14)
        pdf.cell(0,10,"Diagnosis",ln=True)
        pdf.set_font("Helvetica","",11)
        for label,key in [("Crop","crop"),("Disease","disease"),("Confidence","confidence"),("Severity","severity")]:
            val = result.get(key,"")
            if key == "confidence": val = str(int(float(val)*100))+"%"
            pdf.cell(40,8,label+":",ln=False)
            pdf.set_font("Helvetica","B",11)
            pdf.cell(0,8,str(val),ln=True)
            pdf.set_font("Helvetica","",11)
        advisory = result.get("advisory",{})
        if isinstance(advisory,str):
            advisory = json.loads(advisory)
        pdf.ln(3)
        for title,key in [("About this Disease","description"),("Immediate Action","immediate_action"),("Treatment","treatment"),("Prevention","prevention")]:
            pdf.set_font("Helvetica","B",12)
            pdf.cell(0,10,title,ln=True)
            pdf.set_font("Helvetica","",10)
            pdf.multi_cell(0,6,str(advisory.get(key,"No data.")))
            pdf.ln(3)
        pdf.set_font("Helvetica","I",8)
        pdf.cell(0,8,"Kilimo AI - AI-powered crop disease diagnosis for Kenyan farmers",ln=True,align="C")
        return bytes(pdf.output())
    except Exception as e:
        return ("PDF error: "+str(e)).encode()

def render_scan():
    from PIL import Image
    import io
    from utils.model_loader import load_kilimo_model
    from utils.preprocessor import preprocess_image, get_severity, get_top3, format_disease_name
    from utils.gradcam import generate_gradcam, overlay_heatmap, pil_to_bytes
    from utils.advisory import get_advisory, save_scan_to_db

    dark = st.session_state.get("dark_mode",False)
    text = "#F5F5F5" if dark else "#1A1A1A"
    muted = "#9CA3AF"
    card = "#242424" if dark else "#FFFFFF"
    border = "#333333" if dark else "#E5E7EB"
    bg = "#1A1A1A" if dark else "#EEF2EE"

    render_header()

    st.markdown("<div style='padding:14px 16px 8px;font-family:DM Serif Display,serif;font-size:1.3rem;color:"+text+";'>Scan Plant</div>", unsafe_allow_html=True)

    crops = ["Maize","Tomato","Potato","Pepper"]
    if "selected_crop" not in st.session_state:
        st.session_state["selected_crop"] = "Maize"

    st.markdown("<div style='padding:0 12px 8px;font-size:0.8rem;font-weight:600;color:"+muted+";'>SELECT CROP</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i,crop in enumerate(crops):
        with cols[i]:
            selected = st.session_state["selected_crop"] == crop
            if st.button(crop, key="crop_"+crop, type="primary" if selected else "secondary", use_container_width=True):
                st.session_state["selected_crop"] = crop
                st.session_state["scan_result"] = None
                st.session_state["uploaded_image"] = None
                st.session_state["original_bytes"] = None
                st.session_state["heatmap_bytes"] = None
                st.rerun()

    if not st.session_state.get("scan_result"):
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown(
                "<div class='kupload-btn' style='background:"+card+";border-color:#52B788;'>"
                "<div class='kupload-icon'>📁</div>"
                "<div style='font-weight:600;font-size:0.88rem;color:"+text+";'>Upload from Gallery</div>"
                "<div style='font-size:0.72rem;color:"+muted+";margin-top:3px;'>JPG, PNG, WEBP</div>"
                "</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload", type=["jpg","jpeg","png","webp"], label_visibility="collapsed", key="file_uploader")
        with c2:
            st.markdown(
                "<div class='kupload-btn' style='background:"+card+";border-color:#52B788;'>"
                "<div class='kupload-icon'>📷</div>"
                "<div style='font-weight:600;font-size:0.88rem;color:"+text+";'>Take a Photo</div>"
                "<div style='font-size:0.72rem;color:"+muted+";margin-top:3px;'>Use camera</div>"
                "</div>", unsafe_allow_html=True)
            camera_image = st.camera_input("Camera", label_visibility="collapsed", key="camera_input")

        st.markdown(
            "<div style='background:"+card+";border-radius:12px;padding:14px;margin:8px 12px;border:1px solid "+border+";'>"
            "<div style='font-size:0.78rem;font-weight:600;color:"+muted+";margin-bottom:8px;'>HOW TO GET BEST RESULTS</div>"
            "<div style='display:flex;gap:16px;'>"
            "<div style='flex:1;text-align:center;font-size:0.72rem;color:"+muted+";'><div style='font-size:1.1rem;margin-bottom:3px;'>☀️</div>Natural light</div>"
            "<div style='flex:1;text-align:center;font-size:0.72rem;color:"+muted+";'><div style='font-size:1.1rem;margin-bottom:3px;'>🎯</div>Focus on leaf</div>"
            "<div style='flex:1;text-align:center;font-size:0.72rem;color:"+muted+";'><div style='font-size:1.1rem;margin-bottom:3px;'>🚫</div>Avoid blur</div>"
            "</div></div>", unsafe_allow_html=True)

        image_bytes = None
        if uploaded_file:
            image_bytes = uploaded_file.read()
            st.session_state["uploaded_image"] = image_bytes
        elif camera_image:
            image_bytes = camera_image.getvalue()
            st.session_state["uploaded_image"] = image_bytes
        elif st.session_state.get("uploaded_image"):
            image_bytes = st.session_state["uploaded_image"]

        if image_bytes:
            img = Image.open(io.BytesIO(image_bytes))
            st.image(img, use_container_width=True, caption="Uploaded leaf")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("🔬 Analyse Leaf", use_container_width=True, type="primary"):
                with st.spinner("Analysing your leaf..."):
                    try:
                        model, class_names = load_kilimo_model()
                        img_array, pil_img = preprocess_image(image_bytes)
                        crop_filter = st.session_state["selected_crop"].lower()
                        if crop_filter == "maize": crop_filter = "corn"
                        predictions = model.predict(img_array)
                        top_idx = int(predictions[0].argmax())
                        top_confidence = float(predictions[0][top_idx])
                        top_class = class_names[top_idx]
                        if not any(crop_filter in c.lower() for c in [top_class]):
                            valid_indices = [i for i,c in enumerate(class_names) if crop_filter in c.lower()]
                            if valid_indices:
                                valid_preds = [(i,float(predictions[0][i])) for i in valid_indices]
                                top_idx, top_confidence = max(valid_preds, key=lambda x: x[1])
                                top_class = class_names[top_idx]
                        crop_name, disease_name = format_disease_name(top_class)
                        severity, severity_color = get_severity(top_confidence)
                        top3 = get_top3(predictions, class_names)
                        heatmap = generate_gradcam(model, img_array, top_idx)
                        overlay = overlay_heatmap(pil_img, heatmap)
                        advisory = get_advisory(top_class)
                        st.session_state["original_bytes"] = image_bytes
                        st.session_state["heatmap_bytes"] = pil_to_bytes(overlay)
                        st.session_state["scan_result"] = {
                            "crop": crop_name,
                            "disease": disease_name,
                            "raw_class": top_class,
                            "confidence": top_confidence,
                            "severity": severity,
                            "severity_color": severity_color,
                            "top3": top3,
                            "advisory": advisory
                        }
                    except Exception as e:
                        st.error("Analysis failed: "+str(e))

    if st.session_state.get("scan_result"):
        render_results(st.session_state["scan_result"], dark, text, muted, card, border)

    render_bottom_nav()

def render_results(result, dark, text, muted, card, border):
    from utils.preprocessor import format_disease_name
    import json

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    orig = st.session_state.get("original_bytes")
    heat = st.session_state.get("heatmap_bytes")
    if orig and heat:
        c1,c2 = st.columns(2)
        with c1: st.image(orig, caption="Original", use_container_width=True)
        with c2: st.image(heat, caption="Disease Hotspots", use_container_width=True)

    conf = result.get("confidence",0)
    confidence_pct = int(conf*100)
    severity = result.get("severity","")
    severity_color = result.get("severity_color","#1B4332")
    crop = result.get("crop","")
    disease = result.get("disease","")
    badge_class = "bsevere" if conf>=0.85 else "bmoderate" if conf>=0.60 else "bhealthy"

    st.markdown(
        "<div class='kcard' style='background:"+card+";border:1px solid "+border+";margin:8px 12px;'>"
        "<div style='font-size:0.75rem;color:"+muted+";font-weight:500;'>"+crop.upper()+"</div>"
        "<div class='kdisease' style='color:"+text+";'>"+disease+"</div>"
        "<div style='display:flex;align-items:center;gap:10px;margin-top:8px;'>"
        "<div style='font-family:DM Serif Display,serif;font-size:2.2rem;color:"+severity_color+";line-height:1;'>"+str(confidence_pct)+"%</div>"
        "<span class='"+badge_class+"'>"+severity+"</span>"
        "</div>"
        "<div style='background:#F3F4F6;border-radius:6px;height:6px;margin-top:8px;overflow:hidden;'>"
        "<div style='background:"+severity_color+";width:"+str(confidence_pct)+"%;height:6px;border-radius:6px;'></div>"
        "</div>"
        "</div>", unsafe_allow_html=True)

    if conf < 0.70:
        st.markdown(
            "<div style='background:#FFFBEB;border-left:3px solid #F59E0B;border-radius:10px;padding:10px 14px;margin:6px 12px;'>"
            "<div style='font-size:0.82rem;color:#92400E;'>⚠️ Low confidence — we recommend consulting an expert.</div>"
            "</div>", unsafe_allow_html=True)
        if st.button("Find Nearest Vet", key="find_vet"):
            st.session_state["page"] = "vets"
            st.rerun()

    advisory = result.get("advisory",{})
    if isinstance(advisory,str):
        try: advisory = json.loads(advisory)
        except: advisory = {}

    st.markdown(
        "<div class='kcard' style='background:"+card+";border:1px solid "+border+";margin:8px 12px;'>"
        "<div style='font-size:0.78rem;font-weight:600;color:"+muted+";margin-bottom:6px;'>ABOUT THIS DISEASE</div>"
        "<div style='font-size:0.85rem;color:"+text+";line-height:1.6;'>"+advisory.get("description","No description available.")+"</div>"
        "</div>", unsafe_allow_html=True)

    if st.button("🌐 Get Latest Info from Web", use_container_width=True, key="scrape_btn"):
        from utils.scraper import get_latest_advisory
        with st.spinner("Fetching latest advisory..."):
            scraped, success = get_latest_advisory(result.get("raw_class",""))
            if success and scraped:
                st.success("Latest advisory loaded!")
                st.info(scraped)
            else:
                st.info("Showing database advisory — web data unavailable.")

    top3 = result.get("top3") or []
    if isinstance(top3,str):
        try: top3 = json.loads(top3)
        except: top3 = []

    with st.expander("📊 Full confidence breakdown"):
        for item in top3:
            try:
                _,d = format_disease_name(item["class"])
                pct = float(item["confidence"])
                st.markdown(
                    "<div style='margin:6px 0;'>"
                    "<div style='display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:3px;'>"
                    "<span style='color:"+text+";'>"+d+"</span>"
                    "<span style='font-weight:600;color:#1B4332;'>"+str(int(pct*100))+"%</span>"
                    "</div>"
                    "<div style='background:#F3F4F6;border-radius:4px;height:5px;overflow:hidden;'>"
                    "<div style='background:#1B4332;width:"+str(int(pct*100))+"%;height:5px;border-radius:4px;'></div>"
                    "</div></div>", unsafe_allow_html=True)
            except: pass

    st.markdown("<div style='padding:4px 12px 6px;font-weight:600;font-size:0.85rem;color:"+muted+";'>TREATMENT PLAN</div>", unsafe_allow_html=True)
    tab1,tab2,tab3 = st.tabs(["⚡ Immediate Action","💊 Treatment","🛡️ Prevention"])
    with tab1:
        st.markdown("<div style='padding:6px 0;font-size:0.85rem;color:"+text+";line-height:1.6;'>"+advisory.get("immediate_action","No data.")+"</div>", unsafe_allow_html=True)
    with tab2:
        st.markdown("<div style='padding:6px 0;font-size:0.85rem;color:"+text+";line-height:1.6;'>"+advisory.get("treatment","No data.")+"</div>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<div style='padding:6px 0;font-size:0.85rem;color:"+text+";line-height:1.6;'>"+advisory.get("prevention","No data.")+"</div>", unsafe_allow_html=True)

    st.markdown("<div style='padding:4px 12px 6px;font-weight:600;font-size:0.85rem;color:"+muted+";'>DOWNLOAD</div>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        if heat:
            st.download_button("📥 Heatmap", data=heat,
                file_name="kilimo_"+disease.replace(" ","_")+"_heatmap.png",
                mime="image/png", use_container_width=True)
    with c2:
        pdf = generate_pdf_report(result)
        st.download_button("📄 PDF Report", data=pdf,
            file_name="kilimo_"+disease.replace(" ","_")+"_report.pdf",
            mime="application/pdf", use_container_width=True)

    if st.session_state.get("authenticated"):
        if st.button("💾 Save Scan", use_container_width=True, type="primary", key="save_scan"):
            from utils.advisory import save_scan_to_db
            user_id = st.session_state["user"].get("id")
            ok = save_scan_to_db(user_id=user_id, crop=crop, disease=disease,
                confidence=conf, top3=top3, image_url="", heatmap_url="", treatment=advisory)
            if ok: st.success("Scan saved!")
            else: st.error("Failed to save scan.")
    else:
        st.markdown(
            "<div style='background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:12px;text-align:center;margin:6px 12px;'>"
            "<div style='font-size:0.82rem;color:#166534;font-weight:600;'>Create a free account to save your scan history</div>"
            "</div>", unsafe_allow_html=True)
        if st.button("Create Free Account", use_container_width=True, key="guest_signup"):
            st.session_state["guest"] = False
            st.session_state["show_landing"] = False
            st.session_state["auth_mode"] = "signup"
            st.rerun()

    if st.button("🔄 Scan Again", use_container_width=True, key="scan_again"):
        st.session_state["scan_result"] = None
        st.session_state["uploaded_image"] = None
        st.session_state["original_bytes"] = None
        st.session_state["heatmap_bytes"] = None
        st.rerun()
