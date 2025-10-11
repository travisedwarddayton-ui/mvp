import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import json
import time
import numpy as np

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write("Upload a DICOM file → it will be uploaded to Orthanc, cleaned using OCR anonymization, and displayed side-by-side for comparison.")

# ---- Helper: Convert DICOM pixel data to viewable image ----
def render_dicom(dicom_bytes):
    ds = pydicom.dcmread(io.BytesIO(dicom_bytes))
    arr = ds.pixel_array.astype(np.float32)

    # Handle MONOCHROME1 (inverted grayscale)
    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        arr = np.max(arr) - arr

    # Normalize 0–255
    arr -= arr.min()
    if arr.max() > 0:
        arr /= arr.max()
    arr = (arr * 255).astype(np.uint8)

    arr = np.squeeze(arr)
    if arr.ndim == 2:
        arr = np.stack([arr]*3, axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] != 3:
        arr = arr[..., :3]
    return arr

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file:
    try:
        dicom_bytes = uploaded_file.read()
        dataset = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)

        # --- Show Before Image ---
        st.subheader("🩻 Before (Original DICOM)")
        try:
            st.image(render_dicom(dicom_bytes), use_column_width=True, clamp=True)
        except Exception as e:
            st.warning(f"⚠️ Couldn't preview image: {e}")

        st.subheader("📋 DICOM Header Info")
        st.json({
            "Patient Name": str(getattr(dataset, "PatientName", "N/A")),
            "Modality": str(getattr(dataset, "Modality", "N/A")),
            "Has PixelData": hasattr(dataset, "PixelData")
        })

        if st.button("🚀 Upload, Clean & Compare"):
            st.info("📤 Uploading DICOM to Orthanc...")

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

            instance_id = upload.json().get("ID")
            st.success(f"✅ Uploaded to Orthanc: {instance_id}")

            # --- Trigger cleaner script ---
            st.info("🧠 Triggering cleaner script on Orthanc...")
            lua_code = f'os.execute("/scripts/on_stored_instance.sh {instance_id} &")'
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

            # --- Wait for cleaned version ---
            st.info("⏳ Waiting for cleaned DICOM to appear...")
            cleaned_id = None
            deadline = time.time() + 180
            orig_meta = requests.get(f"{ORTHANC_URL}/instances/{instance_id}/metadata/LastUpdate", auth=AUTH, verify=False)
            orig_ts = float(orig_meta.text) if orig_meta.status_code == 200 else 0.0

            while time.time() < deadline:
                time.sleep(5)
                resp = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
                if resp.status_code != 200:
                    continue

                timestamps = {}
                for iid in resp.json():
                    meta = requests.get(f"{ORTHANC_URL}/instances/{iid}/metadata/LastUpdate", auth=AUTH, verify=False)
                    if meta.status_code == 200:
                        try:
                            ts = float(meta.text)
                            if ts > orig_ts:
                                timestamps[iid] = ts
                        except ValueError:
                            pass

                if timestamps:
                    cleaned_id = max(timestamps, key=timestamps.get)
                    break

                st.write(f"⏱️ Checking for new cleaned file... ({int(deadline - time.time())}s left)")

            if not cleaned_id:
                st.warning("⚠️ No cleaned DICOM detected after timeout.")
                st.stop()

            st.success(f"✅ Cleaned DICOM detected: {cleaned_id}")

            # --- Download cleaned DICOM ---
            anon_file = requests.get(f"{ORTHANC_URL}/instances/{cleaned_id}/file", auth=AUTH, verify=False)
            cleaned_bytes = anon_file.content

            # --- Show After Image ---
            st.subheader("🧼 After (Cleaned DICOM)")
            try:
                st.image(render_dicom(cleaned_bytes), use_column_width=True, clamp=True)
            except Exception as e:
                st.warning(f"⚠️ Couldn't preview cleaned image: {e}")

            # --- Download Button ---
            st.download_button(
                label="⬇️ Download Cleaned DICOM",
                data=cleaned_bytes,
                file_name="cleaned.dcm",
                mime="application/dicom"
            )

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")
else:
    st.info("📥 Upload a DICOM file to begin.")
