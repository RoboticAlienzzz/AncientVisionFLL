import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --------- Firebase init ----------
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase_key"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Νέο εύρημα", layout="centered", page_icon="➕")

st.markdown("## ➕ Καταχώριση νέου αρχαιολογικού ευρήματος")
st.markdown(
    "Συμπλήρωσε τα στοιχεία και βγάλε ή ανέβασε μια φωτογραφία. "
    "Η εικόνα αποθηκεύεται απευθείας στη βάση δεδομένων μαζί με τα υπόλοιπα στοιχεία."
)

# --------- Φόρμα νέου ευρήματος ----------
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

        capture_mode = st.radio(
            "Πώς θέλεις να δώσεις τη φωτογραφία;",
            ["📷 Χρήση κάμερας", "📁 Επιλογή από αρχείο"],
        )

        camera_image = None
        file_image = None

        if capture_mode.startswith("📷"):
            camera_image = st.camera_input("Βγάλε φωτογραφία ευρήματος")
        else:
            file_image = st.file_uploader(
                "Επέλεξε φωτογραφία από τη συσκευή",
                type=["jpg", "jpeg", "png"]
            )

    notes = st.text_area("Σημειώσεις για αρχαιολόγους (προαιρετικό)", height=100)

    submitted = st.form_submit_button("💾 Αποθήκευση ευρήματος")

if submitted:
    uploaded_image = camera_image if camera_image is not None else file_image

    if not coin_name or not site_name:
        st.error("Συμπλήρωσε τα πεδία με αστερίσκο (*).")
    elif uploaded_image is None:
        st.error("Πρέπει να δώσεις μία φωτογραφία (κάμερα ή αρχείο).")
    else:
        # Παίρνουμε τα bytes της εικόνας
        image_bytes = uploaded_image.getvalue()

        data = {
            "coin_name": coin_name,
            "type": obj_type,
            "period": period,
            "site_name": site_name,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "image_bytes": image_bytes,  # <-- αποθήκευση φωτογραφίας στη Firestore
            "notes": notes,
            "timestamp": datetime.now()
        }

        db.collection("findings").add(data)
        st.success("✅ Το εύρημα αποθηκεύτηκε μαζί με τη φωτογραφία!")
        st.info("Μπορείς να το δεις στο Dashboard και στις σελίδες χάρτη/πίνακα.")
