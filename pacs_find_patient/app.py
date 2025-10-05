# federated_imaging_demo_radiology.py
import streamlit as st
import pandas as pd
import time, random, asyncio
from datetime import datetime, date

st.set_page_config(page_title="Unified Imaging Query Demo", layout="wide")

# ------------------------------------------------------------------
# Mock data from two vendor PACS clouds
# ------------------------------------------------------------------
PHILIPS_CLOUD = [
    {"patient_id": "123", "study": "CT Thorax", "modality": "CT", "vendor": "Philips Imaging Cloud", "date": "2025-09-25"},
    {"patient_id": "123", "study": "CT Abdomen", "modality": "CT", "vendor": "Philips Imaging Cloud", "date": "2025-07-02"},
    {"patient_id": "456", "study": "MRI Brain", "modality": "MR", "vendor": "Philips Imaging Cloud", "date": "2025-08-16"},
]

GE_CLOUD = [
    {"pid": "123", "exam": "CT Chest", "modality": "CT", "vendor": "GE Health Cloud", "study_date": "2025-09-25"},
    {"pid": "123", "exam": "CT Thorax w/ contrast", "modality": "CT", "vendor": "GE Health Cloud", "study_date": "2025-04-19"},
    {"pid": "456", "exam": "XR Shoulder", "modality": "CR", "vendor": "GE Health Cloud", "study_date": "2025-02-21"},
]

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def normalize(record):
    """Map Philips + GE schemas into one unified schema."""
    return {
        "patient_id": record.get("patient_id") or record.get("pid"),
        "study": record.get("study") or record.get("exam"),
        "modality": record.get("modality"),
        "date": record.get("date") or record.get("study_date"),
        "vendor": record.get("vendor"),
    }

def filter_records(records, patient_id, modality, start, end):
    out = []
    for r in records:
        n = normalize(r)
        if patient_id and n["patient_id"] != patient_id:
            continue
        if modality and n["modality"] != modality:
            continue
        try:
            d = datetime.strptime(n["date"], "%Y-%m-%d").date()
            if start and d < start: continue
            if end and d > end: continue
        except: pass
        out.append(n)
    return out

def query_cloud(dataset, patient_id, modality, start, end):
    t0 = time.perf_counter()
    time.sleep(random.uniform(0.4, 1.2))   # simulate vendor latency
    res = filter_records(dataset, patient_id, modality, start, end)
    return res, time.perf_counter() - t0

async def query_cloud_async(dataset, patient_id, modality, start, end):
    t0 = time.perf_counter()
    await asyncio.sleep(random.uniform(0.4, 1.2))
    res = filter_records(dataset, patient_id, modality, start, end)
    return res, time.perf_counter() - t0

# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------
st.title("Unified Imaging Query Demo")
st.markdown("""
Radiologists often need to **search multiple PACS or vendor portals** (Philips, GE, Siemens …)  
just to find prior studies for a single patient.  
This demo shows how a **federated query layer** can bring them together in one place.
""")

# Query controls
c1, c2, c3, c4 = st.columns([1.2,1,1,1])
with c1: patient_id = st.text_input("Patient ID", value="123")
with c2: modality   = st.selectbox("Modality", ["","CT","MR","CR"], index=1)
with c3: start_date = st.date_input("From", value=date(2025,4,1))
with c4: end_date   = st.date_input("To",   value=date(2025,10,31))

st.divider()

tabs = st.tabs(["Philips Portal", "GE Portal", "Unified View", "Metrics"])
if "run_log" not in st.session_state: st.session_state.run_log = []

# ------------------------------------------------------------------
# Philips
# ------------------------------------------------------------------
with tabs[0]:
    st.subheader("Philips Imaging Cloud (separate query)")
    if st.button("Find Priors in Philips"):
        res, t = query_cloud(PHILIPS_CLOUD, patient_id, modality, start_date, end_date)
        st.success(f"Found {len(res)} studies in {t:.2f}s")
        st.dataframe(pd.DataFrame(res))

# ------------------------------------------------------------------
# GE
# ------------------------------------------------------------------
with tabs[1]:
    st.subheader("GE Health Cloud (separate query)")
    if st.button("Find Priors in GE"):
        res, t = query_cloud(GE_CLOUD, patient_id, modality, start_date, end_date)
        st.success(f"Found {len(res)} studies in {t:.2f}s")
        st.dataframe(pd.DataFrame(res))

# ------------------------------------------------------------------
# Unified Federated Query
# ------------------------------------------------------------------
with tabs[2]:
    st.subheader("Federated Query – Unified Patient View")
    if st.button("Run Unified Query"):
        # Baseline: separate lookups
        rA, tA = query_cloud(PHILIPS_CLOUD, patient_id, modality, start_date, end_date)
        rB, tB = query_cloud(GE_CLOUD,      patient_id, modality, start_date, end_date)
        fragmented = tA + tB

        # Federated: parallel fan-out
        t0 = time.perf_counter()
        rA2, tA2 = asyncio.run(query_cloud_async(PHILIPS_CLOUD, patient_id, modality, start_date, end_date))
        rB2, tB2 = asyncio.run(query_cloud_async(GE_CLOUD,      patient_id, modality, start_date, end_date))
        federated = time.perf_counter() - t0

        unified = sorted(rA2 + rB2, key=lambda x: x["date"])
        df = pd.DataFrame(unified)
        saved = fragmented - federated
        pct   = (saved/fragmented*100) if fragmented>0 else 0

        k1,k2,k3 = st.columns(3)
        k1.metric("Two separate portals", f"{fragmented:.2f}s")
        k2.metric("Unified query time",   f"{federated:.2f}s")
        k3.metric("Time saved", f"{saved:.2f}s", f"{pct:.0f}%")

        st.dataframe(df, use_container_width=True)
        st.session_state.run_log.append({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "patient_id": patient_id,
            "modality": modality,
            "fragmented_s": round(fragmented,2),
            "federated_s": round(federated,2),
            "saved_s": round(saved,2),
            "pct_saved": round(pct,1),
            "records": len(df)
        })

# ------------------------------------------------------------------
# Metrics log
# ------------------------------------------------------------------
with tabs[3]:
    st.subheader("Recorded Runs")
    log = pd.DataFrame(st.session_state.run_log)
    if not log.empty:
        st.dataframe(log, use_container_width=True)
        st.download_button("Download CSV",
                           log.to_csv(index=False).encode(),
                           "federated_query_runs.csv","text/csv")
    else:
        st.info("Run a unified query to log results.")

st.divider()
st.caption("Demo only. Philips & GE datasets are simulated. The unified query normalizes both into one FHIR-like schema.")
