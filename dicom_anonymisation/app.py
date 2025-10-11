import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import json
import time

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Anonymizer", layout="centered")

st.title("🩻 DICOM Anonymizer (Orthanc Cleaner)")
st.write("Upload a DICOM file — Orthanc will run the PaddleOCR cleaner and return a new anonymized version.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file:
    try:
        dicom_bytes = uploaded_file.read()
        dataset = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)

        st.subheader("📋 Local DICOM Header Check")
        st.json({
            "Patient Name": str(getattr(dataset, "PatientName", "N/A")),
            "Modality": str(getattr(dataset, "Modality", "N/A")),
            "Already Anonymized": getattr(dataset, "PatientIdentityRemoved", "").upper() == "YES",
        })

        if st.button("🚀 Upload & Trigger Cleaning"):
            st.info("Uploading to Orthanc...")

            upload = requests.post(
                f"{ORTHANC_URL}/instances",
                data=dicom_bytes,
                headers={"Content-Type": "application/octet-stream"},
                auth=AUTH,
                timeout=60,
                verify=False
            )

            if upload.status_code != 200:
                st.error(f"❌ Upload failed: {upload.text}")
                st.stop()

            upload_json = upload.json()
            instance_id = upload_json.get("ID")
            st.success(f"✅ Uploaded successfully! Instance ID: {instance_id}")
            st.info("Waiting for Orthanc cleaner to generate the anonymized version...")

            # === Wait for the new anonymized instance ===
            existing_ids = set(
                requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False).json()
            )

            new_id = None
            for _ in range(30):  # wait up to ~30s
                time.sleep(2)
                ids = set(
                    requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False).json()
                )
                diff = ids - existing_ids
                if diff:
                    new_id = diff.pop()
                    break

            if not new_id:
                st.error("❌ Timeout: Cleaner did not upload a new instance in time.")
                st.stop()

            st.success(f"🎉 Cleaned version detected! ID: {new_id}")

            anon_file = requests.get(
                f"{ORTHANC_URL}/instances/{new_id}/file",
                auth=AUTH,
                timeout=60,
                verify=False
            )

            if anon_file.status_code == 200:
                st.download_button(
                    label="⬇️ Download Cleaned DICOM",
                    data=anon_file.content,
                    file_name="cleaned.dcm",
                    mime="application/dicom"
                )
            else:
                st.error(f"❌ Failed to retrieve cleaned file: {anon_file.text}")

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")

else:
    st.info("Please upload a DICOM (.dcm) file to begin.")
