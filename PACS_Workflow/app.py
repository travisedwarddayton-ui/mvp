# app.py
# Radiology Workflow Accelerator — Full MVP Application
# -------------------------------------------------
# Purpose: End-to-end MVP to demo a vendor-neutral workflow system for radiology data.
# Features:
# - Ingest simulated studies.
# - Normalize metadata.
# - Route to storage tiers.
# - Process (convert/export).
# - Deliver to radiologist queue.
# - Archive & compliance view.
# - Failure/retry handling.
# - Persona-based dashboards (Radiologist, IT, Compliance).

import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Radiology Workflow Accelerator", page_icon="🩻", layout="wide")

# -----------------------------
# Sample Data Generator
# -----------------------------
def generate_studies(n=30):
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
            "Status": "Ingested",
            "Error": None
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

# Apply step transition with error handling
for i, row in st.session_state.studies.iterrows():
    if row["Status"] != "Archived":
        if row["Error"]:  # Retry chance
            if random.random() > 0.7:
                st.session_state.studies.at[i, "Error"] = None
        else:
            if random.random() > 0.15:  # 85% chance to move forward
                st.session_state.studies.at[i, "Status"] = step_logic[row["Status"]]
            else:
                st.session_state.studies.at[i, "Error"] = f"Failed at {row['Status']}"

# -----------------------------
# Persona Switch
# -----------------------------
st.sidebar.title("Persona")
role = st.sidebar.radio("Select your view", ["Radiologist", "IT", "Compliance"])

# -----------------------------
# UI - Shared KPIs
# -----------------------------
st.title("🩻 Radiology Workflow Accelerator")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Studies", len(st.session_state.studies))
col2.metric("Archived", (st.session_state.studies["Status"]=="Archived").sum())
col3.metric("Errors", st.session_state.studies["Error"].notna().sum())
col4.metric("In Progress", (st.session_state.studies["Status"]!="Archived").sum())

# -----------------------------
# Radiologist View
# -----------------------------
if role == "Radiologist":
    st.subheader("My Worklist")
    queue = st.session_state.studies[st.session_state.studies["Status"]=="Delivered"]
    st.dataframe(queue[["StudyID","PatientID","Modality","BodyPart","StudyDate","Vendor"]], use_container_width=True)
    st.info("Radiologists see only studies that are ready to read (Delivered stage).")

# -----------------------------
# IT View
# -----------------------------
elif role == "IT":
    t1, t2 = st.tabs(["Workflow Monitor","Error Handling"])

    with t1:
        st.subheader("Workflow Monitor")
        st.dataframe(st.session_state.studies, use_container_width=True)
        st.graphviz_chart("""
        digraph workflow {
            rankdir=LR;
            Ingested -> Normalized -> Routed -> Processed -> Delivered -> Archived;
        }
        """)

    with t2:
        st.subheader("Error Handling")
        errors = st.session_state.studies[st.session_state.studies["Error"].notna()]
        if errors.empty:
            st.success("No errors currently.")
        else:
            st.dataframe(errors[["StudyID","Status","Error"]], use_container_width=True)
            if st.button("Retry All Failed"):
                st.session_state.studies.loc[st.session_state.studies["Error"].notna(), "Error"] = None
                st.success("Retry triggered. Refresh to see progress.")

# -----------------------------
# Compliance View
# -----------------------------
else:
    st.subheader("Archiving & Compliance")
    archived = st.session_state.studies[st.session_state.studies["Status"]=="Archived"]
    st.dataframe(archived[["StudyID","PatientID","Modality","BodyPart","StudyDate","Vendor"]], use_container_width=True)
    st.caption("Auditors see that all studies eventually flow into archive with traceable steps.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("🔄 Refresh page to simulate ongoing workflow progression with random errors/retries.")
