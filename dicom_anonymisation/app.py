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


# ---------- Helper: robust discovery of cleaned DICOM ----------
def orthanc_find_cleaned(original_instance_id, max_wait_seconds=120, poll_every=4):
    """
    Smart discovery of cleaned instance.
    Step 1️⃣  Snapshot existing instances.
    Step 2️⃣  Poll for new uploads.
    Step 3️⃣  Verify SeriesDescription = CLEANED_FROM_<original_id>.
    Step 4️⃣  Fallback to /tools/find for redundancy.
    """
    target_value = f"CLEANED_FROM_{original_instance_id}"
    deadline = time.time() + max_wait_seconds
    known_instances = set()

    try:
        existing = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
        if existing.status_code == 200:
            known_instances = set(existing.json())
    except Exception:
        pass

    while time.time() < deadline:
        # 1️⃣  Check for newly added instances
        r = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
        if r.status_code == 200:
            all_instances = set(r.json())
            new_candidates = list(all_instances - known_instances)

            for inst_id in new_candidates[-20:]:  # check only the latest uploads
                tags = requests.get(
                    f"{ORTHANC_URL}/instances/{inst_id}/simplified-tags",
                    auth=AUTH,
                    verify=False
                )
                if tags.status_code == 200:
                    series = tags.json().get("SeriesDescription", "")
                    if target_value in series:
                        st.info("🧩 Found cleaned instance via new upload list.")
                        return inst_id

        # 2️⃣  Fallback to /tools/find (sometimes Orthanc indexes slower)
        payload = {
            "Level": "Instance",
            "Expand": False,
            "Query": {"SeriesDescription": target_value}
        }
        r = requests.post(f"{ORTHANC_URL}/tools/find", auth=AUTH, json=payload, verify=False)
        if r.status_code == 200:
            try:
                ids = r.json()
                if ids:
                    st.info("📜 Found cleaned instance via /tools/find.")
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

            # --- Trigger cleaner
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

            # --- Wait and poll Orthanc
            st.info("⏳ Waiting for Orthanc to register the cleaned file...")
            cleaned_instance_id = orthanc_find_cleaned(instance_id, max_wait_seconds=180, poll_every=5)

            if not cleaned_instance_id:
                st.error("❌ Timed out waiting for cleaned instance. "
                         "Ensure the cleaner sets SeriesDescription=CLEANED_FROM_<original_id>.")
                st.stop()

            st.success(f"✅ Found cleaned instance: {cleaned_instance_id}")

            # --- Download cleaned DICOM
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
