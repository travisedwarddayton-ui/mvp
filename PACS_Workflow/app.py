# Imaging Operations Control Tower – Streamlit MVP (Fixed Date Handling)

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
                recs.append({
                    "exam_id": f"E{m.machine_id}-{date}-{i}",
                    "date": pd.to_datetime(date),
                    "site": m.site,
                    "machine_id": m.machine_id,
                    "modality": m.modality,
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
role = st.sidebar.selectbox("Role", ["Radiology Director", "CFO", "CIO/CTO"])
site_filter = st.sidebar.multiselect("Sites", options=SITES, default=SITES)
modality_filter = st.sidebar.multiselect("Modalities", options=MODALITIES, default=MODALITIES)

# FIXED DATE RANGE HANDLING
raw_date = st.sidebar.date_input(
    "Date range",
    value=(dt.date.today() - dt.timedelta(days=60), dt.date.today()),
)

# Ensure raw_date is always a tuple of two dates
if isinstance(raw_date, (list, tuple)) and len(raw_date) == 2:
    start_date, end_date = raw_date
else:
    start_date = raw_date
    end_date = raw_date

# Convert to pandas Timestamps
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# ------------------------------------------------------------
# Data Filter
# ------------------------------------------------------------
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
