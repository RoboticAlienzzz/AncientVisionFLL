import io
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

# -----------------------------------------------------
# ΒΑΛΕ ΕΔΩ ΤΑ ΣΩΣΤΑ FOLDER IDs ΑΠΟ ΤΟ GOOGLE DRIVE
# -----------------------------------------------------
COINS_FOLDER_ID = "1T2BRWHcKAeo5ppav_XhNZDDGQMoJXwdM"
SHERDS_FOLDER_ID = "1nX5zMdQv4N5sp51424cY5DvcA4Es5es4"

# Λίγο πιο “ανοιχτό” scope για Drive
SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    info = dict(st.secrets["firebase_key"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=creds)
    return service


def upload_image_to_drive(uploaded_file, obj_type: str = "coin") -> str:
    """
    Παίρνει ένα UploadedFile από Streamlit (camera_input ή file_uploader),
    το ανεβάζει στο Google Drive στον σωστό φάκελο (coins ή sherds)
    και επιστρέφει ένα δημόσιο URL.
    """
    if uploaded_file is None:
        raise ValueError("No file provided for upload.")

    service = get_drive_service()

    folder_id = COINS_FOLDER_ID if obj_type == "coin" else SHERDS_FOLDER_ID

    file_bytes = uploaded_file.getvalue()
    file_stream = io.BytesIO(file_bytes)

    file_metadata = {
        "name": uploaded_file.name,
        "parents": [folder_id],
    }

    media = MediaIoBaseUpload(
        file_stream,
        mimetype=uploaded_file.type,
        resumable=False,  # απλό upload, όχι resumable
    )

    try:
        # 1. Upload αρχείου
        uploaded = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        file_id = uploaded["id"]

        # 2. Δίνουμε public read access
        service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
        ).execute()

        # 3. URL για εμφάνιση εικόνας
        file_url = f"https://drive.google.com/uc?id={file_id}"
        return file_url

    except HttpError as e:
        # Δείχνουμε λίγο πιο φιλικό μήνυμα στο Streamlit
        st.error(
            "⚠️ Σφάλμα κατά το ανέβασμα στο Google Drive. "
            "Έλεγξε ότι:\n"
            "- Το Google Drive API είναι ενεργό στο project\n"
            "- Το service account έχει πρόσβαση (Editor) στους φακέλους Coins/Sherds\n"
            "- Τα folder IDs στο drive_utils.py είναι σωστά."
        )
        # Για debugging μπορούσες να κάνεις print(e), αλλά στο Cloud κρύβεται.
        raise
