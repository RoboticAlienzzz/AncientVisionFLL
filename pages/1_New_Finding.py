import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="New Finding", page_icon="📷", layout="wide")

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
# UI TITLE
# ------------------------
st.markdown(
    """
    <h2 style='color:#f8fafc;'>📷 Καταχώριση νέου ευρήματος</h2>
    <p style='color:#cbd5e1;'>Βγάλε ή ανέβασε φωτογραφία, συμπλήρωσε τα στοιχεία και αποθήκευσε το εύρημα.</p>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# PHOTO CAPTURE (λειτουργεί σε κινητό & desktop)
# ------------------------
uploaded_file = st.file_uploader(
    "📸 Βγάλε φωτογραφία ή ανέβασε μία",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
    label_visibility="visible"
)

if uploaded_file:
    st.image(uploaded_file, caption="Προεπισκόπηση", use_column_width=True)

# ------------------------
# FORM FIELDS
# ------------------------
with st.form("new_finding_form"):
    col1, col2 = st.columns(2)

    with col1:
        coin_name = st.text_input("Όνομα/Τίτλος")
        period = st.text_input("Περίοδος")
        finding_type = st.selectbox(
            "Τύπος",
            ["coin", "sherd", "other"]
        )

    with col2:
        site_name = st.text_input("Τοποθεσία (όνομα)")
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")

    notes = st.text_area("Σημειώσεις")

    submitted = st.form_submit_button("💾 Αποθήκευση")

# ------------------------
# SAVE LOGIC (μόνο Firestore)
# ------------------------
if submitted:

    if uploaded_file is None:
        st.error("Πρέπει να ανεβάσεις ή να βγάλεις μία φωτογραφία.")
        st.stop()

    # Διαβάζουμε τα bytes της εικόνας
    image_bytes = uploaded_file.read()

    # Αποθηκεύουμε κατευθείαν στη βάση
    db.collection("findings").add({
        "coin_name": coin_name,
        "type": finding_type,
        "period": period,
        "site_name": site_name,
        "latitude": latitude,
        "longitude": longitude,
        "image_bytes": image_bytes,  # ΕΔΩ ΜΠΑΙΝΕΙ Η ΕΙΚΟΝΑ
        "image_url": "",              # Αφήνεται άδειο
        "notes": notes,
        "timestamp": datetime.utcnow(),
    })

    st.success("Το εύρημα αποθηκεύτηκε επιτυχώς!")
    st.balloons()
