"""app.py — Streamlit entry point for AppLovin Gems V2"""
import streamlit as st

st.set_page_config(page_title="AppLovin Gems", page_icon="💎", layout="wide")

# ── White/Blue Design System CSS ──
st.markdown("""
<style>
    /* ── Font family ── */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }

    /* ── Main backgrounds: all white ── */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
    [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF !important;
    }

    /* ── Text color ── */
    .stApp p, .stApp span, .stApp label, .stApp div,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #111111 !important;
    }

    /* ── Sidebar: white with blue accents ── */
    section[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #111111 !important;
    }

    /* ── Sidebar radio: blue active pills ── */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 4px !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 10px 16px !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background-color: #EFF6FF !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] span,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p,
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
        color: #FFFFFF !important;
    }

    /* ── Expander styling ── */
    [data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        background-color: #FFFFFF !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #111111 !important;
    }

    /* ── Tabs styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 16px !important;
        color: #6B7280 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }

    /* ── Metric values ── */
    [data-testid="stMetricValue"] {
        color: #1E293B !important;
    }
    [data-testid="stMetricLabel"] {
        color: #6B7280 !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #F8FAFC; }
    ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

    /* ── Selectbox / multiselect ── */
    [data-testid="stSelectbox"], [data-testid="stMultiSelect"] {
        color: #111111 !important;
    }

    /* ── Card helper class ── */
    .gem-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        padding: 16px;
        margin-bottom: 12px;
    }

    /* ── Trade terminal box — override global dark-text rule ── */
    .stApp .trade-terminal,
    .stApp .trade-terminal div,
    .stApp .trade-terminal span,
    .stApp .trade-terminal p {
        color: #E0E0E0 !important;
    }
    .stApp .trade-terminal .tv-amber { color: #F59E0B !important; }
    .stApp .trade-terminal .tv-green { color: #4ADE80 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px 0;">
        <div style="font-size:28px;font-weight:800;color:#2563EB;letter-spacing:1px;">
            AppLovin Gems
        </div>
        <div style="font-size:11px;color:#6B7280;margin-top:2px;">
            Pattern-Matched Stock Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["The AppLovin Strategy", "50-Stock Scanner", "Options Engine", "Unusual Options Activity"],
        label_visibility="collapsed",
    )

# ── Page routing ──
from applovin_page import render_applovin_page
from scanner_page import render_scanner_page
from options_page import render_options_page
from unusual_activity_page import render_unusual_activity_page

if page == "The AppLovin Strategy":
    render_applovin_page()
elif page == "50-Stock Scanner":
    render_scanner_page()
elif page == "Options Engine":
    render_options_page()
else:
    render_unusual_activity_page()
