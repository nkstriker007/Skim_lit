import streamlit as st
import base64
import os

st.set_page_config(
    page_title="SkimLit",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_styles():
    image_path = "bg_img.jpg"

    if not os.path.exists(image_path):
        st.error(f"Background image not found: {image_path}")
        return

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>

    /* BACKGROUND */
    [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(rgba(5,10,25,0.75), rgba(5,10,25,0.75)),
            url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .stApp {{
        background: transparent;
    }}

    /* REMOVE HEADER BG */
    [data-testid="stHeader"],
    [data-testid="stToolbar"] {{
        background: transparent;
    }}

    /* MAIN CARD (GLASS DARK) */
    .main .block-container {{
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(18px);
        border-radius: 24px;
        padding: 2rem 2.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.08);
    }}

    /* TEXT = WHITE */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
        color: #e5e7eb !important;
    }}

    /* SIDEBAR (DEEP BLUE) */
    [data-testid="stSidebar"] {{
        background: rgba(2, 6, 23, 0.95);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }}


    /* REMOVE COLLAPSE BUTTON */
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* BUTTONS */
    div.stButton > button {{
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border-radius: 14px;
        border: none;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.35);
    }}

    div.stButton > button:hover {{
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
    }}
    [data-testid="stSidebar"] * {{
    color: inherit !important;
    }}
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    button[title="Close sidebar"],
    button[title="Open sidebar"] {{
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* Remove top spacing where button was */
    [data-testid="stHeader"] {{
        height: 0px !important;
    }}
    /* INPUTS */
    .stTextInput input,
    .stTextArea textarea {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
    }}

    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.25);
    }}

    /* TABS */
    [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: white !important;
    }}

    [data-baseweb="tab"][aria-selected="true"] {{
        background: rgba(59,130,246,0.2);
    }}
    .result-card,
    .result-card * {{
        color: #0f172 ;
    }}
    </style>
    """, unsafe_allow_html=True)