
import streamlit as st
import pandas as pd
import pydeck as pdk
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --------- Firebase init (Cloud μέσω st.secrets) ----------
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --------- Load data from Firestore ----------
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

st.set_page_config(page_title="AncientVisionFLL – Dashboard", layout="wide")
st.title("🏺 AncientVisionFLL – Dashboard Ευρημάτων")

findings = load_findings()

# --------- Sidebar Filters ----------
st.sidebar.header("🔎 Φίλτρα")

type_options = ["coin", "sherd", "other"]
selected_types = st.sidebar.multiselect(
    "Τύπος Ευρήματος",
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

# --------- KPIs ----------
st.markdown("### 📊 Συνολικά Στοιχεία")
col1, col2, col3 = st.columns(3)
col1.metric("🪙 Σύνολο Ευρημάτων", len(filtered))
col2.metric("🏛️ Αρχαιολογικοί Χώροι",
            filtered["site_name"].nunique() if not filtered.empty else 0)
col3.metric("🕰️ Διαφορετικές Περίοδοι",
            filtered["period"].nunique() if not filtered.empty else 0)

# --------- Map ----------
st.markdown("### 🗺️ Χάρτης Ευρημάτων")
map_df = filtered.dropna(subset=["latitude", "longitude"])

if not map_df.empty:
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[longitude, latitude]',
        get_color='[200, 30, 0, 160]',
        get_radius=400,
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=map_df["latitude"].mean(),
        longitude=map_df["longitude"].mean(),
        zoom=6
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{coin_name}\n{site_name}\n{period}"}
    ))
else:
    st.info("Δεν υπάρχουν ευρήματα με συντεταγμένες ακόμη.")

# --------- Table ----------
st.markdown("### 📋 Πίνακας Ευρημάτων")
if not filtered.empty:
    st.dataframe(
        filtered[[
            "coin_name", "type", "period",
            "site_name", "latitude", "longitude",
            "timestamp", "notes"
        ]],
        use_container_width=True
    )
else:
    st.info("Δεν υπάρχουν ευρήματα για εμφάνιση.")

# --------- Photos ----------
st.markdown("### 📸 Φωτογραφίες Ευρημάτων")
if not filtered.empty:
    for i, row in filtered.iterrows():
        if row["image_url"]:
            st.image(
                row["image_url"],
                caption=f'{row["coin_name"]} – {row["site_name"]}',
                width=220
            )
else:
    st.info("Δεν υπάρχουν φωτογραφίες για εμφάνιση.")
