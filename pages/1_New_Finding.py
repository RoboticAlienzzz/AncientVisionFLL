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
# FAKE AI CLASSIFIER (DEMO)
# ------------------------
def ai_suggest_fields(image_bytes: bytes):
    """
    Demo συνάρτηση "AI".
    ΤΩΡΑ απλά επιστρέφει σταθερές τιμές,
    αλλά ΕΔΩ θα βάλετε αργότερα το πραγματικό σας μοντέλο
    (π.χ. TensorFlow / REST API κτλ.)
    """
    if not image_bytes:
        return None

    # TODO: αντικαταστήστε αυτό με πραγματικές προβλέψεις από το μοντέλο σας.
    suggestion = {
        "name": "Unknown coin",
        "type": "coin",           # "coin", "sherd" ή "other"
        "period": "Roman",        # π.χ. "Classical", "Hellenistic", "Roman" κλπ
        "confidence": 0.65        # demo confidence
    }
    return suggestion


# ------------------------
# UI TITLE
# ------------------------
st.markdown(
    """
    <h2 style='color:#f8fafc;'>📷 Καταχώριση νέου ευρήματος</h2>
    <p style='color:#cbd5e1;'>
        Βγάλε ή ανέβασε φωτογραφία, άσε την AI να προτείνει τύπο & περίοδο
        και στη συνέχεια συμπλήρωσε/διόρθωσε τα στοιχεία.
    </p>
    """,
    unsafe_allow_html=True,
)

# ------------------------
# PHOTO UPLOADER
# ------------------------
uploaded_file = st.file_uploader(
    "📸 Βγάλε φωτογραφία ή ανέβασε μία",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
    label_visibility="visible"
)

ai_result = None
if uploaded_file:
    image_bytes = uploaded_file.getvalue()
    st.image(uploaded_file, caption="Προεπισκόπηση", use_column_width=True)

    # Καλούμε το "AI" για προτάσεις
    ai_result = ai_suggest_fields(image_bytes)

    if ai_result is not None:
        with st.expander("🔮 Προτάσεις AI για το εύρημα", expanded=True):
            st.write(f"**Προτεινόμενος τίτλος:** {ai_result.get('name', '')}")
            st.write(f"**Προτεινόμενος τύπος:** {ai_result.get('type', '')}")
            st.write(f"**Προτεινόμενη περίοδος:** {ai_result.get('period', '')}")
            conf = ai_result.get("confidence", None)
            if conf is not None:
                st.write(f"**Βεβαιότητα AI (demo):** {int(conf * 100)}%")
            st.caption("⚠ Demo AI – οι τιμές είναι ενδεικτικές. Οι μαθητές μπορούν να τις διορθώσουν.")

# ------------------------
# FORM FIELDS (με default από AI αν υπάρχουν)
# ------------------------
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

with st.form("new_finding_form"):
    col1, col2 = st.columns(2)

    with col1:
        coin_name = st.text_input("Όνομα/Τίτλος", value=default_name)
        period = st.text_input("Περίοδος", value=default_period)
        finding_type = st.selectbox(
            "Τύπος",
            type_options,
            index=default_type_index
        )

    with col2:
        site_name = st.text_input("Τοποθεσία (όνομα)")
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")

    notes = st.text_area("Σημειώσεις")

    submitted = st.form_submit_button("💾 Αποθήκευση")

# ------------------------
# SAVE LOGIC (μόνο Firestore, με εικόνα ως bytes)
# ------------------------
if submitted:
    if uploaded_file is None:
        st.error("Πρέπει να ανεβάσεις ή να βγάλεις μία φωτογραφία πριν αποθηκεύσεις.")
        st.stop()

    image_bytes = uploaded_file.getvalue()

    db.collection("findings").add({
        "coin_name": coin_name,
        "type": finding_type,
        "period": period,
        "site_name": site_name,
        "latitude": latitude,
        "longitude": longitude,
        "image_bytes": image_bytes,  # εικόνα κατευθείαν στη βάση
        "image_url": "",             # δεν χρησιμοποιούμε Drive εδώ
        "notes": notes,
        "timestamp": datetime.utcnow(),
    })

    st.success("✅ Το εύρημα αποθηκεύτηκε επιτυχώς!")
    st.balloons()
