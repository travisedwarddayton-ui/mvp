import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import json
import time
import numpy as np
import cv2

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write("Upload a DICOM file → it will be uploaded to Orthanc, cleaned using OCR anonymization, and displayed side-by-side for comparison.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

# Helper: render DICOM pixel data as image
def render_dicom(dicom_bytes):
    ds = pydicom.dcmread(io.BytesIO(dicom_bytes))
    pixel_array = ds.pixel_array.astype(np.float32)
    img = cv2.normalize(pixel_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img

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

        if st.button("🚀 Upload, Clean & Compare"):
            st.info("📤 Uploading DICOM to Orthanc...")

            # Upload to Orthanc
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

            # Trigger cleaner
            st.info("🧠 Running OCR anonymization on Orthanc instance...")
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

            # Wait for cleaned file
            st.info("⏳ Waiting for cleaned DICOM to appear in Orthanc...")
            cleaned_id = None
            deadline = time.time() + 180
            orig_meta = requests.get(f"{ORTHANC_URL}/instances/{instance_id}/metadata/LastUpdate", auth=AUTH, verify=False)
            orig_ts = float(orig_meta.text) if orig_meta.status_code == 200 else 0.0

            while time.time() < deadline:
                time.sleep(5)
                resp = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
                if resp.status_code != 200:
                    continue

                all_ids = resp.json()
                timestamps = {}
                for iid in all_ids:
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

            # Fetch cleaned DICOM
            st.success(f"✅ Cleaned DICOM detected: {cleaned_id}")
            anon_file = requests.get(
                f"{ORTHANC_URL}/instances/{cleaned_id}/file",
                auth=AUTH,
                verify=False
            )

            cleaned_bytes = anon_file.content

            # ---- Display Comparison ----
            st.markdown("## 🩻 Visual Comparison")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Original DICOM")
                st.image(render_dicom(dicom_bytes), use_column_width=True)

            with col2:
                st.markdown("### Cleaned DICOM")
                try:
                    st.image(render_dicom(cleaned_bytes), use_column_width=True)
                except Exception as e:
                    st.error(f"⚠️ Unable to visualize cleaned DICOM: {e}")

            # ---- Download cleaned file ----
            st.download_button(
                label="⬇️ Download Cleaned DICOM",
                data=cleaned_bytes,
                file_name="cleaned.dcm",
                mime="application/dicom"
            )

            st.json({
                "Original ID": instance_id,
                "Cleaned ID": cleaned_id
            })

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")

else:
    st.info("📥 Upload a DICOM file to begin.")
