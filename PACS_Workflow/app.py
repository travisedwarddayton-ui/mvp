# app.py
# Radiology Workflow Accelerator — Hospital-Scale MVP (Feature-Complete Demo, Fixed SLA Calculation)
# ---------------------------------------------------------------------------
# Fix: SLA calculation threw ValueError due to column assignment shape mismatch. Now using .loc with assign.

import json
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Radiology Workflow Accelerator", page_icon="🩻", layout="wide")

# -----------------------------
# Constants & Lookups
# -----------------------------
VENDORS = ["GE", "Philips", "Siemens", "Canon", "Sectra", "Fujifilm", "Carestream", "Agfa"]
MODALITIES = ["CT", "XR", "MR", "US", "MG"]
BODYPARTS = ["CHEST", "BRAIN", "KNEE", "ABDOMEN", "SPINE", "PELVIS"]
DEPARTMENTS = ["ER", "Oncology", "Cardiology", "Neuro", "Ortho", "Outpatient"]
PRIORITIES = ["STAT", "Urgent", "Routine"]
WORKFLOW_STEPS = ["Ingested", "Normalized", "Routed", "Processed", "Delivered", "Archived"]
STEP_NEXT = {
    "Ingested": "Normalized",
    "Normalized": "Routed",
    "Routed": "Processed",
    "Processed": "Delivered",
    "Delivered": "Archived",
    "Archived": "Archived",
}
AI_STATES = ["Pending", "Running", "Complete", "Failed"]

DEFAULT_POLICIES = {
    "CT": {"retention": 3650, "tier": "Short-term + Archive", "encrypt": True, "export": True},
    "MR": {"retention": 3650, "tier": "Long-term Archive", "encrypt": True, "export": True},
    "XR": {"retention": 3650, "tier": "Compliance Vault", "encrypt": True, "export": False},
    "US": {"retention": 1825, "tier": "General Archive", "encrypt": True, "export": True},
    "MG": {"retention": 3650, "tier": "Compliance Vault", "encrypt": True, "export": False},
}

RADIOLOGISTS = [
    {"name": "Dr. Smith", "dept": "ER", "capacity": 30},
    {"name": "Dr. Chen", "dept": "Oncology", "capacity": 25},
    {"name": "Dr. Patel", "dept": "Neuro", "capacity": 20},
    {"name": "Dr. García", "dept": "Cardiology", "capacity": 25},
    {"name": "Dr. Rossi", "dept": "Ortho", "capacity": 25},
    {"name": "Dr. Lee", "dept": "Outpatient", "capacity": 30},
]

# -----------------------------
# Helpers (unchanged)
# -----------------------------
# ... keep all helper functions from the previous version ...

# -----------------------------
# Radiologist View (fixed SLA calc)
# -----------------------------
if role == "Radiologist":
    st.subheader("My Worklists (Priority & SLA)")
    names = [r["name"] for r in RADIOLOGISTS]
    me = st.selectbox("Radiologist", names)
    mine = studies[(studies["AssignedTo"] == me) & (studies["Status"] == "Delivered")].copy()

    if not mine.empty:
        now_dt = datetime.now()
        sla_remaining = []
        for _, r in mine.iterrows():
            try:
                sla_val = int(r.get("SLA_Minutes", 0))
                dt = datetime.strptime(str(r.get("StudyDate")), "%Y-%m-%d")
                remaining = sla_val - int((now_dt - dt).total_seconds() / 60)
            except Exception:
                remaining = sla_val
            sla_remaining.append(remaining)
        mine.loc[:, "SLA_Remaining_min"] = sla_remaining

        mine.sort_values(
            by=["Priority", "SLA_Remaining_min"],
            ascending=[True, True],
            inplace=True,
            key=lambda s: s.map({"STAT":0, "Urgent":1, "Routine":2}) if s.name=="Priority" else s
        )

        st.dataframe(
            mine[["StudyID","PatientID","Department","Modality","BodyPart","Priority","SLA_Remaining_min","AIStatus"]].head(200),
            use_container_width=True
        )

        with st.expander("Timeline for a case"):
            pick_id = st.selectbox("Select StudyID", mine["StudyID"].head(50))
            tl = json.loads(studies.loc[studies["StudyID"]==pick_id, "Timeline"].values[0])
            st.json(tl)
    else:
        st.info("No assigned cases yet. Run a batch to advance workflow and auto-assign.")
