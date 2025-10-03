# Imaging Operations Control Tower – Streamlit MVP (Now with Patient Discovery)

import datetime as dt
import random
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Imaging Ops Control Tower", layout="wide")

# ------------------------------------------------------------
# Synthetic Data
# ------------------------------------------------------------
SITES = ["Main Campus", "North Clinic", "East Outpatient", "West Oncology"]
MODALITIES = ["CT", "MRI", "XR", "US", "PET", "MG"]

def generate_machine_inventory(n=10):
    rows = []
    for i in range(n):
        rows.append({
            "machine_id": f"M{i:03d}",
            "modality": random.choice(MODALITIES),
            "site": random.choice(SITES),
        })
    return pd.DataFrame(rows)

def generate_exam_history(inv_df, days=90):
    recs = []
    start = dt.date.today() - dt.timedelta(days=days)
    for _, m in inv_df.iterrows():
        for d in range(days):
            date = start + dt.timedelta(days=d)
            for i in range(random.randint(0, 5)):
                patient_id = f"P{random.randint(1000,9999)}"
                patient_name = random.choice(["Smith", "Garcia", "Khan", "Ivanova", "Lee"]) + \
                               ", " + random.choice(["John", "Maria", "Ali", "Anna", "Wei"])
                recs.append({
                    "exam_id": f"E{m.machine_id}-{date}-{i}",
                    "date": pd.to_datetime(date),
                    "site": m.site,
                    "machine_id": m.machine_id,
                    "modality": m.modality,
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "accession": f"ACC{random.randint(10000,99999)}",
                })
    return pd.DataFrame(recs)

@st.cache_data
def load_data():
    inv = generate_machine_inventory(20)
    ex = generate_exam_history(inv, 150)
    return inv, ex

inv_df, exams_df = load_data()

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
role = st.sidebar.selectbox("Role", ["Radiology Director", "CFO", "CIO/CTO", "Compliance Officer"])
site_filter = st.sidebar.multiselect("Sites", options=SITES, default=SITES)
modality_filter = st.sidebar.multiselect("Modalities", options=MODALITIES, default=MODALITIES)

# FIXED DATE RANGE HANDLING
raw_date = st.sidebar.date_input(
    "Date range",
    value=(dt.date.today() - dt.timedelta(days=60), dt.date.today()),
)
if isinstance(raw_date, (list, tuple)) and len(raw_date) == 2:
    start_date, end_date = raw_date
else:
    start_date = raw_date
    end_date = raw_date

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

mask = (
    exams_df["site"].isin(site_filter)
    & exams_df["modality"].isin(modality_filter)
    & (pd.to_datetime(exams_df["date"]) >= start_date)
    & (pd.to_datetime(exams_df["date"]) <= end_date)
)

ex = exams_df.loc[mask]

st.title("Imaging Operations Control Tower")

st.metric("Filtered Exams", len(ex))
if not ex.empty:
    st.plotly_chart(px.histogram(ex, x="date", color="modality", title="Exam Volume"), use_container_width=True)
else:
    st.warning("No data in selected date range.")

# ------------------------------------------------------------
# Patient Discovery & Compliance Queries (Requirement #21)
# ------------------------------------------------------------
st.subheader("Patient Discovery & Compliance Queries")
with st.expander("Run Patient Discovery Query", expanded=False):
    pid = st.text_input("Patient ID contains:")
    pname = st.text_input("Patient Name contains:")
    acc = st.text_input("Accession Number contains:")
    date_range = st.date_input(
        "Exam Date Range",
        value=(dt.date.today() - dt.timedelta(days=30), dt.date.today()),
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        dstart, dend = date_range
    else:
        dstart = dend = date_range
    dstart = pd.to_datetime(dstart)
    dend = pd.to_datetime(dend)

    query = exams_df.copy()
    if pid:
        query = query[query["patient_id"].str.contains(pid, case=False)]
    if pname:
        query = query[query["patient_name"].str.contains(pname, case=False)]
    if acc:
        query = query[query["accession"].str.contains(acc, case=False)]
    query = query[(pd.to_datetime(query["date"]) >= dstart) & (pd.to_datetime(query["date"]) <= dend)]

    st.write(f"Matches: {len(query)}")
    st.dataframe(query.head(200), use_container_width=True, hide_index=True)
    st.download_button("Download Results (CSV)", query.to_csv(index=False).encode("utf-8"), "patient_discovery.csv", "text/csv")
