import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --------- Load data ----------
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
            "image_url": d.get("image_url", ""),
            "notes": d.get("notes", ""),
            "timestamp": d.get("timestamp", "")
        })
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "id", "coin_name", "type", "period", "site_name",
            "latitude", "longitude", "image_url", "notes", "timestamp"
        ])

# --------- Page config ----------
st.set_page_config(
    page_title="AncientVision – Dashboard",
    layout="wide",
    page_icon="🏺"
)

# --------- CSS για Sufee-style + cards ----------
st.markdown(
    """
    <style>
    /* Σκούρο sidebar */
    [data-testid="stSidebar"] {
        background-color: #343a40;
    }
    [data-testid="stSidebar"] * {
        color: #f8f9fa;
    }

    /* Κύριο φόντο */
    .main > div {
        background-color: #f1f2f7;
    }

    /* Header card για τίτλο project */
    .header-card {
        background-color: #ffffff;
        border-radius: 0.9rem;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .big-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
        color: #343a40;
    }
    .subtitle {
        font-size: 0.95rem;
        color: #6c757d;
        margin-bottom: 0.2rem;
    }
    .subtitle-small {
        font-size: 0.8rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Κάρτες KPI */
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 0.8rem;
    }
    .kpi-card {
        flex: 1;
        padding: 0.9rem 1.1rem;
        border-radius: 0.6rem;
        color: #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .kpi-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.9;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 0.15rem;
    }

    .kpi-blue   { background: #007bff; }
    .kpi-teal   { background: #17a2b8; }
    .kpi-orange { background: #fd7e14; }

    /* Generic card (για gallery) */
    .card {
        background-color: #ffffff;
        border-radius: 0.8rem;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------- Φίλτρα & δεδομένα ----------
findings = load_findings()

st.sidebar.header("🔎 Φίλτρα")

type_options = ["coin", "sherd", "other"]
selected_types = st.sidebar.multiselect(
    "Τύπος ευρήματος",
    options=type_options,
    default=type_options
)

period_options = (
    sorted(findings["period"].dropna().unique().tolist())
    if not findings.empty else []
)
selected_periods = st.sidebar.multiselect(
    "Περίοδος",
    options=period_options,
    default=period_options
)

filtered = findings.copy()
if selected_types:
    filtered = filtered[filtered["type"].isin(selected_types)]
if selected_periods:
    filtered = filtered[filtered["period"].isin(selected_periods)]

# ====== HEADER CARD με τίτλο project ======
st.markdown(
    """
    <div class="header-card">
        <div class="subtitle-small">FLL Innovation Project</div>
        <div class="big-title">AncientVision – Dashboard</div>
        <div class="subtitle">
            Ψηφιακό εργαλείο για αναγνώριση νομισμάτων & θραυσμάτων και
            οργάνωση αρχαιολογικών ευρημάτων σε πραγματικό χρόνο.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ====== KPI CARDS (χωρίς χάρτη & πίνακα εδώ) ======
total_findings = len(filtered)
sites_count = filtered["site_name"].nunique() if not filtered.empty else 0
periods_count = filtered["period"].nunique() if not filtered.empty else 0

st.markdown(
    f"""
    <div class="kpi-row">
        <div class="kpi-card kpi-blue">
            <div class="kpi-label">Συνολο ευρηματων</div>
            <div class="kpi-value">{total_findings}</div>
        </div>
        <div class="kpi-card kpi-teal">
            <div class="kpi-label">Αρχαιολογικοι χωροι</div>
            <div class="kpi-value">{sites_count}</div>
        </div>
        <div class="kpi-card kpi-orange">
            <div class="kpi-label">Διαφορετικες περιοδοι</div>
            <div class="kpi-value">{periods_count}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ====== GALLERY CARD (μόνο φωτογραφίες στο dashboard) ======
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📸 Προσφατα ευρηματα")

if not filtered.empty:
    rows = filtered.sort_values("timestamp", ascending=False)
    rows = rows[rows["image_url"] != ""]
    if rows.empty:
        st.info("Δεν υπάρχουν φωτογραφίες ακόμη. Καταχώρισε ένα νέο εύρημα από τη σελίδα ‘New Finding’.")
    else:
        cols = st.columns(4)
        max_photos = min(8, len(rows))  # μέχρι 8 thumbnails
        for idx, (_, row) in enumerate(rows.head(max_photos).iterrows()):
            col = cols[idx % 4]
            with col:
                st.image(
                    row["image_url"],
                    caption=f'{row["coin_name"]}',
                    use_column_width=True
                )
else:
    st.info("Δεν υπάρχουν ευρήματα ακόμη. Καταχώρισε το πρώτο από τη σελίδα ‘New Finding’.")
st.markdown('</div>', unsafe_allow_html=True)

# ΤΕΛΟΣ – ο χάρτης & ο πίνακας είναι μόνο στην σελίδα Map/Table
