import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pydicom
import io
import json
import time

# ===== CONFIG =====
ORTHANC_URL = "https://mwyksr0jwqlfxm-8042.proxy.runpod.net"
AUTH = HTTPBasicAuth("orthanc", "orthanc")

st.set_page_config(page_title="🩻 DICOM Cleaner", layout="centered")

st.title("🩻 DICOM Cleaner (Orthanc + PaddleOCR)")
st.write("Upload a DICOM file → it will be uploaded to Orthanc and automatically cleaned using OCR anonymization.")

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

        if st.button("🚀 Upload & Clean"):
            st.info("📤 Uploading DICOM to Orthanc...")

            # --- Record existing instance IDs before upload ---
            pre_upload_resp = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
            pre_existing_ids = set(pre_upload_resp.json()) if pre_upload_resp.status_code == 200 else set()

            # --- Upload new DICOM ---
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

            # --- Trigger Cleaner ---
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

            # --- Poll Orthanc for new anonymized image ---
            st.info("⏳ Waiting for cleaned DICOM to appear in Orthanc...")

            cleaned_id = None
            deadline = time.time() + 180  # wait up to 3 minutes

            while time.time() < deadline:
                time.sleep(5)
                resp = requests.get(f"{ORTHANC_URL}/instances", auth=AUTH, verify=False)
                if resp.status_code != 200:
                    continue
                
                all_ids = resp.json()
                # Filter out the original one
                candidate_ids = [iid for iid in all_ids if iid != instance_id]
                
                # Query timestamps for each candidate
                timestamps = {}
                for iid in candidate_ids:
                    meta = requests.get(f"{ORTHANC_URL}/instances/{iid}/metadata/LastUpdate", auth=AUTH, verify=False)
                    if meta.status_code == 200:
                        timestamps[iid] = float(meta.text)

                        except ValueError:
                            pass

                if timestamps:
                    cleaned_id = max(timestamps, key=timestamps.get)
                    # Double check it's newer than the uploaded one
                    orig_meta = requests.get(f"{ORTHANC_URL}/instances/{instance_id}/metadata/LastUpdate", auth=AUTH, verify=False)
                    if orig_meta.status_code == 200:
                        try:
                            if timestamps[cleaned_id] > float(orig_meta.text):
                                break
                        except ValueError:
                            pass

                st.write(f"⏱️ Checking for new cleaned file... ({int(deadline - time.time())}s left)")

            st.write(f"🕓 Checked {len(timestamps)} instances.")

            if cleaned_id:
                st.success(f"✅ Cleaned DICOM detected: {cleaned_id}")

                anon_file = requests.get(
                    f"{ORTHANC_URL}/instances/{cleaned_id}/file",
                    auth=AUTH,
                    verify=False
                )

                st.download_button(
                    label="⬇️ Download Cleaned DICOM",
                    data=anon_file.content,
                    file_name="cleaned.dcm",
                    mime="application/dicom"
                )

                st.json({
                    "Original ID": instance_id,
                    "Cleaned ID": cleaned_id,
                    "Time Difference (s)": round(timestamps[cleaned_id] - float(orig_meta.text), 2)
                })

            else:
                st.warning("⚠️ No cleaned DICOM detected after timeout. Check container logs.")

    except Exception as e:
        st.error(f"⚠️ Invalid DICOM file: {e}")

else:
    st.info("📥 Upload a DICOM file to begin.")
