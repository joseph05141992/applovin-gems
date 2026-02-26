"""app.py — Streamlit entry point for Monarch AI / AppLovin Gems"""
import streamlit as st

st.set_page_config(page_title="Monarch AI", page_icon="crown", layout="wide")

# ── Dark theme CSS injection ──
st.markdown("""
<style>
    /* Main backgrounds */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    section[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #0D0D0E !important;
        color: #E8E8E8 !important;
    }
    /* Text */
    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #E8E8E8 !important;
    }
    /* Radio buttons */
    [data-testid="stRadio"] label { color: #E8E8E8 !important; }
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0D0D0E; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px 0;">
        <div style="font-size:28px;font-weight:800;color:#C4A265;letter-spacing:1px;">
            Monarch AI
        </div>
        <div style="font-size:11px;color:#888;margin-top:2px;">
            AppLovin Gems Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["The AppLovin Strategy", "50-Stock Scanner", "Options Engine"],
        label_visibility="collapsed",
    )

# ── Page routing ──
from applovin_page import render_applovin_page
from scanner_page import render_scanner_page
from options_page import render_options_page

if page == "The AppLovin Strategy":
    render_applovin_page()
elif page == "50-Stock Scanner":
    render_scanner_page()
else:
    render_options_page()
