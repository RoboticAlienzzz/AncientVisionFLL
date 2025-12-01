import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ------------------------- COLORS -------------------------
BG_MAIN = "#2e3a47"      # ίδιο με app.py
BG_SIDEBAR = "#384655"
CARD_COLOR = "#3f4a5b"   # χρώμα από την εικόνα
TEXT_LIGHT = "#f8fafc"

# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --------- Page config ----------
st.set_page_config(page_title="New Finding", page_icon="➕", layout="centered")

# --------- GLOBAL STYLE (ίδιο theme με app.py) ----------
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
    [data-testid="stSidebar"] {{
        background-color: {BG_SIDEBAR} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {TEXT_LIGHT} !important;
    }}
    .block-container {{
        background-color: transparent !important;
        padding-top: 0.8rem;
        padding-bottom: 1.5rem;
    }}

    /* Λίγο πιο όμορφα inputs στη φόρμα */
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stTextArea textarea {{
        background-color: #ffffff !important;
        color: #111 !important;
        border-radius: 0.4rem !important;
        border: 1px solid rgba(0,0,0,0.25) !important;
    }}

    /* Κρύβουμε footer */
    footer {{visibility: hidden !important;}}
    </style>
    """,
    unsafe_allow_html=True
)

# --------- UI ----------
st.markdown("## ➕ Καταχώριση νέου αρχαιολογικού ευρήματος")
st.write(
    "Συμπλήρωσε τα στοιχεία του ευρήματος. "
    "**Προσωρινά οι φωτογραφίες δεν αποθηκεύονται** – κρατάμε μόνο τα δεδομένα."
)

with st.form("new_finding_form"):
    col_left, col_right = st.columns(2)

    with col_left:
        coin_name = st.text_input("Όνομα / περιγραφή ευρήματος*")
        obj_type = st.selectbox("Τύπος", ["coin", "sherd", "other"])
        period = st.text_input("Περίοδος (π.χ. Classical, Hellenistic)")
        site_name = st.text_input("Αρχαιολογικός χώρος*")

    with col_right:
        latitude = st.number_input("Latitude (γεωγραφικό πλάτος)", format="%.6f")
        longitude = st.number_input("Longitude (γεωγραφικό μήκος)", format="%.6f")

        # UI για κάμερα / αρχείο αλλά δεν αποθηκεύουμε την εικόνα
        capture_mode = st.radio(
            "Φωτογραφία ευρήματος (προαιρετική – δεν αποθηκεύεται προς το παρόν)",
            ["📷 Χρήση κάμερας", "📁 Επιλογή από αρχείο"],
        )

        if capture_mode.startswith("📷"):
            st.camera_input("Βγάλε φωτογραφία ευρήματος")
        else:
            st.file_uploader(
                "Επέλεξε φωτογραφία από τη συσκευή",
                type=["jpg", "jpeg", "png"]
            )

    notes = st.text_area("Σημειώσεις για αρχαιολόγους (προαιρετικό)", height=100)

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
            "image_bytes": None,   # δεν αποθηκεύουμε εικόνα
            "image_url": "",
            "notes": notes,
            "timestamp": datetime.now()
        }
        db.collection("findings").add(data)
        st.success("✅ Το εύρημα αποθηκεύτηκε με επιτυχία (χωρίς φωτογραφία).")
