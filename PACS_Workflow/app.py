# app.py
# Radiology Workflow Accelerator — MVP Workflow Engine
# -------------------------------------------------
# Purpose: Show end users a proof-of-concept radiology workflow system:
# - Ingest → Normalize → Route → Process → Deliver → Archive.
# - Each study flows step by step with statuses.
# - Simulates automation for MVP sales demos.

import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Radiology Workflow Accelerator", page_icon="🩻", layout="wide")

# -----------------------------
# Sample Data
# -----------------------------
def generate_studies(n=15):
    vendors = ["GE", "Philips", "Siemens"]
    modalities = ["CT", "XR", "MR"]
    body_parts = ["CHEST", "BRAIN", "KNEE"]
    base_date = datetime.now() - timedelta(days=30)

    studies = []
    for i in range(n):
        studies.append({
            "StudyID": f"S{i+1:04}",
            "PatientID": str(1000+i),
            "Vendor": random.choice(vendors),
            "Modality": random.choice(modalities),
            "BodyPart": random.choice(body_parts),
            "StudyDate": (base_date + timedelta(days=random.randint(0,30))).strftime("%Y-%m-%d"),
            "Status": "Ingested"
        })
    return pd.DataFrame(studies)

if "studies" not in st.session_state:
    st.session_state.studies = generate_studies()

# -----------------------------
# Workflow Transitions
# -----------------------------
workflow_steps = ["Ingested", "Normalized", "Routed", "Processed", "Delivered", "Archived"]

step_logic = {
    "Ingested": "Normalized",
    "Normalized": "Routed",
    "Routed": "Processed",
    "Processed": "Delivered",
    "Delivered": "Archived",
    "Archived": "Archived"
}

# Apply step transition
for i, row in st.session_state.studies.iterrows():
    if row["Status"] != "Archived":
        if random.random() > 0.2:  # 80% chance to move forward
            st.session_state.studies.at[i, "Status"] = step_logic[row["Status"]]

# -----------------------------
# UI
# -----------------------------
st.title("🩻 Radiology Workflow Accelerator")
st.caption("Proof-of-concept MVP: studies automatically move through the workflow lifecycle.")

# KPI Overview
col1, col2, col3 = st.columns(3)
col1.metric("Total Studies", len(st.session_state.studies))
col2.metric("Completed (Archived)", (st.session_state.studies["Status"]=="Archived").sum())
col3.metric("In Progress", (st.session_state.studies["Status"]!="Archived").sum())

# Workflow Table
st.subheader("Study Workflow Status")
st.dataframe(st.session_state.studies, use_container_width=True)

# Pipeline Visualization
st.subheader("Workflow Pipeline")
st.graphviz_chart("""
digraph workflow {
    rankdir=LR;
    Ingested -> Normalized -> Routed -> Processed -> Delivered -> Archived;
}
""")

# Auto-refresh simulation
st.caption("🔄 Studies auto-progress through workflow stages. Refresh page to see updates.")
