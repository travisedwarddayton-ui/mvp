import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import time
import numpy as np
from datetime import datetime

# ===== CONFIG =====
ORTHANC_URL = "https://2x8g2wtjf1rkd8-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write(
    "Upload a DICOM file → it will be uploaded to Orthanc, cleaned using OCR anonymization, "
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
            st.image(render_dicom(dicom_bytes), use_column_width=True, clamp=True)
        except Exception as e:
            st.warning(f"⚠️ Couldn't render original image: {e}")

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

            # --- Get creation date of uploaded instance ---
            orig_meta = requests.get(
                f"{ORTHANC_URL}/instances/{instance_id}/metadata/CreationDate",
                auth=AUTH, verify=False
            )
            orig_date_str = orig_meta.text.strip() if orig_meta.status_code == 200 else ""
            orig_date = datetime.strptime(orig_date_str, "%Y%m%dT%H%M%S") if orig_date_str else datetime.now()
            st.write(f"🕒 Original instance CreationDate: {orig_date}")

            # --- Trigger cleaner ---
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

            # --- Poll Orthanc for cleaned file ---
            st.info("⏳ Waiting for cleaned DICOM to appear (max 3 min)...")
            cleaned_id = None
            deadline = time.time() + 180

            while time.time() < deadline:
                time.sleep(5)
                resp = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
                if resp.status_code != 200:
                    continue

                ids = resp.json()
                candidates = {}
                for iid in ids:
                    meta = requests.get(
                        f"{ORTHANC_URL}/instances/{iid}/metadata/CreationDate",
                        auth=AUTH, verify=False
                    )
                    if meta.status_code == 200:
                        try:
                            ts_str = meta.text.strip()
                            ts = datetime.strptime(ts_str, "%Y%m%dT%H%M%S")
                            if ts > orig_date:
                                candidates[iid] = ts
                        except Exception:
                            pass

                if candidates:
                    cleaned_id = max(candidates, key=candidates.get)
                    if cleaned_id != instance_id:
                        st.write(f"🆕 Detected new cleaned instance: {cleaned_id}")
                        break

                st.write(f"⏱️ Checking for cleaned file... ({int(deadline - time.time())}s left)")

            if not cleaned_id:
                st.warning("⚠️ No cleaned DICOM detected after timeout.")
                st.stop()

            st.success(f"✅ Cleaned DICOM detected: {cleaned_id}")

            # --- Download the cleaned DICOM ---
            anon_file = requests.get(
                f"{ORTHANC_URL}/instances/{cleaned_id}/file", auth=AUTH, verify=False
            )
            cleaned_bytes = anon_file.content

            # --- Display side-by-side comparison ---
            st.markdown("## 🔍 Visual Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Original")
                st.image(render_dicom(dicom_bytes), use_column_width=True, clamp=True)
            with col2:
                st.markdown("### Cleaned")
                st.image(render_dicom(cleaned_bytes), use_column_width=True, clamp=True)

            # --- Download cleaned DICOM ---
            st.download_button(
                label="⬇️ Download Cleaned DICOM",
                data=cleaned_bytes,
                file_name="cleaned.dcm",
                mime="application/dicom"
            )

            st.json({
                "Original ID": instance_id,
                "Cleaned ID": cleaned_id,
                "Original CreationDate": orig_date_str
            })

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")

else:
    st.info("📥 Upload a DICOM file to begin.")
