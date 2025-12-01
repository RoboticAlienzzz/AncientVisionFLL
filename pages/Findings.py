import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# ------------------------- COLORS -------------------------
BG_MAIN = "#2e3a47"
BG_SIDEBAR = "#384655"
CARD_COLOR = "#3f4a5b"
TEXT_LIGHT = "#f8fafc"

# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --------- Page config ----------
st.set_page_config(
    page_title="Findings Table & Small Map",
    page_icon="📋",
    layout="wide"
)

# --------- GLOBAL STYLE ----------
st.markdown(
    f"""
    <style>
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
    div[data-testid="stToolbar"] {{
        background-color: {BG_MAIN} !important;
        color: {TEXT_LIGHT} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
    }}
    .block-container {{
        background-color: transparent !important;
        padding-top: 1rem;
        padding-bottom: 1.5rem;
    }}

    .small-header-card {{
        background-color: {CARD_COLOR} !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 0.7rem;
        padding: 1rem 1.2rem;
        margin-top: 3rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}

    footer {{visibility:hidden !important;}}
    </style>
    """,
    unsafe_allow_html=True
)

# --------- ΛΕΥΚΟ ΚΕΙΜΕΝΟ ----------
st.markdown(
    f"""
    <style>
    h1, h2, h3, h4, h5, h6,
    p, span, div, label {{
        color: {TEXT_LIGHT} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {TEXT_LIGHT} !important;
    }}
    .stAlert p {{
        color: black !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

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
            "image_url": d.get("image_url", ""),
            "notes": d.get("notes", ""),
            "timestamp": d.get("timestamp", "")
        })
    return pd.DataFrame(data)

df = load_findings()

# --------- Τίτλος σελίδας ----------
st.markdown(
    """
    <div class="small-header-card">
        <span style="font-size:1.4rem; font-weight:700;">📋 Πίνακας ευρημάτων & μικρός χάρτης</span><br/>
        <span style="opacity:0.9;">Γρήγορη προεπισκόπηση ευρημάτων με πίνακα και χάρτη επάνω αριστερά.</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --------- Layout: Μικρός χάρτης + πληροφορίες ----------
col_map, col_info = st.columns([1.4, 2])

with col_map:
    st.markdown("##### 🗺️ Μικρός χάρτης ευρημάτων")
    if df.empty or df["latitude"].isna().all():
        st.info("Δεν υπάρχουν ακόμη συντεταγμένες για χάρτη.")
    else:
        map_df = df.dropna(subset=["latitude", "longitude"]).copy()
        map_df.rename(columns={"latitude": "lat", "longitude": "lon"}, inplace=True)
        st.map(map_df[["lat", "lon"]], use_container_width=True)

with col_info:
    st.markdown("##### ℹ️ Πληροφορίες προβολής")
    st.write(
        "- Ο χάρτης δείχνει όλα τα ευρήματα με καταχωρημένες συντεταγμένες.\n"
        "- Ο πίνακας παρακάτω περιέχει πλήρη στοιχεία για κάθε εύρημα.\n"
        "- Μπορείς να κάνεις scroll / sort στον πίνακα για γρήγορο έλεγχο."
    )

st.markdown("---")

# --------- Πίνακας ευρημάτων ----------
st.markdown("### 📑 Αναλυτικός πίνακας ευρημάτων")

if df.empty:
    st.info("Δεν υπάρχουν ευρήματα στη βάση δεδομένων ακόμη.")
else:
    show_cols = [
        "coin_name", "type", "period", "site_name",
        "latitude", "longitude", "timestamp", "notes"
    ]
    existing_cols = [c for c in show_cols if c in df.columns]
    st.dataframe(
        df[existing_cols],
        use_container_width=True,
        hide_index=True
    )
