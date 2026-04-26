import streamlit as st

st.set_page_config(
    page_title="Kilimo AI",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

from main_app import main
main()
