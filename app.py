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
    page_title="AncientVisionFLL – Dashboard",
    layout="wide",
    page_icon="🏺"
)

# --------- CSS για Sufee-style χρώματα ----------
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

    /* Κύριο φόντο σαν admin template */
    .main > div {
        background-color: #f1f2f7;
    }

    /* Τίτλος & υπότιτλος */
    .big-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: #343a40;
    }
    .subtitle {
        font-size: 0.95rem;
        color: #6c757d;
        margin-bottom: 1.2rem;
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

    .kpi-blue   { background: #007bff; }  /* μπλε */
    .kpi-teal   { background: #17a2b8; }  /* τιρκουάζ */
    .kpi-orange { background: #fd7e14; }  /* πορτοκαλί */

    /* Tabs container λίγο πιο “card” */
    .stTabs [role="tablist"] {
        border-bottom: 1px solid #dee2e6;
    }
    .stTabs [role="tab"] {
        padding-top: 0.4rem;
        padding-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------- Φόρτωση δεδομένων ----------
findings = load_findings()

# ====== SIDEBAR FILTERS ======
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

# ====== HEADER ======
st.markdown(
    '<div class="big-title">AncientVisionFLL – Archaeology Dashboard</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Ζωντανή εικόνα για νομίσματα και θραύσματα από τους αρχαιολογικούς χώρους της ομάδας.</div>',
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

# ====== MAIN TABS ======
tab_map, tab_table, tab_photos = st.tabs(["🗺️ Χάρτης", "📋 Πίνακας", "📸 Φωτογραφίες"])

# --- Χάρτης ---
with tab_map:
    st.subheader("Χωρική κατανομή ευρημάτων")
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

# --- Πίνακας ---
with tab_table:
    st.subheader("Αναλυτικός πίνακας")
    if not filtered.empty:
        show_cols = [
            "coin_name", "type", "period",
            "site_name", "latitude", "longitude",
            "timestamp", "notes"
        ]
        st.dataframe(
            filtered[show_cols],
            use_container_width=True,
            height=420
        )
    else:
        st.info("Δεν υπάρχουν ευρήματα για εμφάνιση.")

# --- Φωτογραφίες ---
with tab_photos:
    st.subheader("Γκαλερί ευρημάτων")
    if not filtered.empty:
        rows = filtered[filtered["image_url"] != ""]
        if rows.empty:
            st.info("Δεν υπάρχουν φωτογραφίες ακόμη.")
        else:
            cols = st.columns(3)
            for idx, (_, row) in enumerate(rows.iterrows()):
                col = cols[idx % 3]
                with col:
                    st.image(
                        row["image_url"],
                        caption=f'{row["coin_name"]} – {row["site_name"]}',
                        use_column_width=True
                    )
    else:
        st.info("Δεν υπάρχουν φωτογραφίες για εμφάνιση.")
