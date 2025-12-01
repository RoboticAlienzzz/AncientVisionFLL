import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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
st.set_page_config(page_title="New Finding", page_icon="➕", layout="centered")

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

    /* Λευκά inputs με μαύρο κείμενο */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {{
        background-color: white !important;
        color: black !important;
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
    ::placeholder {{
        color: rgba(255,255,255,0.6) !important;
    }}
    .stAlert p {{
        color: black !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------- UI ----------
st.markdown("## ➕ Καταχώριση νέου αρχαιολογικού ευρήματος")
st.write(
    "Συμπλήρωσε τα στοιχεία του ευρήματος. "
    "Προσωρινά οι φωτογραφίες **δεν αποθηκεύονται** στη βάση."
)

with st.form("new_finding_form"):
    col_left, col_right = st.columns(2)

    with col_left:
        coin_name = st.text_input("Όνομα / περιγραφή ευρήματος*")
        obj_type = st.selectbox("Τύπος", ["coin", "sherd", "other"])
        period = st.text_input("Περίοδος (π.χ. Hellenistic)")
        site_name = st.text_input("Αρχαιολογικός χώρος*")

    with col_right:
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")

        capture_mode = st.radio(
            "Φωτογραφία (δεν αποθηκεύεται ακόμη)",
            ["📷 Χρήση κάμερας", "📁 Από αρχείο"]
        )

        if capture_mode.startswith("📷"):
            st.camera_input("Βγάλε φωτογραφία")
        else:
            st.file_uploader("Επιλογή εικόνας", type=["jpg", "jpeg", "png"])

    notes = st.text_area("Σημειώσεις για αρχαιολόγους", height=100)
    submitted = st.form_submit_button("💾 Αποθήκευση ευρήματος")

if submitted:
    if not coin_name or not site_name:
        st.error("Συμπλήρωσε τα πεδία με αστερίσκο (*).")
    else:
        data = {
            "coin_name": coin_name,
            "type": obj_type,
            "period": period,
            "site_name": site_name,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "image_bytes": None,
            "image_url": "",
            "notes": notes,
            "timestamp": datetime.now()
        }
        db.collection("findings").add(data)
        st.success("✅ Το εύρημα αποθηκεύτηκε με επιτυχία (χωρίς φωτογραφία).")
