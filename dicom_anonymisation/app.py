import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import json

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Anonymizer", layout="centered")
st.title("🩻 DICOM Anonymizer (Hosted Version)")
st.write("Upload a DICOM file — it will be validated locally and then sent securely to your Orthanc server.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file:
    try:
        # Read DICOM bytes
        dicom_bytes = uploaded_file.read()
        dataset = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)

        # Local metadata
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

            if st.button("🚀 Upload & Anonymize"):
                st.info("Uploading to Orthanc... Please wait...")

                files = {"file": ("upload.dcm", dicom_bytes, "application/octet-stream")}

                try:
                    upload = requests.post(
                        f"{ORTHANC_URL}/instances",
                        files=files,
                        auth=AUTH,
                        timeout=60,
                        verify=False  # RunPod proxy uses HTTPS frontend, HTTP backend
                    )

                    st.write(f"🔎 Upload status: {upload.status_code}")
                    st.text("---- Raw Upload Response ----")
                    st.text(upload.text)

                    # Try to parse Orthanc response
                    try:
                        upload_json = upload.json()
                    except json.JSONDecodeError:
                        st.error("❌ Unexpected upload response (not JSON)")
                        st.text("Headers:")
                        st.json(dict(upload.headers))
                        st.text("Raw body:")
                        st.text(upload.text)
                        st.stop()

                    if upload.status_code == 200:
                        instance_id = upload_json.get("ID")
                        st.success(f"✅ Uploaded successfully — Instance ID: {instance_id}")

                        # ---- Anonymize ----
                        st.info("🔄 Anonymizing on Orthanc...")

                        anon = requests.post(
                            f"{ORTHANC_URL}/instances/{instance_id}/anonymize",
                            auth=AUTH,
                            timeout=60,
                            verify=False
                        )

                        st.write(f"Anonymize status: {anon.status_code}")
                        st.text("---- Raw Anonymize Response ----")
                        st.text(anon.text)

                        try:
                            anon_json = anon.json()
                        except json.JSONDecodeError:
                            st.error("❌ Unexpected anonymize response (not JSON)")
                            st.text("Headers:")
                            st.json(dict(anon.headers))
                            st.text("Raw body:")
                            st.text(anon.text)
                            st.stop()

                        if anon.status_code == 200:
                            anon_id = anon_json.get("ID")
                            st.success(f"🎉 Anonymization complete! ID: {anon_id}")

                            anon_file = requests.get(
                                f"{ORTHANC_URL}/instances/{anon_id}/file",
                                auth=AUTH,
                                timeout=60,
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

else:
    st.info("Please upload a DICOM (.dcm) file to begin.")
