import time
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------- COLORS -------------------------
BG_MAIN = "#2e3a47"      # background για όλες τις σελίδες + header bar
BG_SIDEBAR = "#384655"   # sidebar
CARD_COLOR = "#3f4a5b"   # χρώμα από την εικόνα (header card + φίλτρα)
TEXT_LIGHT = "#f8fafc"

# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --------- Page config ----------
st.set_page_config(
    page_title="AncientVision – Dashboard",
    layout="wide",
    page_icon="🏺"
)

# --------- GLOBAL STYLE ----------
st.markdown(
    f"""
    <style>
    /* GLOBAL BACKGROUND */
    .stApp {{
        background-color: {BG_MAIN} !important;
        background: {BG_MAIN} !important;
        color: {TEXT_LIGHT} !important;
    }}
    html, body {{
        background-color: {BG_MAIN} !important;
    }}
    .main {{
        background-color: {BG_MAIN} !important;
        color: {TEXT_LIGHT} !important;
    }}

    /* HEADER BAR */
    div[data-testid="stToolbar"] {{
        background-color: {BG_MAIN} !important;
        color: {TEXT_LIGHT} !important;
        border: none !important;
    }}

    /* SIDEBAR BACKGROUND */
    section[data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
    }}

    .block-container {{
        background-color: transparent !important;
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
    }}

    /* HEADER CARD */
    .header-card {{
        background-color: {CARD_COLOR} !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 0.8rem;
        padding: 1.4rem;
        margin-top: 3rem;  /* πιο κάτω για να μην ακουμπάει το header bar */
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.35);
    }}

    /* KPI ROW */
    .kpi-row {{
        display:flex;
        gap:1rem;
        margin-bottom:1rem;
    }}
    .kpi-card {{
        flex:1;
        padding:1rem;
        border-radius:0.6rem;
        color:#fff;
        font-weight:600;
        box-shadow:0 2px 6px rgba(0,0,0,0.22);
    }}

    /* ΦΙΛΤΡΑ SIDEBAR ΜΕ CARD_COLOR */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="number"],
    section[data-testid="stSidebar"] textarea {{
        background-color: {CARD_COLOR} !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 0.4rem !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: {CARD_COLOR} !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 0.4rem !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }}

    section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
        background-color: rgba(255,255,255,0.16) !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 0.4rem !important;
    }}

    /* Μικρότερο font στο header Φίλτρα */
    section[data-testid="stSidebar"] h1 {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }}

    /* Κρύψιμο footer */
    footer {{visibility: hidden !important;}}
    </style>
    """,
    unsafe_allow_html=True
)

# --------- ΛΕΥΚΑ ΓΡΑΜΜΑΤΑ ΠΑΝΤΟΥ (εκτός inputs) ----------
st.markdown(
    f"""
    <style>
    h1, h2, h3, h4, h5, h6,
    p, span, div, label {{
        color: {TEXT_LIGHT} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {TEXT_LIGHT} !important;
    }}

    ::placeholder {{
        color: rgba(255,255,255,0.6) !important;
    }}

    /* Inputs παραμένουν readable */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {{
        color: black !important;
        background-color: white !important;
    }}

    .stAlert p {{
        color: black !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------- ΑΛΛΑΓΗ ΟΝΟΜΑΤΩΝ ΣΤΟ SIDEBAR NAV (app → Dashboard, Table → Findings) ----------
st.markdown(
    """
    <style>
    /* Πιάνουμε τα στοιχεία του navigation στο sidebar */
    div[data-testid="stSidebarNav"] li:nth-child(1) a span {{
        font-size: 0px !important;
    }}
    div[data-testid="stSidebarNav"] li:nth-child(1) a span:after {{
        content: "Dashboard";
        font-size: 1rem !important;
        color: #f8fafc !important;
    }}

    /* 2ο στοιχείο είναι "New Finding" – το αφήνουμε ίδιο */

    /* 3ο στοιχείο: Table and Small Map -> Findings */
    div[data-testid="stSidebarNav"] li:nth-child(3) a span {{
        font-size: 0px !important;
    }}
    div[data-testid="stSidebarNav"] li:nth-child(3) a span:after {{
        content: "Findings";
        font-size: 1rem !important;
        color: #f8fafc !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------- Splash Screen ----------
if "splash_done" not in st.session_state:
    st.markdown(
        f"""
        <style>
        .splash-box {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: {TEXT_LIGHT};
        }}
        .splash-title {{
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }}
        .splash-subtitle {{
            font-size: 1rem;
            opacity: 0.85;
            max-width: 480px;
        }}
        </style>

        <div class="splash-box">
            <div class="splash-title">AncientVision</div>
            <div class="splash-subtitle">Φόρτωση του συστήματος...</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress.progress(i + 1)

    st.session_state["splash_done"] = True
    st.rerun()

# --------- Φόρτωση δεδομένων ----------
@st.cache_data
def load_findings():
    docs = (
        db.collection("findings")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .stream()
    )
    data = []
    for doc in docs:
        d = doc.to_dict()
        data.append({
            "id": doc.id,
            "coin_name": d.get("coin_name", ""),
            "type": d.get("type", ""),
            "period": d.get("period", ""),
            "site_name": d.get("site_name", ""),
            "latitude": d.get("latitude", None),
            "longitude": d.get("longitude", None),
            "image_bytes": d.get("image_bytes", None),
            "image_url": d.get("image_url", ""),
            "notes": d.get("notes", ""),
            "timestamp": d.get("timestamp", "")
        })
    return pd.DataFrame(data)

findings = load_findings()

# --------- Sidebar Filters ----------
st.sidebar.header("Φίλτρα")   # χωρίς 🔍

selected_types = st.sidebar.multiselect(
    "Τύπος ευρήματος",
    ["coin", "sherd", "other"],
    default=["coin", "sherd", "other"]
)

periods = (
    sorted(findings["period"].dropna().unique().tolist())
    if not findings.empty else []
)

selected_periods = st.sidebar.multiselect(
    "Περίοδος",
    periods,
    default=periods
)

filtered = findings.copy()
if selected_types:
    filtered = filtered[filtered["type"].isin(selected_types)]
if selected_periods:
    filtered = filtered[filtered["period"].isin(selected_periods)]

# --------- HEADER CARD ----------
st.markdown(
    f"""
    <div class="header-card">
        <div style="font-size:0.8rem; text-transform:uppercase; opacity:0.85;">
            ROBOTICALIENZ'S INNOVATION PROJECT
        </div>
        <div style="font-size:2.1rem; font-weight:700; margin-top:0.3rem; margin-bottom:0.3rem;">
            AncientVision – Archaeology Dashboard
        </div>
        <div style="font-size:1rem; opacity:0.9;">
            Ψηφιακό εργαλείο για αναγνώριση, καταγραφή & ανάλυση αρχαιολογικών ευρημάτων.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------- KPI CARDS ----------
total = len(filtered)
sites = filtered["site_name"].nunique() if not filtered.empty else 0
periods_count = filtered["period"].nunique() if not filtered.empty else 0

st.markdown(
    f"""
    <div class="kpi-row">
        <div class="kpi-card" style="background:#007bff;">
            Σύνολο ευρημάτων<br><span style="font-size:1.6rem;">{total}</span>
        </div>
        <div class="kpi-card" style="background:#17a2b8;">
            Αρχαιολογικοί χώροι<br><span style="font-size:1.6rem;">{sites}</span>
        </div>
        <div class="kpi-card" style="background:#fd7e14;">
            Διαφορετικές περίοδοι<br><span style="font-size:1.6rem;">{periods_count}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------- GALLERY ----------
st.markdown("### 📸 Πρόσφατα ευρήματα")

if not filtered.empty:
    rows = filtered.sort_values("timestamp", ascending=False)
    rows = rows[
        rows["image_bytes"].notnull() |
        (rows["image_url"].astype(str) != "")
    ]

    if rows.empty:
        st.info("Δεν υπάρχουν φωτογραφίες ακόμη.")
    else:
        cols = st.columns(4)
        for idx, (_, row) in enumerate(rows.head(8).iterrows()):
            col = cols[idx % 4]
            img = row["image_bytes"] if row["image_bytes"] not in [None, b""] else row["image_url"]
            col.image(img, caption=row["coin_name"], use_column_width=True)
else:
    st.info("Δεν υπάρχουν ευρήματα ακόμη.")
