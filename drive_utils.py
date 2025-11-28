import io
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# ----------------------------------------
# ΡΥΘΜΙΣΗ: βάλε εδώ τα IDs των φακέλων σου στο Google Drive
# ----------------------------------------
COINS_FOLDER_ID = "1T2BRWHcKAeo5ppav_XhNZDDGQMoJXwdM"
SHERDS_FOLDER_ID = "1nX5zMdQv4N5sp51424cY5DvcA4Es5es4"

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_drive_service():
    """
    Δημιουργεί ένα Google Drive service χρησιμοποιώντας το ίδιο service account
    που βάλαμε στα secrets (firebase_key).
    """
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
    και επιστρέφει ένα δημόσιο URL για χρήση στο app.
    """
    if uploaded_file is None:
        raise ValueError("No file provided for upload.")

    service = get_drive_service()

    # Επιλογή σωστού folder ανάλογα με τον τύπο
    folder_id = COINS_FOLDER_ID if obj_type == "coin" else SHERDS_FOLDER_ID

    # Διαβάζουμε τα bytes του αρχείου
    file_bytes = uploaded_file.getvalue()
    file_stream = io.BytesIO(file_bytes)

    file_metadata = {
        "name": uploaded_file.name,
        "parents": [folder_id],
    }

    media = MediaIoBaseUpload(
        file_stream,
        mimetype=uploaded_file.type,
        resumable=True,
    )

    # Ανεβάζουμε το αρχείο
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    file_id = uploaded["id"]

    # Δίνουμε δικαίωμα "anyone with the link"
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    # Direct link για χρήση στις εικόνες
    file_url = f"https://drive.google.com/uc?id={file_id}"
    return file_url
