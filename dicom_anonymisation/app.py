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

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="centered")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write("Upload a DICOM file → it will be uploaded to Orthanc and automatically cleaned using OCR anonymization.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file:
    try:
        dicom_bytes = uploaded_file.read()
        dataset = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)

        st.subheader("📋 DICOM Header Info")
        st.json({
            "Patient Name": str(getattr(dataset, "PatientName", "N/A")),
            "Modality": str(getattr(dataset, "Modality", "N/A")),
            "Has PixelData": hasattr(dataset, "PixelData")
        })

        if st.button("🚀 Upload & Clean"):
            st.info("Uploading to Orthanc...")

            upload = requests.post(
                f"{ORTHANC_URL}/instances",
                data=dicom_bytes,
                headers={"Content-Type": "application/octet-stream"},
                auth=AUTH,
                verify=False
            )

            if upload.status_code != 200:
                st.error(f"❌ Upload failed: {upload.text}")
                st.stop()

            upload_json = upload.json()
            instance_id = upload_json.get("ID")
            st.success(f"✅ Uploaded to Orthanc: {instance_id}")

            # --- Trigger Cleaner ---
            st.info("🧠 Running OCR anonymization on Orthanc instance...")
            
            lua_code = f'os.execute("/scripts/on_stored_instance.sh {instance_id} &")'


            trigger = requests.post(
                f"{ORTHANC_URL}/tools/execute-script",
                auth=AUTH,
                data=lua_code,
                headers={"Content-Type": "text/plain"},
                verify=False
            )

            if trigger.status_code == 200:
                st.success("🎯 Cleaner script executed successfully!")
            else:
                st.warning(f"⚠️ Could not trigger cleaner via API ({trigger.status_code})")

            # --- Poll Orthanc for new anonymized image ---
            st.info("⏳ Waiting for cleaned DICOM to appear in Orthanc...")

            time.sleep(10)  # give Orthanc time to process

            instances = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
            if instances.status_code == 200:
                all_instances = instances.json()
                if len(all_instances) > 1:
                    latest_id = all_instances[-1]
                    st.success(f"✅ Cleaned DICOM ready: {latest_id}")

                    # Download the cleaned file
                    anon_file = requests.get(
                        f"{ORTHANC_URL}/instances/{latest_id}/file",
                        auth=AUTH,
                        verify=False
                    )

                    st.download_button(
                        label="⬇️ Download Cleaned DICOM",
                        data=anon_file.content,
                        file_name="cleaned.dcm",
                        mime="application/dicom"
                    )
                else:
                    st.warning("No new cleaned DICOM detected yet.")
            else:
                st.error("❌ Failed to list Orthanc instances")

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")
else:
    st.info("Upload a DICOM file to begin.")
