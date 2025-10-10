import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="DICOM Anonymizer", page_icon="🩻", layout="centered")

st.title("🩻 DICOM Anonymizer (Hosted Version)")
st.write("Upload a DICOM file — it will be validated locally and then sent securely to your Orthanc server.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file is not None:
    try:
        # Read entire file into memory
        dicom_bytes = uploaded_file.read()
        buffer = io.BytesIO(dicom_bytes)

        # Validate locally with pydicom
        dataset = pydicom.dcmread(buffer, stop_before_pixels=False)
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
                try:
                    st.info("Uploading to Orthanc (please wait)...")

                    # Streamlit hosted fix: re-wrap bytes in new BytesIO each time
                    files = {"file": ("upload.dcm", dicom_bytes, "application/dicom")}

                    r = requests.post(
                        f"{ORTHANC_URL}/instances",
                        files=files,
                        auth=AUTH,
                        timeout=30,
                        verify=False
                    )
                    
                    st.write(f"Status: {r.status_code}")
                    st.text(r.text)


                    if r.status_code == 200:
                        instance_id = r.json()["ID"]
                        st.success(f"Uploaded successfully. Instance ID: {instance_id}")

                        st.info("Anonymizing...")
                        anon_response = requests.post(
                            f"{ORTHANC_URL}/instances/{instance_id}/anonymize",
                            auth=AUTH,
                            timeout=30,
                            verify=True
                        )

                        if anon_response.status_code == 200:
                            anon_id = anon_response.json()["ID"]
                            st.success("🎉 Anonymization complete!")

                            anon_file = requests.get(
                                f"{ORTHANC_URL}/instances/{anon_id}/file",
                                auth=AUTH,
                                timeout=30,
                                verify=True
                            )

                            st.download_button(
                                label="⬇️ Download Anonymized DICOM",
                                data=anon_file.content,
                                file_name="anonymized.dcm",
                                mime="application/dicom"
                            )
                        else:
                            st.error(f"Anonymization failed: {anon_response.text}")
                    else:
                        st.error(f"Upload failed: {r.text}")

                except requests.exceptions.RequestException as e:
                    st.error(f"🌐 Connection error: {e}")

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")
