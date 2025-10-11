import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import time
import matplotlib.pyplot as plt

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="centered")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write("Upload a DICOM file — it will be uploaded to Orthanc, cleaned using OCR anonymization, and ready for download.")

uploaded_file = st.file_uploader("Choose a DICOM file", type=["dcm"])

def show_dicom_image(dicom_bytes, title):
    """Helper to display a DICOM image."""
    try:
        ds = pydicom.dcmread(io.BytesIO(dicom_bytes))
        if hasattr(ds, "pixel_array"):
            img = ds.pixel_array
            fig, ax = plt.subplots(figsize=(4, 4))
            ax.imshow(img, cmap="gray")
            ax.set_title(title)
            ax.axis("off")
            st.pyplot(fig)
    except Exception:
        st.warning(f"⚠️ Could not display {title}")

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

        show_dicom_image(dicom_bytes, "Original DICOM")

        if st.button("🚀 Upload & Clean"):
            progress = st.progress(0, text="Uploading to Orthanc...")

            # --- Upload DICOM ---
            upload = requests.post(
                f"{ORTHANC_URL}/instances",
                data=dicom_bytes,
                headers={"Content-Type": "application/octet-stream"},
                auth=AUTH,
                verify=False
            )
            progress.progress(20, text="DICOM uploaded, triggering cleaner...")

            if upload.status_code != 200:
                st.error(f"❌ Upload failed: {upload.text}")
                st.stop()

            upload_json = upload.json()
            instance_id = upload_json.get("ID")
            st.success(f"✅ Uploaded to Orthanc: {instance_id}")

            # --- Trigger Cleaner ---
            lua_code = f'os.execute("/scripts/on_stored_instance.sh {instance_id} &")'
            trigger = requests.post(
                f"{ORTHANC_URL}/tools/execute-script",
                auth=AUTH,
                data=lua_code,
                headers={"Content-Type": "text/plain"},
                verify=False,
                timeout=10
            )
            progress.progress(40, text="Cleaner script triggered...")

            if trigger.status_code != 200:
                st.warning(f"⚠️ Could not trigger cleaner via API ({trigger.status_code})")

            # --- Poll Orthanc for cleaned DICOM ---
            cleaned_id = None
            deadline = time.time() + 180  # 3 minutes
            while time.time() < deadline:
                resp = requests.get(f"{ORTHANC_URL}/instances?expand", auth=AUTH, verify=False)
                if resp.status_code != 200:
                    continue
                instances = resp.json()
                timestamps = {i["ID"]: i.get("LastUpdate", 0) for i in instances if i["ID"] != instance_id}
                if timestamps:
                    cleaned_id = max(timestamps, key=timestamps.get)
                    orig = next((i for i in instances if i["ID"] == instance_id), None)
                    if orig and timestamps[cleaned_id] > orig.get("LastUpdate", 0):
                        break
                remaining = int(deadline - time.time())
                progress.progress(
                    min(90, int(50 + (180 - remaining) / 2)),
                    text=f"Waiting for cleaner to finish... ({remaining}s left)"
                )
                time.sleep(5)

            if not cleaned_id:
                progress.empty()
                st.warning("⚠️ No cleaned DICOM detected after timeout. Check logs.")
                st.stop()

            progress.progress(100, text="✅ Cleaning complete!")

            # --- Download cleaned DICOM ---
            anon_file = requests.get(
                f"{ORTHANC_URL}/instances/{cleaned_id}/file",
                auth=AUTH,
                verify=False
            )

            st.success(f"✅ Cleaned DICOM ready: {cleaned_id}")

            show_dicom_image(anon_file.content, "Cleaned DICOM")

            st.download_button(
                label="⬇️ Download Cleaned DICOM",
                data=anon_file.content,
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
