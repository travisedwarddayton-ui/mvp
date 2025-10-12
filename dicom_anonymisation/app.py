import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import numpy as np
import uuid
import time

# ===== CONFIG =====
ORTHANC_URL = "https://pyr3wouqpxxey9-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write(
    "Upload a DICOM file → It will be uploaded to Orthanc, cleaned using OCR anonymization, "
    "and displayed side-by-side for before/after comparison."
)

# ---------- Helper: render DICOM as image ----------
def render_dicom(dicom_bytes):
    ds = pydicom.dcmread(io.BytesIO(dicom_bytes))
    arr = ds.pixel_array.astype(np.float32)
    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        arr = np.max(arr) - arr
    arr -= arr.min()
    if arr.max() > 0:
        arr /= arr.max()
    arr = (arr * 255).astype(np.uint8)
    arr = np.squeeze(arr)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] != 3:
        arr = arr[..., :3]
    return arr


# ---------- Upload & process ----------
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

        st.markdown("### 🩻 Original DICOM (Before Cleaning)")
        try:
            st.image(render_dicom(dicom_bytes), use_container_width=True, clamp=True)
        except Exception as e:
            st.warning(f"⚠️ Couldn't render original image: {e}")

        if st.button("🚀 Upload, Clean & Compare"):
            # --- Generate deterministic cleaned ID
            cleaned_id = str(uuid.uuid4())
            st.info(f"🆔 Assigned Cleaned ID: {cleaned_id}")

            # --- Upload DICOM to Orthanc
            st.info("📤 Uploading DICOM to Orthanc...")
            upload = requests.post(
                f"{ORTHANC_URL}/instances",
                data=dicom_bytes,
                headers={"Content-Type": "application/dicom"},
                auth=AUTH,
                verify=False
            )

            if upload.status_code != 200:
                st.error(f"❌ Upload failed ({upload.status_code}): {upload.text[:500]}")
                st.stop()

            try:
                upload_json = upload.json()
            except Exception:
                st.error(f"❌ Orthanc did not return valid JSON:\n\n{upload.text[:500]}")
                st.stop()

            instance_id = upload_json.get("ID")
            if not instance_id:
                st.error("❌ Upload succeeded but no 'ID' field in Orthanc response.")
                st.stop()

            st.success(f"✅ Uploaded to Orthanc: {instance_id}")

            # --- Trigger Cleaner with --cleaned-id flag
            st.info("🧠 Running OCR anonymization on Orthanc instance...")
            lua_code = f'os.execute("/scripts/on_stored_instance.sh {instance_id} --cleaned-id {cleaned_id} &")'

            trigger = requests.post(
                f"{ORTHANC_URL}/tools/execute-script",
                auth=AUTH,
                data=lua_code,
                headers={"Content-Type": "text/plain"},
                verify=False,
                timeout=10
            )

            if trigger.status_code == 200:
                st.success("🎯 Cleaner script started in background!")
            else:
                st.warning(f"⚠️ Could not trigger cleaner via API ({trigger.status_code})")

            # --- Wait briefly for Orthanc to ingest cleaned instance
            st.info("⏳ Waiting for Orthanc to receive cleaned file...")
            time.sleep(10)

            # --- Fetch the cleaned DICOM directly
            st.write(f"🔍 Fetching cleaned DICOM using known ID: {cleaned_id}")
            anon_file = requests.get(
                f"{ORTHANC_URL}/instances/{cleaned_id}/file",
                auth=AUTH,
                verify=False
            )

            # If not found yet, retry a few times
            retries = 12
            for i in range(retries):
                if anon_file.status_code == 200:
                    break
                time.sleep(5)
                st.write(f"⏱️ Waiting for cleaned instance... ({retries - i - 1}s left)")
                anon_file = requests.get(
                    f"{ORTHANC_URL}/instances/{cleaned_id}/file",
                    auth=AUTH,
                    verify=False
                )

            if anon_file.status_code != 200:
                st.error(f"❌ Cleaned file not found ({anon_file.status_code}): {anon_file.text[:200]}")
                st.stop()

            cleaned_bytes = anon_file.content
            st.success(f"✅ Cleaned DICOM retrieved successfully!")

            # --- Display comparison ---
            st.markdown("## 🔍 Visual Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Original")
                st.image(render_dicom(dicom_bytes), use_container_width=True, clamp=True)
            with col2:
                st.markdown("### Cleaned")
                st.image(render_dicom(cleaned_bytes), use_container_width=True, clamp=True)

            # --- Download cleaned DICOM ---
            st.download_button(
                label="⬇️ Download Cleaned DICOM",
                data=cleaned_bytes,
                file_name=f"cleaned_{cleaned_id}.dcm",
                mime="application/dicom"
            )

            st.json({
                "Original ID": instance_id,
                "Expected Cleaned ID": cleaned_id,
            })

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")

else:
    st.info("📥 Upload a DICOM file to begin.")
