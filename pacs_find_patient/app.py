# federated_imaging_demo_clean.py
import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, date
import asyncio

st.set_page_config(page_title="Federated Imaging Query Demo", layout="wide")

# -----------------------------
# Mock Datasets
# -----------------------------
CLOUD_A = [
    {"patient_id": "123", "study": "CT Thorax", "modality": "CT", "vendor": "Cloud A", "date": "2025-09-25"},
    {"patient_id": "123", "study": "CT Abdomen", "modality": "CT", "vendor": "Cloud A", "date": "2025-07-02"},
    {"patient_id": "456", "study": "MRI Brain", "modality": "MR", "vendor": "Cloud A", "date": "2025-08-16"},
    {"patient_id": "789", "study": "XR Chest", "modality": "CR", "vendor": "Cloud A", "date": "2025-06-03"},
    {"patient_id": "123", "study": "XR Chest", "modality": "CR", "vendor": "Cloud A", "date": "2025-10-01"},
]

CLOUD_B = [
    {"pid": "123", "exam": "CT Chest", "modality": "CT", "vendor": "Cloud B", "study_date": "2025-09-25"},
    {"pid": "123", "exam": "CT Thorax w/ contrast", "modality": "CT", "vendor": "Cloud B", "study_date": "2025-04-19"},
    {"pid": "222", "exam": "MRI Spine", "modality": "MR", "vendor": "Cloud B", "study_date": "2025-07-12"},
    {"pid": "456", "exam": "XR Shoulder", "modality": "CR", "vendor": "Cloud B", "study_date": "2025-02-21"},
    {"pid": "123", "exam": "US Abdomen", "modality": "US", "vendor": "Cloud B", "study_date": "2025-10-03"},
]

# -----------------------------
# Helper Functions
# -----------------------------
def normalize(record):
    return {
        "patient_id": record.get("patient_id") or record.get("pid"),
        "study": record.get("study") or record.get("exam"),
        "modality": record.get("modality"),
        "date": record.get("date") or record.get("study_date"),
        "vendor": record.get("vendor"),
    }

def filter_records(records, patient_id, modality, start_date, end_date):
    out = []
    for r in records:
        n = normalize(r)
        if patient_id and n["patient_id"] != patient_id:
            continue
        if modality and n["modality"] != modality:
            continue
        try:
            d = datetime.strptime(n["date"], "%Y-%m-%d").date()
            if start_date and d < start_date: continue
            if end_date and d > end_date: continue
        except Exception:
            pass
        out.append(n)
    return out

def query_cloud(dataset, patient_id, modality, start_date, end_date):
    start = time.perf_counter()
    time.sleep(random.uniform(0.4, 1.2))  # simulate network latency
    results = filter_records(dataset, patient_id, modality, start_date, end_date)
    elapsed = time.perf_counter() - start
    return results, elapsed

async def query_cloud_async(dataset, patient_id, modality, start_date, end_date):
    t0 = time.perf_counter()
    await asyncio.sleep(random.uniform(0.4, 1.2))
    results = filter_records(dataset, patient_id, modality, start_date, end_date)
    elapsed = time.perf_counter() - t0
    return results, elapsed

# -----------------------------
# UI
# -----------------------------
st.title("Federated Imaging Query Demo")

st.markdown("""
Hospitals often store imaging data across **multiple vendor clouds**.
This demo shows how a **federated query layer** can unify results instantly
without switching systems.
""")

st.subheader("Query Filters")
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
with c1:
    patient_id = st.text_input("Patient ID", value="123")
with c2:
    modality = st.selectbox("Modality", options=["", "CT", "MR", "CR", "US"], index=1)
with c3:
    start_date = st.date_input("Start date", value=date(2025, 4, 1))
with c4:
    end_date = st.date_input("End date", value=date(2025, 10, 31))

st.divider()

tabs = st.tabs(["Cloud A (separate query)", "Cloud B (separate query)", "Federated (unified query)", "Metrics"])

if "run_log" not in st.session_state:
    st.session_state.run_log = []

with tabs[0]:
    st.markdown("### Cloud A (Fragmented Search)")
    if st.button("Run Query on Cloud A"):
        results, t = query_cloud(CLOUD_A, patient_id, modality, start_date, end_date)
        st.success(f"Returned {len(results)} results in {t:.2f} seconds")
        st.dataframe(pd.DataFrame(results))

with tabs[1]:
    st.markdown("### Cloud B (Fragmented Search)")
    if st.button("Run Query on Cloud B"):
        results, t = query_cloud(CLOUD_B, patient_id, modality, start_date, end_date)
        st.success(f"Returned {len(results)} results in {t:.2f} seconds")
        st.dataframe(pd.DataFrame(results))

with tabs[2]:
    st.markdown("### Federated Query (Unified View)")
    if st.button("Run Federated Query"):
        # Fragmented baseline
        r_a, t_a = query_cloud(CLOUD_A, patient_id, modality, start_date, end_date)
        r_b, t_b = query_cloud(CLOUD_B, patient_id, modality, start_date, end_date)
        fragmented = t_a + t_b

        # Federated async
        t0 = time.perf_counter()
        r_a2, t_a2 = asyncio.run(query_cloud_async(CLOUD_A, patient_id, modality, start_date, end_date))
        r_b2, t_b2 = asyncio.run(query_cloud_async(CLOUD_B, patient_id, modality, start_date, end_date))
        federated = time.perf_counter() - t0

        unified = sorted(r_a2 + r_b2, key=lambda x: x["date"])
        df_unified = pd.DataFrame(unified)
        saved = fragmented - federated
        pct = (saved / fragmented * 100) if fragmented > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Fragmented time", f"{fragmented:.2f}s")
        c2.metric("Federated time", f"{federated:.2f}s")
        c3.metric("Time saved", f"{saved:.2f}s", f"{pct:.0f}%")

        st.dataframe(df_unified, use_container_width=True)

        st.session_state.run_log.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "patient_id": patient_id,
            "modality": modality,
            "fragmented_time_s": round(fragmented, 2),
            "federated_time_s": round(federated, 2),
            "time_saved_s": round(saved, 2),
            "pct_saved": round(pct, 1),
            "records": len(df_unified)
        })

with tabs[3]:
    st.markdown("### Recorded Runs")
    if st.session_state.run_log:
        df_log = pd.DataFrame(st.session_state.run_log)
        st.dataframe(df_log, use_container_width=True)
        st.download_button(
            "Download CSV",
            df_log.to_csv(index=False).encode("utf-8"),
            file_name="federated_query_runs.csv",
            mime="text/csv"
        )
    else:
        st.info("Run a federated query to record metrics.")

st.divider()
st.caption("Demo purpose only. Cloud A and B are mock data sources. Federated query normalizes both into a unified schema.")
