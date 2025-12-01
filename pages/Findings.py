import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="Findings", page_icon="📋", layout="wide")

# ------------------------
# FIREBASE INIT
# ------------------------
try:
    firebase_admin.get_app()
except ValueError:
    cfg = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(cfg)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ------------------------
# THEME COLORS (ίδια με app.py)
# ------------------------
BG_MAIN = "#2e3a47"
BG_SIDEBAR = "#384655"
CARD_COLOR = "#3f4a5b"
TEXT_LIGHT = "#f8fafc"

# ------------------------
# GLOBAL STYLE (ίδιο look με Dashboard)
# ------------------------
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
        border: none !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
    }}

    .block-container {{
        background-color: transparent !important;
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
    }}

    h1, h2, h3, h4, h5, h6,
    p, span, div, label {{
        color: {TEXT_LIGHT} !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {{
        color: black !important;
        background-color: white !important;
    }}

    .stAlert p {{
        color: black !important;
    }}

    .finder-card {{
        background-color: {CARD_COLOR};
        border-radius: 0.8rem;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.35);
        margin-bottom: 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# FAKE AI CLASSIFIER (DEMO)
# ------------------------
def ai_suggest_fields(image_bytes: bytes):
    """
    Demo AI – αργότερα εδώ βάζετε το πραγματικό σας μοντέλο.
    Τώρα επιστρέφει απλά κάποιες ενδεικτικές τιμές.
    """
    if not image_bytes:
        return None

    return {
        "name": "Unknown coin",
        "type": "coin",
        "period": "Roman",
        "confidence": 0.65,
    }

# ------------------------
# ΒΟΗΘΗΤΙΚΟ: Φόρτωση ευρημάτων
# ------------------------
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
        data.append(
            {
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
                "timestamp": d.get("timestamp", ""),
            }
        )
    return pd.DataFrame(data)

# ------------------------
# STATE: αν είναι ανοικτή η φόρμα
# ------------------------
if "show_new_form" not in st.session_state:
    st.session_state["show_new_form"] = False

# ------------------------
# HEADER
# ------------------------
st.markdown(
    """
    <div class="finder-card">
        <h2>📋 Πίνακας ευρημάτων & μικρός χάρτης</h2>
        <p style="opacity:0.9;">
            Εδώ βλέπεις όλα τα καταχωρημένα ευρήματα, μαζί με έναν μικρό χάρτη.
            Μπορείς επίσης να προσθέσεις νέο εύρημα από το κουμπί παρακάτω.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# ΚΟΥΜΠΙ ΓΙΑ ΕΜΦΑΝΙΣΗ / ΚΡΥΨΙΜΟ ΦΟΡΜΑΣ
# ------------------------
btn_col1, btn_col2 = st.columns([1, 4])
with btn_col1:
    if st.button("➕ Καταχώριση νέου ευρήματος"):
        st.session_state["show_new_form"] = not st.session_state["show_new_form"]

# ------------------------
# ΦΟΡΜΑ ΝΕΟΥ ΕΥΡΗΜΑΤΟΣ (ΜΕ AI) – ΜΕΣΑ ΣΤΗ ΣΕΛΙΔΑ
# ------------------------
if st.session_state["show_new_form"]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="finder-card">', unsafe_allow_html=True)
    st.markdown("### 📷 Νέο εύρημα", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "📸 Βγάλε φωτογραφία ή ανέβασε μία",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        label_visibility="visible",
        key="new_finding_uploader"
    )

    ai_result = None
    image_bytes = None

    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
        st.image(uploaded_file, caption="Προεπισκόπηση", use_column_width=True)

        ai_result = ai_suggest_fields(image_bytes)
        if ai_result:
            with st.expander("🔮 Προτάσεις AI για το εύρημα", expanded=True):
                st.write(f"**Προτεινόμενος τίτλος:** {ai_result.get('name', '')}")
                st.write(f"**Προτεινόμενος τύπος:** {ai_result.get('type', '')}")
                st.write(f"**Προτεινόμενη περίοδος:** {ai_result.get('period', '')}")
                conf = ai_result.get("confidence", None)
                if conf is not None:
                    st.write(f"**Βεβαιότητα AI (demo):** {int(conf * 100)}%")
                st.caption(
                    "⚠ Demo AI – οι τιμές είναι ενδεικτικές και μπορούν να διορθωθούν από τους μαθητές."
                )

    type_options = ["coin", "sherd", "other"]
    default_type = "coin"
    default_name = ""
    default_period = ""

    if ai_result:
        default_type = ai_result.get("type", default_type)
        default_name = ai_result.get("name", default_name)
        default_period = ai_result.get("period", default_period)

    if default_type not in type_options:
        default_type = "coin"
    default_type_index = type_options.index(default_type)

    with st.form("new_finding_form_in_findings"):
        col1, col2 = st.columns(2)

        with col1:
            coin_name = st.text_input("Όνομα/Τίτλος", value=default_name)
            period = st.text_input("Περίοδος", value=default_period)
            finding_type = st.selectbox(
                "Τύπος", type_options, index=default_type_index
            )

        with col2:
            site_name = st.text_input("Τοποθεσία (όνομα)")
            latitude = st.number_input("Latitude", format="%.6f")
            longitude = st.number_input("Longitude", format="%.6f")

        notes = st.text_area("Σημειώσεις")

        submitted = st.form_submit_button("💾 Αποθήκευση")

    if submitted:
        if uploaded_file is None or image_bytes is None:
            st.error("Πρέπει πρώτα να ανεβάσεις ή να βγάλεις μία φωτογραφία.")
        else:
            db.collection("findings").add(
                {
                    "coin_name": coin_name,
                    "type": finding_type,
                    "period": period,
                    "site_name": site_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "image_bytes": image_bytes,
                    "image_url": "",
                    "notes": notes,
                    "timestamp": datetime.utcnow(),
                }
            )
            st.success("✅ Το εύρημα αποθηκεύτηκε επιτυχώς!")
            st.session_state["show_new_form"] = False
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# Φόρτωση δεδομένων για πίνακα & χάρτη
# ------------------------
df = load_findings()

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------
# ΜΙΚΡΟΣ ΧΑΡΤΗΣ + INFO
# ------------------------
st.markdown('<div class="finder-card">', unsafe_allow_html=True)
col_map, col_info = st.columns([2, 1])

with col_map:
    st.markdown("#### 🗺️ Μικρός χάρτης ευρημάτων")
    # κρατάμε μόνο όσα έχουν γεωγραφία
    if not df.empty and df["latitude"].notnull().any():
        map_df = df.dropna(subset=["latitude", "longitude"])
        if not map_df.empty:
            st.map(map_df[["latitude", "longitude"]])
        else:
            st.info("Δεν υπάρχουν συντεταγμένες για εμφάνιση στον χάρτη.")
    else:
        st.info("Δεν υπάρχουν ακόμη ευρήματα με συντεταγμένες.")

with col_info:
    st.markdown("#### ℹ️ Πληροφορίες προβολής")
    st.write(
        "Στον χάρτη εμφανίζονται τα ευρήματα για τα οποία έχουν δοθεί συντεταγμένες "
        "(latitude/longitude). Κάτω εμφανίζεται ο αναλυτικός πίνακας με όλα τα πεδία."
    )

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------
# ΠΙΝΑΚΑΣ ΕΥΡΗΜΑΤΩΝ
# ------------------------
st.markdown('<div class="finder-card">', unsafe_allow_html=True)
st.markdown("#### 📑 Αναλυτικός πίνακας ευρημάτων")

if df.empty:
    st.info("Δεν υπάρχουν ακόμη καταχωρημένα ευρήματα.")
else:
    # δεν χρειαζόμαστε image_bytes / image_url στον πίνακα
    table_df = df.drop(columns=["image_bytes", "image_url"], errors="ignore")
    st.dataframe(table_df, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
