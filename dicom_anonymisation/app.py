import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import time
import numpy as np

# ===== CONFIG =====
ORTHANC_URL = "https://2x8g2wtjf1rkd8-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")
st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")

def render_dicom(dicom_bytes):
    ds = pydicom.dcmread(io.BytesIO(dicom_bytes))
    arr = ds.pixel_array.astype(np.float32)
    # Handle MONOCHROME1
    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        arr = np.max(arr) - arr
    # Normalize to 0..255
    arr -= arr.min()
    if arr.max() > 0:
        arr /= arr.max()
    arr = (arr * 255).astype(np.uint8)
    arr = np.squeeze(arr)
    # Ensure 3 channels for Streamlit
    if arr.ndim == 2:
        arr = np.stack([arr]*3, axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] != 3:
        arr = arr[..., :3]
    return arr

def get_last_update(iid):
    r = requests.get(f"{ORTHANC_URL}/instances/{iid}/metadata/LastUpdate", auth=AUTH, verify=False, timeout=15)
    if r.status_code == 200:
        try:
            return float(r.text.strip())
        except ValueError:
            return -1.0
    return -1.0

def get_latest_new_instance(exclude_id, min_ts):
    """Return the instance ID with the largest LastUpdate strictly > min_ts and != exclude_id."""
    r = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False, timeout=20)
    if r.status_code != 200:
        return None
    newest_id = None
    newest_ts = min_ts
    for iid in r.json():
        if iid == exclude_id:
            continue
        ts = get_last_update(iid)
        if ts > newest_ts:
            newest_ts = ts
            newest_id = iid
    return newest_id

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

if uploaded_file:
    try:
        dicom_bytes = uploaded_file.read()
        ds_local = pydicom.dcmread(io.BytesIO(dicom_bytes), stop_before_pixels=False)

        st.subheader("📋 DICOM Header (Local)")
        st.json({
            "Patient Name": str(getattr(ds_local, "PatientName", "N/A")),
            "Modality": str(getattr(ds_local, "Modality", "N/A")),
            "Has PixelData": hasattr(ds_local, "PixelData")
        })

        st.markdown("### 🩻 Original (before)")
        try:
            st.image(render_dicom(dicom_bytes), use_column_width=True, clamp=True)
        except Exception as e:
            st.warning(f"Could not render original image: {e}")

        if st.button("🚀 Upload, Clean & Compare"):
            st.info("📤 Uploading to Orthanc...")
            up = requests.post(
                f"{ORTHANC_URL}/instances",
                data=dicom_bytes,
                headers={"Content-Type": "application/octet-stream"},
                auth=AUTH,
                verify=False,
                timeout=60
            )
            if up.status_code != 200:
                st.error(f"Upload failed: {up.text}")
                st.stop()

            instance_id = up.json().get("ID")
            st.success(f"Uploaded instance: {instance_id}")

            # Original timestamp
            orig_ts = get_last_update(instance_id)
            st.write(f"Original LastUpdate: {orig_ts}")

            # Try to trigger your cleaner (non-fatal if it fails)
            lua = f'os.execute("/scripts/on_stored_instance.sh {instance_id} &")'
            trig = requests.post(
                f"{ORTHANC_URL}/tools/execute-script",
                auth=AUTH,
                data=lua,
                headers={"Content-Type": "text/plain"},
                verify=False,
                timeout=10
            )
            if trig.status_code == 200:
                st.success("Cleaner script triggered.")
            else:
                st.warning(f"Cleaner trigger returned {trig.status_code}. Will still poll for result.")

            # Poll for newest instance by LastUpdate
            st.info("⏳ Waiting for cleaned DICOM (up to 3 minutes)...")
            cleaned_id = None
            deadline = time.time() + 180
            while time.time() < deadline:
                time.sleep(5)
                candidate = get_latest_new_instance(exclude_id=instance_id, min_ts=orig_ts)
                if candidate:
                    cleaned_id = candidate
                    break
                remaining = int(deadline - time.time())
                st.write(f"⏱️ Checking for cleaned file... ({remaining}s left)")

            if not cleaned_id:
                st.warning("No cleaned DICOM detected within timeout.")
                st.stop()

            st.success(f"Cleaned instance: {cleaned_id}")

            # Download & render cleaned
            file_resp = requests.get(f"{ORTHANC_URL}/instances/{cleaned_id}/file", auth=AUTH, verify=False, timeout=60)
            if file_resp.status_code != 200:
                st.error(f"Could not download cleaned file: {file_resp.text}")
                st.stop()
            cleaned_bytes = file_resp.content

            st.markdown("## 🔍 Visual Comparison")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Before")
                st.image(render_dicom(dicom_bytes), use_column_width=True, clamp=True)
            with c2:
                st.markdown("### After")
                st.image(render_dicom(cleaned_bytes), use_column_width=True, clamp=True)

            st.download_button(
                "⬇️ Download Cleaned DICOM",
                data=cleaned_bytes,
                file_name="cleaned.dcm",
                mime="application/dicom"
            )

            st.json({
                "Original ID": instance_id,
                "Cleaned ID": cleaned_id
            })

    except Exception as e:
        st.error(f"Invalid DICOM file: {e}")
else:
    st.info("📥 Upload a DICOM file to begin.")
