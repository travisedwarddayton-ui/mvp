import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import numpy as np
import time

# ===== CONFIG =====
ORTHANC_URL = "https://2x8g2wtjf1rkd8-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write("Upload a DICOM → View metadata and image → Trigger cleaning if needed")

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
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] != 3:
        arr = arr[..., :3]
    return arr


# ---------- Upload & Inspect ----------
uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file:
    dicom_bytes = uploaded_file.read()

    # ---- Preview the local file ----
    st.markdown("### 📋 Local File Header Info")
    try:
        ds = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)
        st.json({
            "Patient Name": str(getattr(ds, "PatientName", "N/A")),
            "Modality": str(getattr(ds, "Modality", "N/A")),
            "Has PixelData": hasattr(ds, "PixelData")
        })
        st.image(render_dicom(dicom_bytes), use_column_width=True, caption="🩻 Local (Before Upload)")
    except Exception as e:
        st.warning(f"⚠️ Could not read local DICOM: {e}")

    if st.button("🚀 Upload & Inspect in Orthanc"):
        with st.spinner("Uploading to Orthanc..."):
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
        st.success(f"✅ Uploaded! Instance ID: {instance_id}")

        # ---- Immediately fetch details via GET ----
        with st.spinner("Fetching metadata from Orthanc..."):
            info = requests.get(
                f"{ORTHANC_URL}/instances/{instance_id}",
                auth=AUTH,
                verify=False
            ).json()

            creation = requests.get(
                f"{ORTHANC_URL}/instances/{instance_id}/metadata/CreationDate",
                auth=AUTH,
                verify=False
            ).text.strip()

        st.markdown("### 🧠 Orthanc Instance Metadata")
        st.json({
            "Instance ID": instance_id,
            "Creation Date": creation,
            "Main DICOM Tags": info.get("MainDicomTags", {}),
            "Parent Study": info.get("ParentStudy", ""),
            "Parent Series": info.get("ParentSeries", "")
        })

        # ---- Download & Display the Orthanc version (for comparison) ----
        file_resp = requests.get(
            f"{ORTHANC_URL}/instances/{instance_id}/file",
            auth=AUTH,
            verify=False
        )
        if file_resp.status_code == 200:
            orthanc_bytes = file_resp.content
            st.image(render_dicom(orthanc_bytes), use_column_width=True, caption="🩻 Orthanc Stored Copy")
        else:
            st.warning("⚠️ Could not retrieve stored copy from Orthanc.")

        # ---- Optional: Trigger Cleaner ----
        if st.button("🧼 Trigger OCR Cleaner"):
            st.info("Running cleaner on uploaded instance...")
            lua_code = f'os.execute("/scripts/on_stored_instance.sh {instance_id} &")'
            trigger = requests.post(
                f"{ORTHANC_URL}/tools/execute-script",
                auth=AUTH,
                data=lua_code,
                headers={"Content-Type": "text/plain"},
                verify=False
            )
            if trigger.status_code == 200:
                st.success("Cleaner triggered successfully!")
            else:
                st.warning(f"Cleaner trigger failed ({trigger.status_code})")
else:
    st.info("📥 Upload a DICOM file to begin.")
