import streamlit as st
import requests
import json
import os
from styles import apply_styles
API_URL = os.getenv("API_URL", "http://backend:8000")
   # docker-compose service name; change to Render URL after deploy
st.set_page_config(page_title="SkimLit", page_icon="🔬", layout="wide")

apply_styles()
LABEL_COLORS = {
    "BACKGROUND":  "rgba(191, 219, 254, 0.85)",
    "OBJECTIVE":   "rgba(187, 247, 208, 0.85)",
    "METHODS":     "rgba(254, 240, 138, 0.85)",
    "RESULTS":     "rgba(254, 202, 202, 0.85)",
    "CONCLUSIONS": "rgba(221, 214, 254, 0.85)",
}


EXAMPLE_ABSTRACT = (
    "This study investigates the effect of low-dose aspirin on cardiovascular outcomes. "
    "We conducted a randomized controlled trial with 1,200 participants over 24 months. "
    "Participants were assigned to receive either aspirin or placebo daily. "
    "Results showed a 22% reduction in major cardiovascular events in the aspirin group. "
    "These findings suggest that low-dose aspirin remains effective in high-risk populations."
)

# ── Session state ─────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "page" not in st.session_state:
    st.session_state.page = "classify"


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔬 SkimLit")
    st.caption("Biomedical Abstract Classifier")
    st.divider()

    if st.session_state.token:
        st.success("Logged in")
        if st.button("Classify", use_container_width=True):
            st.session_state.page = "classify"
        if st.button("History", use_container_width=True):
            st.session_state.page = "history"
        if st.button("Analytics", use_container_width=True):
            st.session_state.page = "analytics"
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.page = "classify"
            st.rerun()
    else:
        st.info("Login to classify abstracts and save results.")

    st.divider()
    st.markdown("**Label guide**")
    for label, color in LABEL_COLORS.items():
        st.markdown(
        f'''
        <div style="
            background:{color};
            color:#0f172a !important;
            padding:4px 10px;
            border-radius:6px;
            font-size:0.8em;
            font-weight:700;
            display:inline-block;
            margin-bottom:8px;
        ">{label}</div>
        ''',
        unsafe_allow_html=True
        )
        


# ── Auth page ─────────────────────────────────────────────────────────────────
if not st.session_state.token:
    st.title("Welcome to SkimLit")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            r = requests.post(f"{API_URL}/auth/login",
                              data={"username": email, "password": password})
            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab_register:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register", type="primary"):
            r = requests.post(f"{API_URL}/auth/register",
                              json={"email": email, "password": password})
            if r.status_code == 201:
                st.success("Account created! Please login.")
            else:
                st.error(r.json().get("detail", "Registration failed"))

    st.stop()


# ── Classify page ─────────────────────────────────────────────────────────────
if st.session_state.page == "classify":
    st.title("Classify Abstract")
    abstract = st.text_area("Paste your abstract below",
                             value=EXAMPLE_ABSTRACT, height=200)
    col1, col2 = st.columns([1, 5])
    with col1:
        classify_btn = st.button("Classify", type="primary")
    with col2:
        if st.button("Load example"):
            st.rerun()

    if classify_btn and abstract.strip():
        with st.spinner("Classifying..."):
            r = requests.post(f"{API_URL}/predict",
                              json={"abstract": abstract},
                              headers=auth_headers())
        if r.status_code == 200:
            sentences = r.json()["sentences"]
            st.markdown("### Results")
            for item in sentences:
                label = item["label"]
                conf = item["confidence"]
                color = LABEL_COLORS.get(label, "#EAECEE")
                st.markdown(
                f'''
                <div class="result-card" style="background:{color}; color:#0f172a; padding:10px 14px; border-radius:8px; margin:5px 0; line-height:1.6;">
                <b>{label}</b> <span style="opacity:0.7; font-size:0.85em;">({conf:.0%})</span><br>{item["sentence"]}.</div>''',unsafe_allow_html=True)
        elif r.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.token = None
            st.rerun()
        else:
            st.error("Classification failed. Is the backend running?")


# ── History page ──────────────────────────────────────────────────────────────
elif st.session_state.page == "history":
    st.title("Your Classification History")
    r = requests.get(f"{API_URL}/history", headers=auth_headers())
    if r.status_code == 200:
        history = r.json()
        if not history:
            st.info("No classifications yet. Go classify an abstract!")
        for item in history:
            with st.expander(f"{item['created_at'][:19]}  —  {item['abstract'][:80]}..."):
                results = json.loads(item["results"])
                for s in results:
                    color = LABEL_COLORS.get(s["label"], "#EAECEE")
                    st.markdown(
                        f'''
                        <div class="result-card" style="background:{color}; color:#0f172a; padding:8px 12px; border-radius:6px; margin:3px 0;">
                        <b>{s["label"]}</b> ({s["confidence"]:.0%}) — {s["sentence"]}.</div>''',unsafe_allow_html=True)
    else:
        st.error("Failed to load history.")


# ── Analytics page ────────────────────────────────────────────────────────────
elif st.session_state.page == "analytics":
    st.title("Your Usage Analytics")
    r = requests.get(f"{API_URL}/analytics/usage", headers=auth_headers())
    if r.status_code == 200:
        data = r.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Abstracts", data["total_predictions"])
        col2.metric("Sentences Classified", data["total_sentences_classified"])
        col3.metric("Requests (7 days)", data["requests_last_7_days"])

        st.markdown("### Label Distribution")
        if data["label_distribution"]:
            import pandas as pd
            df = pd.DataFrame(data["label_distribution"])
            st.bar_chart(df.set_index("label")["count"])
        else:
            st.info("Classify some abstracts to see your label distribution.")
    else:
        st.error("Failed to load analytics.")
