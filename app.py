import time
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

# --------- Page config ----------
st.set_page_config(
    page_title="AncientVisionFLL – Dashboard",
    layout="wide",
    page_icon="🏺"
)

# --------- Global background & SPLASH screen ----------
# Gradient background για όλη την εφαρμογή
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1c7ed6 0, #0b7285 35%, #111827 85%);
        color: #f8fafc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Splash μόνο στο πρώτο load του session
if "splash_done" not in st.session_state:
    st.markdown(
        """
        <style>
        .splash-box {
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: #f8fafc;
        }
        .splash-title {
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .splash-subtitle {
            font-size: 1rem;
            opacity: 0.85;
            max-width: 480px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="splash-box">
            <div class="splash-title">AncientVisionFLL</div>
            <div class="splash-subtitle">
                Φόρτωση του αρχαιολογικού πίνακα ελέγχου...
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    progress = st.progress(0)
    for i in range(100):
        time.sleep(0.01)  # ~1 δευτ.
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
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "id", "coin_name", "type", "period", "site_name",
            "latitude", "longitude", "image_bytes", "image_url",
            "notes", "timestamp"
        ])

# --------- Extra CSS για cards / sidebar / KPI ----------
st.markdown(
    """
    <style>
    /* Σκούρο sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
    }
    [data-testid="stSidebar"] * {
        color: #f8f9fa;
    }

    /* Header card για τίτλο project */
    .header-card {
        background-color: #ffffff;
        border-radius: 0.9rem;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
        color: #111827;
    }
    .big-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
        color: #111827;
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
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
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
        box-shadow: 0 1px 6px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
        color: #111827;
    }

    /* Λίγο μικρότερο padding για να θυμίζει web app */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------- Δεδομένα & φίλτρα ----------
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
        <div class="big-title">AncientVisionFLL – Archaeology Dashboard</div>
        <div class="subtitle">
            Ψηφιακό εργαλείο για αναγνώριση νομισμάτων & θραυσμάτων και
            οργάνωση αρχαιολογικών ευρημάτων σε πραγματικό χρόνο.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ====== KPI CARDS ======
total_findings = len(filtered)
sites_count = filtered["site_name"].nunique() if not filtered.empty else 0
periods_count = filtered["period"].nunique() if not filtered.empty else 0

st.markdown(
    f"""
    <div class="kpi-row">
        <div class="kpi-card kpi-blue">
            <div class="kpi-label">Σύνολο ευρημάτων</div>
            <div class="kpi-value">{total_findings}</div>
        </div>
        <div class="kpi-card kpi-teal">
            <div class="kpi-label">Αρχαιολογικοί χώροι</div>
            <div class="kpi-value">{sites_count}</div>
        </div>
        <div class="kpi-card kpi-orange">
            <div class="kpi-label">Διαφορετικές περίοδοι</div>
            <div class="kpi-value">{periods_count}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ====== GALLERY CARD (πρόσφατα ευρήματα) ======
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📸 Πρόσφατα ευρήματα")

if not filtered.empty:
    rows = filtered.sort_values("timestamp", ascending=False)

    # κρατάμε μόνο όσα έχουν εικόνα (bytes ή URL)
    rows = rows[
        rows["image_bytes"].notnull() |
        (rows["image_url"].astype(str) != "")
    ]

    if rows.empty:
        st.info("Δεν υπάρχουν φωτογραφίες ακόμη. Καταχώρισε ένα νέο εύρημα από τη σελίδα ‘New Finding’.")
    else:
        cols = st.columns(4)
        max_photos = min(8, len(rows))
        for idx, (_, row) in enumerate(rows.head(max_photos).iterrows()):
            col = cols[idx % 4]
            with col:
                img = row["image_bytes"] if row["image_bytes"] not in [None, b""] else row["image_url"]
                st.image(
                    img,
                    caption=f'{row["coin_name"]}',
                    use_column_width=True
                )
else:
    st.info("Δεν υπάρχουν ευρήματα ακόμη. Καταχώρισε το πρώτο από τη σελίδα ‘New Finding’.")
st.markdown('</div>', unsafe_allow_html=True)

# ====== Κρύβουμε Streamlit logo, menu, footer ======
st.markdown(
    """
    <style>
    /* κρύβουμε menu / header / footer / toolbar σε όλες τις συσκευές */
    #MainMenu {display: none !important;}
    header {display: none !important;}
    footer {display: none !important;}
    div[data-testid="stToolbar"] {display: none !important;}

    /* σε περίπτωση που εμφανίζεται ειδικό badge (mobile) */
    .viewerBadge_container__1QSob {display: none !important;}

    /* generic: κρύψε οποιοδήποτε link δείχνει προς streamlit.io */
    a[href*="streamlit.io"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)
