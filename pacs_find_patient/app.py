# federated_imaging_demo.py
import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, date
import asyncio

st.set_page_config(page_title="Federated Imaging Query Demo", layout="wide")

# -----------------------------
# Mock "Cloud" Datasets
# -----------------------------
# Cloud A (e.g., Philips) – uses 'patient_id', 'study', 'date'
CLOUD_A = [
    {"patient_id": "123", "study": "CT Thorax", "modality": "CT", "vendor": "Cloud A", "date": "2025-09-25"},
    {"patient_id": "123", "study": "CT Abdomen", "modality": "CT", "vendor": "Cloud A", "date": "2025-07-02"},
    {"patient_id": "456", "study": "MRI Brain", "modality": "MR", "vendor": "Cloud A", "date": "2025-08-16"},
    {"patient_id": "789", "study": "XR Chest", "modality": "CR", "vendor": "Cloud A", "date": "2025-06-03"},
    {"patient_id": "123", "study": "XR Chest", "modality": "CR", "vendor": "Cloud A", "date": "2025-10-01"},
]

# Cloud B (e.g., GE) – uses 'pid', 'exam', 'study_date'
CLOUD_B = [
    {"pid": "123", "exam": "CT Chest", "modality": "CT", "vendor": "Cloud B", "study_date": "2025-09-25"},
    {"pid": "123", "exam": "CT Thorax w/ contrast", "modality": "CT", "vendor": "Cloud B", "study_date": "2025-04-19"},
    {"pid": "222", "exam": "MRI Spine", "modality": "MR", "vendor": "Cloud B", "study_date": "2025-07-12"},
    {"pid": "456", "exam": "XR Shoulder", "modality": "CR", "vendor": "Cloud B", "study_date": "2025-02-21"},
    {"pid": "123", "exam": "US Abdomen", "modality": "US", "vendor": "Cloud B", "study_date": "2025-10-03"},
]

# -----------------------------
# Helper: normalizer to a common schema (FHIR-ish)
# -----------------------------
def normalize(record):
    # Handle both schemas and map to a simple common form
    patient_id = record.get("patient_id") or record.get("pid") or ""
    study      = record.get("study") or record.get("exam") or ""
    date_val   = record.get("date") or record.get("study_date") or ""
    modality   = record.get("modality") or ""
    vendor     = record.get("vendor") or "Unknown"
    return {
        "patient_id": patient_id,
        "study": study,
        "modality": modality,
        "date": date_val,
        "vendor": vendor
    }

def filter_records(records, patient_id, modality, start_date, end_date):
    out = []
    for r in records:
        n = normalize(r)
        if patient_id and n["patient_id"] != patient_id:
            continue
        if modality and n["modality"] != modality:
            continue
        if start_date or end_date:
            try:
                d = datetime.strptime(n["date"], "%Y-%m-%d").date()
                if start_date and d < start_date: continue
                if end_date and d > end_date: continue
            except Exception:
                pass
        out.append(n)
    return out

# -----------------------------
# Simulate “querying” a cloud with latency
# -----------------------------
def query_cloud_sync(cloud_name, dataset, patient_id, modality, start_date, end_date, min_delay=0.6, max_delay=1.6):
    start = time.perf_counter()
    # simulate variable network / API latency
    time.sleep(random.uniform(min_delay, max_delay))
    results = filter_records(dataset, patient_id, modality, start_date, end_date)
    elapsed = time.perf_counter() - start
    return results, elapsed

async def query_cloud_async(cloud_name, dataset, patient_id, modality, start_date, end_date, min_delay=0.6, max_delay=1.6):
    t0 = time.perf_counter()
    await asyncio.sleep(random.uniform(min_delay, max_delay))
    results = filter_records(dataset, patient_id, modality, start_date, end_date)
    elapsed = time.perf_counter() - t0
    return results, elapsed

# -----------------------------
# UI
# -----------------------------
st.title("Federated Imaging Query – Two Clouds → One Unified View")

st.markdown(
    "This demo simulates **two vendor clouds** with different schemas. "
    "We compare a **fragmented search** (run two separate queries and merge manually) "
    "vs. a **federated search** (one query, unified results)."
)

with st.expander("How this helps your video", expanded=False):
    st.markdown(
        "- Show Cloud A and Cloud B tabs (different schemas).\n"
        "- Run a fragmented search (two queries, two timers).\n"
        "- Run a federated search (one query, one timer).\n"
        "- Highlight **time saved** and **clicks reduced**.\n"
        "- Download the run metrics CSV to include real numbers in your post."
    )

st.subheader("Query")
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
with c1:
    patient_id = st.text_input("Patient ID", value="123")
with c2:
    modality = st.selectbox("Modality", options=["", "CT", "MR", "CR", "US"], index=1)
with c3:
    start_date = st.date_input("Start date", value=date(2025, 4, 1))
with c4:
    end_date = st.date_input("End date", value=date(2025, 10, 31))

st.caption("Tip: use Patient ‘123’ + Modality ‘CT’ to see overlapping studies across both clouds.")

st.markdown("---")

tabA, tabB, tabUnified, tabMetrics = st.tabs(["Cloud A (solo)", "Cloud B (solo)", "Federated (unified)", "Run Metrics"])

# State to store last metrics for download
if "run_log" not in st.session_state:
    st.session_state.run_log = []

with tabA:
    st.markdown("### Cloud A Results")
    if st.button("Query Cloud A", key="btn_a"):
        results_a, t_a = query_cloud_sync("A", CLOUD_A, patient_id, modality, start_date, end_date)
        st.success(f"Cloud A returned {len(results_a)} records in {t_a:.2f} s")
        st.dataframe(pd.DataFrame(results_a))

with tabB:
    st.markdown("### Cloud B Results")
    if st.button("Query Cloud B", key="btn_b"):
        results_b, t_b = query_cloud_sync("B", CLOUD_B, patient_id, modality, start_date, end_date)
        st.success(f"Cloud B returned {len(results_b)} records in {t_b:.2f} s")
        st.dataframe(pd.DataFrame(results_b))

with tabUnified:
    st.markdown("### Federated Query")
    cU1, cU2 = st.columns([1, 1])
    with cU1:
        parallel = st.checkbox("Parallel fan-out (async)", value=True,
                               help="Simulate querying both vendors in parallel.")
    with cU2:
        min_d = st.slider("Min latency per cloud (s)", 0.0, 2.0, 0.6, 0.1)
        max_d = st.slider("Max latency per cloud (s)", 0.2, 3.0, 1.6, 0.1)

    if st.button("Run Federated Query", key="btn_unified"):
        # Baseline: fragmented (two separate solo queries, add their times)
        results_a, t_a = query_cloud_sync("A", CLOUD_A, patient_id, modality, start_date, end_date, min_d, max_d)
        results_b, t_b = query_cloud_sync("B", CLOUD_B, patient_id, modality, start_date, end_date, min_d, max_d)
        fragmented_time = t_a + t_b

        # Federated: either parallel or serial under one call
        t0 = time.perf_counter()
        if parallel:
            # run both in parallel
            results_a2, t_a2 = asyncio.run(
                query_cloud_async("A", CLOUD_A, patient_id, modality, start_date, end_date, min_d, max_d)
            )
            results_b2, t_b2 = asyncio.run(
                query_cloud_async("B", CLOUD_B, patient_id, modality, start_date, end_date, min_d, max_d)
            )
            federated_time = time.perf_counter() - t0
            unified = results_a2 + results_b2
        else:
            # serial fan-out under one call
            results_a2, t_a2 = query_cloud_sync("A", CLOUD_A, patient_id, modality, start_date, end_date, min_d, max_d)
            results_b2, t_b2 = query_cloud_sync("B", CLOUD_B, patient_id, modality, start_date, end_date, min_d, max_d)
            federated_time = time.perf_counter() - t0
            unified = results_a2 + results_b2

        df_unified = pd.DataFrame(unified)
        df_unified = df_unified.sort_values(["date", "vendor"]).reset_index(drop=True)

        saved = max(fragmented_time - federated_time, 0)
        pct   = (saved / fragmented_time * 100) if fragmented_time > 0 else 0

        k1, k2, k3 = st.columns(3)
        k1.metric("Fragmented time (2 separate queries)", f"{fragmented_time:.2f} s")
        k2.metric("Federated time (1 query)", f"{federated_time:.2f} s")
        k3.metric("Time saved", f"{saved:.2f} s", f"{pct:.0f}%")

        st.dataframe(df_unified, use_container_width=True)

        # Log the run in session state
        st.session_state.run_log.append({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "patient_id": patient_id,
            "modality": modality,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "fragmented_time_s": round(fragmented_time, 3),
            "federated_time_s": round(federated_time, 3),
            "time_saved_s": round(saved, 3),
            "pct_saved": round(pct, 1),
            "parallel": parallel,
            "min_latency": min_d,
            "max_latency": max_d,
            "unified_count": len(df_unified),
        })

with tabMetrics:
    st.markdown("### Recorded Runs (for your video / post)")
    log_df = pd.DataFrame(st.session_state.run_log)
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True)
        st.download_button(
            "Download run metrics as CSV",
            data=log_df.to_csv(index=False).encode("utf-8"),
            file_name="federated_query_runs.csv",
            mime="text/csv"
        )
    else:
        st.info("Run a federated query to record metrics.")

st.markdown("---")
st.caption(
    "Demo notes: Cloud A and Cloud B use different field names and schemas. "
    "The federated layer normalizes them into a common structure and optionally fans out in parallel. "
    "Adjust latency sliders to simulate slower or faster vendor APIs."
)

# -----------------------------
# (Optional) How you'd plug in ChatGPT for natural-language queries
# -----------------------------
with st.expander("Optional: How to add ChatGPT orchestration (pseudo-code)"):
    st.code(
        '''
# from openai import OpenAI
# client = OpenAI(api_key="YOUR_KEY")

# nl_query = st.text_input("Ask in natural language (e.g., 'show all CT priors for 123 since June')")
# if nl_query:
#     # 1) Use GPT to parse NL to structured filters
#     parsed = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "Extract patient_id, modality, start_date, end_date from the user's question."},
#             {"role": "user", "content": nl_query}
#         ]
#     ).choices[0].message.content
#
#     # 2) Apply parsed filters to federated_query(...)
#     # 3) Use GPT again to summarize unified results in clinician-friendly prose
        ''',
        language="python"
    )
