import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import numpy as np
import subprocess
import json
import os
import tempfile

# ===== CONFIG =====
ORTHANC_URL = "http://127.0.0.1:8042"   # Orthanc is local inside container
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write(
    "Upload a DICOM → it’s sent to Orthanc, cleaned via PaddleOCR anonymization, "
    "and both versions are shown side-by-side."
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
            st.info("📤 Uploading to Orthanc...")
            upload = requests.post(
                f"{ORTHANC_URL}/instances",
                data=dicom_bytes,
                headers={"Content-Type": "application/dicom"},
                auth=AUTH,
                verify=False
            )

            if upload.status_code != 200:
                st.error(f"❌ Upload failed ({upload.status_code}): {upload.text[:300]}")
                st.stop()

            try:
                upload_json = upload.json()
                instance_id = upload_json["ID"]
            except Exception:
                st.error(f"❌ Invalid response from Orthanc:\n\n{upload.text[:500]}")
                st.stop()

            st.success(f"✅ Uploaded to Orthanc — Instance ID: {instance_id}")
            st.info("🧠 Running PaddleOCR Cleaner...")

            # Run the cleaner script synchronously and capture its JSON output
            try:
                proc = subprocess.run(
                    ["python3", "/scripts/clean_dicom_image_gpu.py", instance_id],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            except subprocess.TimeoutExpired:
                st.error("⏱️ Cleaner timed out after 5 minutes.")
                st.stop()

            if proc.returncode != 0:
                st.error(f"Cleaner error:\n{proc.stderr or proc.stdout}")
                st.stop()

            # Parse JSON output from cleaner
            try:
                result = json.loads(proc.stdout.strip().splitlines()[-1])
            except Exception as e:
                st.error(f"Failed to parse cleaner output:\n\n{proc.stdout}\n\nError: {e}")
                st.stop()

            local_cleaned_path = result.get("local_cleaned_path")
            orthanc_id = result.get("orthanc_id")
            st.success("✅ Cleaner finished successfully!")

            # Load cleaned bytes from the saved path
            if not os.path.exists(local_cleaned_path):
                st.error(f"Cleaned file not found at: {local_cleaned_path}")
                st.stop()

            with open(local_cleaned_path, "rb") as f:
                cleaned_bytes = f.read()

            # --- Visual comparison ---
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
                file_name=os.path.basename(local_cleaned_path),
                mime="application/dicom"
            )

            # --- Summary info ---
            st.json({
                "Original Orthanc ID": instance_id,
                "New Orthanc ID": orthanc_id,
                "Local Cleaned Path": local_cleaned_path
            })

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")
else:
    st.info("📥 Upload a DICOM file to begin.")
