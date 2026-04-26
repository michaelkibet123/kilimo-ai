import streamlit as st
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

def render_scan():
    from PIL import Image
    import io
    import json
    from utils.model_loader import load_kilimo_model
    from utils.preprocessor import preprocess_image, get_severity, get_top3, format_disease_name
    from utils.gradcam import generate_gradcam, overlay_heatmap, pil_to_bytes
    from utils.advisory import get_advisory, save_scan_to_db, get_supabase
    from utils.scraper import get_latest_advisory
    
    render_header()

    st.markdown("### Select Crop")
    crops = ['Maize', 'Tomato', 'Potato', 'Pepper']
    
    if 'selected_crop' not in st.session_state:
        st.session_state['selected_crop'] = 'Maize'
    
    cols = st.columns(4)
    for i, crop in enumerate(crops):
        with cols[i]:
            selected = st.session_state['selected_crop'] == crop
            if st.button(
                crop,
                key=f"crop_{crop}",
                type="primary" if selected else "secondary",
                use_container_width=True
            ):
                st.session_state['selected_crop'] = crop
                st.session_state['scan_result'] = None
                st.session_state['uploaded_image'] = None
                st.rerun()

    st.markdown("### Upload Leaf Image")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="border: 2px dashed #1B4332; border-radius:12px; 
                    padding:1.5rem; text-align:center; cursor:pointer;">
            <div style="font-size:2rem;">☁️</div>
            <div style="font-size:0.85rem; color:#495057; margin-top:0.3rem;">Upload Photo</div>
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload", 
            type=['jpg', 'jpeg', 'png', 'webp'],
            label_visibility='collapsed',
            key="file_uploader"
        )
    
    with col2:
        st.markdown("""
        <div style="border: 2px dashed #1B4332; border-radius:12px;
                    padding:1.5rem; text-align:center; cursor:pointer;">
            <div style="font-size:2rem;">📷</div>
            <div style="font-size:0.85rem; color:#495057; margin-top:0.3rem;">Use Camera</div>
        </div>
        """, unsafe_allow_html=True)
        camera_image = st.camera_input("Camera", label_visibility='collapsed', key="camera_input")

    st.markdown("""
    <div style="background:#F8F9FA; border-radius:10px; padding:0.75rem; margin:0.5rem 0;">
        <div style="font-size:0.8rem; font-weight:600; color:#495057; margin-bottom:0.5rem;">
            📖 How to take a good photo
        </div>
        <div style="display:flex; gap:1rem; font-size:0.75rem; color:#6C757D;">
            <span>☀️ Natural light</span>
            <span>🎯 Focus on leaf</span>
            <span>🚫 Avoid blur</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    image_bytes = None
    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.session_state['uploaded_image'] = image_bytes
    elif camera_image:
        image_bytes = camera_image.getvalue()
        st.session_state['uploaded_image'] = image_bytes
    elif st.session_state.get('uploaded_image'):
        image_bytes = st.session_state['uploaded_image']

    if image_bytes:
        img = Image.open(io.BytesIO(image_bytes))
        st.image(img, use_column_width=True, caption="Uploaded leaf image")

        if st.button("🔬 Analyse Leaf", use_container_width=True, type="primary"):
            with st.spinner("Analysing your leaf..."):
                try:
                    model, class_names = load_kilimo_model()
                    img_array, pil_img = preprocess_image(image_bytes)
                    
                    crop_filter = st.session_state['selected_crop'].lower()
                    if crop_filter == 'maize':
                        crop_filter = 'corn'
                    
                    predictions = model.predict(img_array)
                    
                    top_idx = int(predictions[0].argmax())
                    top_confidence = float(predictions[0][top_idx])
                    top_class = class_names[top_idx]
                    
                    if not any(crop_filter in c.lower() for c in [top_class]):
                        valid_indices = [i for i, c in enumerate(class_names) if crop_filter in c.lower()]
                        if valid_indices:
                            valid_preds = [(i, float(predictions[0][i])) for i in valid_indices]
                            top_idx, top_confidence = max(valid_preds, key=lambda x: x[1])
                            top_class = class_names[top_idx]
                    
                    crop_name, disease_name = format_disease_name(top_class)
                    severity, severity_color = get_severity(top_confidence)
                    top3 = get_top3(predictions, class_names)
                    
                    heatmap = generate_gradcam(model, img_array, top_idx)
                    overlay = overlay_heatmap(pil_img, heatmap)
                    
                    advisory = get_advisory(top_class)
                    
                    st.session_state['scan_result'] = {
                        'crop': crop_name,
                        'disease': disease_name,
                        'raw_class': top_class,
                        'confidence': top_confidence,
                        'severity': severity,
                        'severity_color': severity_color,
                        'top3': top3,
                        'advisory': advisory,
                        'original_bytes': image_bytes,
                        'heatmap_bytes': pil_to_bytes(overlay),
                        'heatmap_only_bytes': pil_to_bytes(Image.fromarray(heatmap))
                    }
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

    if st.session_state.get('scan_result'):
        result = st.session_state['scan_result']
        render_results(result)

    render_bottom_nav()

def render_results(result):
    st.markdown("---")
    st.markdown("## Scan Result")

    col1, col2 = st.columns(2)
    with col1:
        st.image(result['original_bytes'], caption="Original", use_column_width=True)
    with col2:
        st.image(result['heatmap_bytes'], caption="Disease Hotspots", use_column_width=True)

    severity_color = result['severity_color']
    confidence_pct = int(result['confidence'] * 100)
    
    st.markdown(f"""
    <div style="border-left: 4px solid {severity_color}; background:white; 
                border-radius:0 12px 12px 0; padding:1rem; margin:1rem 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-size:0.8rem; color:#6C757D;">{result['crop']}</div>
        <div style="font-size:1.4rem; font-weight:700; color:#212529;">{result['disease']}</div>
        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.5rem;">
            <div style="font-size:1.8rem; font-weight:700; color:{severity_color};">{confidence_pct}%</div>
            <div style="background:{severity_color}20; color:{severity_color}; 
                        padding:0.2rem 0.6rem; border-radius:20px; font-size:0.75rem; font-weight:600;">
                {result['severity']}
            </div>
        </div>
        <div style="font-size:0.8rem; color:#6C757D; margin-top:0.3rem;">Confidence Score</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📊 View full confidence breakdown"):
        for item in result['top3']:
            _, disease = format_disease_name(item['class'])
            pct = item['confidence']
            color = '#1B4332' if pct == result['confidence'] else '#6C757D'
            st.markdown(f"""
            <div style="margin:0.5rem 0;">
                <div style="display:flex; justify-content:space-between; 
                            font-size:0.8rem; margin-bottom:0.2rem;">
                    <span>{disease}</span>
                    <span style="font-weight:600; color:{color};">{int(pct*100)}%</span>
                </div>
                <div style="background:#F0F0F0; border-radius:4px; height:6px;">
                    <div style="background:{color}; width:{int(pct*100)}%; 
                                height:6px; border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if result['confidence'] < 0.70:
        st.markdown("""
        <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:12px; 
                    padding:1rem; margin:0.5rem 0; display:flex; align-items:center; gap:0.5rem;">
            <span style="font-size:1.2rem;">⚠️</span>
            <span style="font-size:0.85rem; color:#92400E;">
                Low confidence result — we recommend consulting an expert.
            </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏪 Find Nearest Vet", key="find_vet"):
            st.session_state['page'] = 'vets'
            st.rerun()

    advisory = result['advisory']
    
    st.markdown("### About this Disease")
    st.markdown(f"""
    <div style="background:#F8F9FA; border-radius:10px; padding:1rem; 
                font-size:0.85rem; color:#495057; line-height:1.6;">
        {advisory.get('description', 'No description available.')}
    </div>
    """, unsafe_allow_html=True)

    if st.button("🌐 Get Latest Info from Web", key="scrape_btn"):
        with st.spinner("Fetching latest advisory..."):
            scraped, success = get_latest_advisory(result['raw_class'])
            if success and scraped:
                st.success("Latest advisory loaded!")
                st.info(scraped)
            else:
                st.info("No newer information found. Showing database advisory.")

    st.markdown("### Treatment Plan")
    tab1, tab2, tab3 = st.tabs(["⚡ Immediate Action", "💊 Treatment", "🛡️ Prevention"])
    
    with tab1:
        st.markdown(f"""
        <div style="padding:0.5rem 0; font-size:0.85rem; color:#495057; line-height:1.6;">
            {advisory.get('immediate_action', 'No data available.')}
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown(f"""
        <div style="padding:0.5rem 0; font-size:0.85rem; color:#495057; line-height:1.6;">
            {advisory.get('treatment', 'No data available.')}
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown(f"""
        <div style="padding:0.5rem 0; font-size:0.85rem; color:#495057; line-height:1.6;">
            {advisory.get('prevention', 'No data available.')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Save & Download")
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download Heatmap",
            data=result['heatmap_bytes'],
            file_name=f"kilimo_ai_{result['disease'].replace(' ', '_')}_heatmap.png",
            mime="image/png",
            use_container_width=True
        )
    
    with col2:
        pdf_bytes = generate_pdf_report(result)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"kilimo_ai_{result['disease'].replace(' ', '_')}_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    if st.session_state.get('authenticated'):
        if st.button("💾 Save Scan", use_container_width=True, type="primary", key="save_scan"):
            user_id = st.session_state['user'].get('id')
            success = save_scan_to_db(
                user_id=user_id,
                crop=result['crop'],
                disease=result['disease'],
                confidence=result['confidence'],
                top3=result['top3'],
                image_url='',
                heatmap_url='',
                treatment=result['advisory']
            )
            if success:
                st.success("Scan saved to your history!")
            else:
                st.error("Failed to save scan. Please try again.")
    else:
        st.markdown("""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px;
                    padding:1rem; text-align:center; margin:0.5rem 0;">
            <div style="font-size:0.85rem; color:#166534; font-weight:600;">
                Create a free account to save your scan history
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create Free Account", use_container_width=True, key="guest_signup"):
            st.session_state['guest'] = False
            st.session_state['show_landing'] = False
            st.session_state['auth_mode'] = 'signup'
            st.rerun()

    if st.button("🔄 Scan Again", use_container_width=True, key="scan_again"):
        st.session_state['scan_result'] = None
        st.session_state['uploaded_image'] = None
        st.rerun()

def generate_pdf_report(result):
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(27, 67, 50)
        pdf.cell(0, 10, 'Kilimo AI - Scan Report', ln=True, align='C')
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(108, 117, 125)
        
        from datetime import datetime
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_draw_color(27, 67, 50)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(33, 37, 41)
        pdf.cell(0, 10, 'Diagnosis', ln=True)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(40, 8, 'Crop:', ln=False)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, result['crop'], ln=True)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(40, 8, 'Disease:', ln=False)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, result['disease'], ln=True)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(40, 8, 'Confidence:', ln=False)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, f"{int(result['confidence']*100)}%", ln=True)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(40, 8, 'Severity:', ln=False)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, result['severity'], ln=True)
        pdf.ln(5)
        
        advisory = result['advisory']
        sections = [
            ('About this Disease', 'description'),
            ('Immediate Action', 'immediate_action'),
            ('Treatment', 'treatment'),
            ('Prevention', 'prevention')
        ]
        
        for title, key in sections:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(27, 67, 50)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(73, 80, 87)
            content = advisory.get(key, 'No data available.')
            pdf.multi_cell(0, 6, content)
            pdf.ln(3)
        
        pdf.set_font('Helvetica', 'I', 8)
        pdf.set_text_color(108, 117, 125)
        pdf.cell(0, 8, 'Kilimo AI - AI-powered crop disease diagnosis for Kenyan farmers', ln=True, align='C')
        
        return bytes(pdf.output())
    except ImportError:
        return b"PDF generation requires fpdf2. Please install it."
    except Exception as e:
        return f"PDF generation failed: {str(e)}".encode()
