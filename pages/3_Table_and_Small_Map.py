import streamlit as st
import pandas as pd
import pydeck as pdk
import firebase_admin
from firebase_admin import credentials, firestore

# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=[
            "id", "coin_name", "type", "period", "site_name",
            "latitude", "longitude", "image_url", "notes", "timestamp"
        ])

st.set_page_config(page_title="Πίνακας & Μικρός Χάρτης", layout="wide", page_icon="📋")

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

# ====== Πάνω σειρά: μικρός χάρτης πάνω αριστερά ======
col_map, col_dummy = st.columns([1.2, 2])

with col_map:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Μικρός χάρτης ευρημάτων")

    map_df = filtered.dropna(subset=["latitude", "longitude"])

    if not map_df.empty:
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=500,
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=map_df["latitude"].mean(),
            longitude=map_df["longitude"].mean(),
            zoom=6
        )

        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "{coin_name}\\n{site_name}\\n{period}"}
        )
        # μικρό «τετράγωνο» παράθυρο χάρτη
        st.pydeck_chart(deck, use_container_width=True, height=260)
    else:
        st.info("Δεν υπάρχουν ευρήματα με συντεταγμένες ακόμη.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_dummy:
    # αφήνουμε κενό ή βάζουμε ένα μικρό κείμενο/οδηγίες
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Πληροφορίες προβολής")
    st.write(
        "Σε αυτή τη σελίδα βλέπεις τον πίνακα της βάσης δεδομένων και "
        "έναν μικρό χάρτη επάνω αριστερά για γρήγορο οπτικό έλεγχο."
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ====== Κάτω: μεγάλος πίνακας βάσης ======
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
