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

# --------- Φόρτωση δεδομένων από Firestore ----------
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

# --------- Ρυθμίσεις σελίδας ----------
st.set_page_config(
    page_title="Πίνακας & μικρός χάρτης",
    layout="wide",
    page_icon="📋"
)

# --------- CSS για cards & φόντο ----------
st.markdown(
    """
    <style>
    .main > div {
        background-color: #f1f2f7;
    }
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

st.markdown("## 📋 Πίνακας ευρημάτων & μικρός χάρτης")

# --------- Δεδομένα ----------
findings = load_findings()

# --------- Sidebar φίλτρα ----------
st.sidebar.header("Φίλτρα (πίνακας & χάρτης)")

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

# ====== Πάνω σειρά: μικρός χάρτης αριστερά, πληροφορίες δεξιά ======
col_map, col_info = st.columns([1.2, 2])

with col_map:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Μικρός χάρτης ευρημάτων")

    # κρατάμε μόνο όσα έχουν συντεταγμένες
    map_df = filtered.dropna(subset=["latitude", "longitude"]).copy()

    if not map_df.empty:
        # st.map θέλει στήλες lat / lon
        map_df = map_df.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(
            map_df[["lat", "lon"]],
            zoom=6,
            use_container_width=True
        )
    else:
        st.info("Δεν υπάρχουν ευρήματα με συντεταγμένες ακόμη.")

    st.markdown('</div>', unsafe_allow_html=True)

with col_info:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Πληροφορίες προβολής")
    st.write(
        "Σε αυτή τη σελίδα βλέπεις τον αναλυτικό πίνακα της βάσης δεδομένων "
        "και έναν μικρό χάρτη επάνω αριστερά για γρήγορο οπτικό έλεγχο των ευρημάτων. "
        "Τα φίλτρα στην αριστερή μπάρα επηρεάζουν και τον χάρτη και τον πίνακα."
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ====== Κάτω: μεγάλος πίνακας ευρημάτων ======
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Αναλυτικός πίνακας ευρημάτων")

if not filtered.empty:
    show_cols = [
        "coin_name", "type", "period",
        "site_name", "latitude", "longitude",
        "timestamp", "notes"
    ]
    st.dataframe(
        filtered[show_cols],
        use_container_width=True,
        height=500
    )
else:
    st.info("Δεν υπάρχουν ευρήματα για εμφάνιση.")
st.markdown('</div>', unsafe_allow_html=True)
