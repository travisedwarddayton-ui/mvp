import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import tempfile
import os

# ======= CONFIG =======
ORTHANC_URL = "http://localhost:8042"
ORTHANC_USER = "orthanc"
ORTHANC_PASS = "orthanc"
AUTH = HTTPBasicAuth(ORTHANC_USER, ORTHANC_PASS)

st.set_page_config(page_title="DICOM Anonymizer", page_icon="🩻", layout="centered")

st.title("🩻 DICOM Anonymizer")
st.write("Upload a DICOM file — it will be sent to the Orthanc server, anonymized, and made available for download.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file is not None:
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dcm") as tmp:
        tmp.write(uploaded_file.read())
        dicom_path = tmp.name

    st.info("Uploading to Orthanc server...")
    with open(dicom_path, "rb") as f:
        r = requests.post(
            f"{ORTHANC_URL}/instances",
            data=f,
            auth=AUTH,
            headers={"Content-Type": "application/dicom"}
        )

    if r.status_code == 200:
        instance_info = r.json()
        instance_id = instance_info["ID"]
        st.success(f"File uploaded successfully. Instance ID: {instance_id}")

        # Anonymize the instance
        st.info("Anonymizing the DICOM file...")
        anon_response = requests.post(
            f"{ORTHANC_URL}/instances/{instance_id}/anonymize",
            auth=AUTH
        )

        if anon_response.status_code == 200:
            anon_id = anon_response.json()["ID"]
            st.success("Anonymization complete!")

            # Retrieve anonymized DICOM file
            download_url = f"{ORTHANC_URL}/instances/{anon_id}/file"

            st.download_button(
                label="⬇️ Download Anonymized DICOM",
                data=requests.get(download_url, auth=AUTH).content,
                file_name="anonymized.dcm",
                mime="application/dicom"
            )
        else:
            st.error(f"Anonymization failed: {anon_response.text}")
    else:
        st.error(f"Upload failed: {r.text}")

    # Clean up temporary file
    os.remove(dicom_path)
