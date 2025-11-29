import time
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------- COLORS -------------------------
BG_MAIN = "#384655"      # background for all pages + header bar
BG_SIDEBAR = "#2e3a47"   # sidebar background color
TEXT_LIGHT = "#f8fafc"


# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()


# --------- Page config ----------
st.set_page_config(
    page_title="AncientVisionFLL – Dashboard",
    layout="wide",
    page_icon="🏺"
)


# --------- GLOBAL STYLE ----------
st.markdown(
    f"""
    <style>

    /* ---------- GLOBAL BACKGROUND ---------- */
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
    }}

    /* ---------- HEADER BAR (top menu) ---------- */
    div[data-testid="stToolbar"] {{
        background-color: {BG_MAIN} !important;
        color: {TEXT_LIGHT} !important;
        border: none !important;
    }}

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT_LIGHT} !important;
    }}

    /* ---------- CARDS & LAYOUT ---------- */
    .header-card {{
        background-color: white !important;
        color: #111 !important;
        border-radius: 0.8rem;
        padding: 1.4rem;
        margin-top: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.25);
    }}

    .block-container {{
        background-color: transparent !important;
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
    }}

    /* ---------- FOOTER ---------- */
    footer {{visibility: hidden !important;}}

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
            <div class="splash-title">AncientVisionFLL</div>
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


# --------- Load Firestore Data ----------
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


# --------- Sidebar Filters ----------
findings = load_findings()

st.sidebar.header("🔎 Φίλτρα")

type_options = ["coin", "sherd", "other"]
selected_types = st.sidebar.multiselect(
    "Τύπος ευρήματος",
    type_options,
    default=type_options
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
    """
    <div class="header-card">
        <div class="subtitle-small" style="font-size:0.8rem; text-transform:uppercase; color:#666;">
            FLL Innovation Project
        </div>
        <div style="font-size:2.1rem; font-weight:700; margin-bottom:0.25rem;">
            AncientVisionFLL – Archaeology Dashboard
        </div>
        <div style="color:#444;">
            Ψηφιακό εργαλείο για καταγραφή & οργάνωση αρχαιολογικών ευρημάτων.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------- KPI CARDS ----------
total = len(filtered)
sites = filtered["site_name"].nunique() if not filtered.empty else 0
periods_count = filtered["period"].nunique() if not filtered.empty else 0

kpi_css = """
    <style>
    .kpi-row {
        display: flex; gap: 1rem;
        margin-bottom: 1rem;
    }
    .kpi-card {
        flex: 1;
        padding: 1rem;
        border-radius: 0.6rem;
        color: #fff;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0,0,0,0.22);
    }
    </style>
"""
st.markdown(kpi_css, unsafe_allow_html=True)

st.markdown(f"""
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
""", unsafe_allow_html=True)


# --------- GALLERY ----------
st.markdown("### 📸 Πρόσφατα ευρήματα")

if not filtered.empty:
    rows = filtered.sort_values("timestamp", ascending=False)
    rows = rows[
        rows["image_bytes"].notnull() |
        (rows["image_url"].astype(str) != "")
    ]

    if rows.empty:
        st.info("Δεν υπάρχουν εικόνες ακόμη.")
    else:
        cols = st.columns(4)
        for idx, (_, row) in enumerate(rows.head(8).iterrows()):
            col = cols[idx % 4]
            img = row["image_bytes"] if row["image_bytes"] not in [None, b""] else row["image_url"]
            col.image(img, caption=row["coin_name"], use_column_width=True)
else:
    st.info("Δεν υπάρχουν ευρήματα ακόμη.")


# --------- HIDE FOOTER ONLY ----------
st.markdown("<style>footer{visibility:hidden;}</style>", unsafe_allow_html=True)
