import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import json

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="DICOM Anonymizer", page_icon="🩻", layout="centered")

st.title("🩻 DICOM Anonymizer (Hosted Version)")
st.write("Upload a DICOM file — it will be validated locally and then sent securely to your Orthanc server.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file is not None:
    try:
        dicom_bytes = uploaded_file.read()
        dataset = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)

        already_anon = getattr(dataset, "PatientIdentityRemoved", "").upper() == "YES"
        has_pixels = hasattr(dataset, "PixelData")

        st.subheader("📋 Local DICOM Header Check")
        st.json({
            "Already Anonymized": already_anon,
            "Has Pixel Data": has_pixels,
            "Patient Name": str(getattr(dataset, "PatientName", "N/A")),
            "Modality": str(getattr(dataset, "Modality", "N/A")),
        })

        if already_anon:
            st.warning("⚠️ Already anonymized — skipping upload.")
        elif not has_pixels:
            st.error("❌ No PixelData found — cannot anonymize.")
        else:
            st.success("✅ Valid DICOM — ready to upload.")

            if st.button("Upload & Anonymize"):
                st.info("📤 Uploading to Orthanc...")

                files = {"file": ("upload.dcm", dicom_bytes, "application/octet-stream")}

                try:
                    upload = requests.post(
                        f"{ORTHANC_URL}/instances",
                        files=files,
                        auth=AUTH,
                        timeout=30,
                        verify=False
                    )

                    # --- Debug info ---
                    st.write(f"🔎 Upload Status: {upload.status_code}")
                    st.text(upload.text)

                    # --- Try parse JSON safely ---
                    try:
                        upload_json = upload.json()
                    except json.JSONDecodeError:
                        st.error(f"Unexpected upload response: {upload.text}")
                        st.stop()

                    if upload.status_code == 200:
                        instance_id = upload_json.get("ID")
                        st.success(f"✅ Uploaded successfully — Instance ID: {instance_id}")

                        st.info("🧩 Anonymizing instance...")
                        anon = requests.post(
                            f"{ORTHANC_URL}/instances/{instance_id}/anonymize",
                            auth=AUTH,
                            timeout=30,
                            verify=False
                        )

                        st.write(f"🔎 Anonymize Status: {anon.status_code}")
                        st.text(anon.text)

                        try:
                            anon_json = anon.json()
                        except json.JSONDecodeError:
                            st.error(f"Unexpected anonymize response: {anon.text}")
                            st.stop()

                        if anon.status_code == 200:
                            anon_id = anon_json.get("ID")
                            st.success("🎉 Anonymization complete!")

                            anon_file = requests.get(
                                f"{ORTHANC_URL}/instances/{anon_id}/file",
                                auth=AUTH,
                                timeout=30,
                                verify=False
                            )

                            st.download_button(
                                label="⬇️ Download Anonymized DICOM",
                                data=anon_file.content,
                                file_name="anonymized.dcm",
                                mime="application/dicom"
                            )
                        else:
                            st.error(f"❌ Anonymization failed: {anon.text}")

                    else:
                        st.error(f"❌ Upload failed: {upload.text}")

                except requests.exceptions.RequestException as e:
                    st.error(f"🌐 Connection error: {e}")

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")
