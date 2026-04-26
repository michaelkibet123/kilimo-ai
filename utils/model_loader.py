import streamlit as st
import gdown
import os
import json

@st.cache_resource
def load_kilimo_model():
    model_path = '/tmp/kilimo_ai_v1.h5'
    class_path = '/tmp/kilimo_class_indices.json'

    if not os.path.exists(model_path):
        with st.spinner('Loading Kilimo AI model...'):
            gdown.download(
                f"https://drive.google.com/uc?id={st.secrets['GOOGLE_DRIVE_MODEL_ID']}",
                model_path,
                quiet=False
            )

    if not os.path.exists(class_path):
        gdown.download(
            f"https://drive.google.com/uc?id={st.secrets['GOOGLE_DRIVE_CLASS_INDICES_ID']}",
            class_path,
            quiet=False
        )

    from tensorflow.keras.models import load_model
    model = load_model(model_path)

    with open(class_path, 'r') as f:
        class_indices = json.load(f)

    class_names = [class_indices[str(i)] for i in range(len(class_indices))]
    return model, class_names
