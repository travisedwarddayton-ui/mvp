import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import numpy as np
import time
import json

# ===== CONFIG =====
ORTHANC_URL = "https://pyr3wouqpxxey9-8042.proxy.runpod.net"  # remote Orthanc
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="wide")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write(
    "Upload a DICOM → it’s uploaded to remote Orthanc, a remote cleaner runs on that node, "
    "and we fetch the cleaned file back from Orthanc."
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


# ---------- Helper: find cleaned DICOM via metadata or fallback ----------
def orthanc_find_cleaned(original_instance_id, max_wait_seconds=60, poll_every=3):
    """
    Poll Orthanc for the cleaned instance.
    Step 1: Iterate recent instances and check Metadata[1000] == original_instance_id
    Step 2: Fallback to SeriesDescription == f"CLEANED_FROM_{original_instance_id}"
    """
    deadline = time.time() + max_wait_seconds

    while time.time() < deadline:
        try:
            # --- Step 1: List instances ---
            r = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
            if r.status_code == 200:
                instance_ids = r.json()

                # Check metadata of each instance
                for inst_id in instance_ids[-30:]:  # only check most recent 30 for speed
                    meta = requests.get(f"{ORTHANC_URL}/instances/{inst_id}/metadata", auth=AUTH, verify=False)
                    if meta.status_code == 200:
                        meta_keys = meta.json()
                        if "1000" in meta_keys:
                            val_resp = requests.get(f"{ORTHANC_URL}/instances/{inst_id}/metadata/1000",
                                                    auth=AUTH, verify=False)
                            if val_resp.status_code == 200:
                                val = val_resp.text.strip().strip('"')
                                if val == original_instance_id:
                                    st.info("🔗 Found cleaned instance via metadata linkage.")
                                    return inst_id
        except Exception as e:
            st.warning(f"⚠️ Metadata lookup error: {e}")

        # --- Step 2: Fallback to SeriesDescription ---
        payload_series = {
            "Level": "Instance",
            "Expand": False,
            "Query": {
                "SeriesDescription": f"CLEANED_FROM_{original_instance_id}"
            }
        }
        r = requests.post(f"{ORTHANC_URL}/tools/find", auth=AUTH, json=payload_series, verify=False)
        if r.status_code == 200:
            try:
                ids = r.json()
                if ids:
                    st.info("📜 Found cleaned instance via SeriesDescription fallback.")
                    return ids[0]
            except Exception:
                pass

        time.sleep(poll_every)

    return None


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
            # --- Upload to remote Orthanc
            st.info("📤 Uploading to Orthanc...")
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

            # --- Trigger cleaner on the remote node via Lua
            st.info("🧠 Running OCR anonymization on the remote Orthanc node...")
            lua_code = f'os.execute("/scripts/clean_dicom_image_gpu.py {instance_id} &")'
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
                st.warning(f"⚠️ Could not trigger cleaner via API ({trigger.status_code}): {trigger.text[:300]}")

            # --- Poll Orthanc to discover the new cleaned instance
            st.info("⏳ Waiting for cleaned instance to appear...")
            cleaned_instance_id = orthanc_find_cleaned(instance_id, max_wait_seconds=120, poll_every=4)

            if not cleaned_instance_id:
                st.error("❌ Timed out waiting for cleaned instance. "
                         "Ensure the cleaner sets Metadata[1000]=<original_id> or SeriesDescription=CLEANED_FROM_<original_id>.")
                st.stop()

            st.success(f"✅ Found cleaned instance: {cleaned_instance_id}")

            # --- Download the cleaned DICOM from Orthanc
            anon_file = requests.get(
                f"{ORTHANC_URL}/instances/{cleaned_instance_id}/file",
                auth=AUTH,
                verify=False
            )
            if anon_file.status_code != 200:
                st.error(f"❌ Failed to download cleaned DICOM ({anon_file.status_code}): {anon_file.text[:300]}")
                st.stop()

            cleaned_bytes = anon_file.content

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
                file_name=f"cleaned_{cleaned_instance_id}.dcm",
                mime="application/dicom"
            )

            # --- Show IDs ---
            st.json({
                "Original ID": instance_id,
                "Cleaned ID": cleaned_instance_id
            })

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")

else:
    st.info("📥 Upload a DICOM file to begin.")
