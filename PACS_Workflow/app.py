# app.py
# Radiology Workflow Accelerator — Streamlit MVP
# -------------------------------------------------
# Purpose: Demonstrate a vendor-neutral workflow layer that
# 1) ingests multi-vendor DICOM metadata (simulated),
# 2) normalizes tags,
# 3) applies routing & retention policies,
# 4) prepares analytics outputs (NIfTI/Parquet/FHIR JSON — simulated),
# 5) provides auditability, KPIs, and a clean end-user UI for Radiology, IT, and Compliance personas.
#
# Notes:
# - This app is production-lean: typed functions, input validation, clear UX, persistent state.
# - Replace simulated transforms with your connectors (Orthanc, Snowflake, Databricks, FHIR server) when ready.
# - Safe to demo: ships with sample data generator and CSV upload.

from __future__ import annotations
import io
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="Radiology Workflow Accelerator",
    page_icon="🩻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Utilities & Types
# -----------------------------
VALID_MODALITIES = {
    "CT": "CT",
    "XR": "X-RAY",
    "MR": "MRI",
    "US": "ULTRASOUND",
    "MG": "MAMMOGRAPHY",
}

BODY_PART_LUT = {
    "CHEST": "CHEST",
    "CHEST/THORAX": "CHEST",
    "THORAX": "CHEST",
    "BRAIN": "BRAIN",
    "HEAD": "BRAIN",
    "KNEE": "KNEE",
    "ABDOMEN": "ABDOMEN",
    "ABD": "ABDOMEN",
}

ROUTING_DEFAULTS = {
    "CT": "Short-term Cloud (30 days)",
    "MRI": "Long-term Archive",
    "X-RAY": "Compliance Vault",
    "ULTRASOUND": "General Archive",
    "MAMMOGRAPHY": "Compliance Vault"
}

@dataclass
class Policy:
    storage_target: str
    retention_days: int
    encrypt: bool = True
    analytics_export: bool = True

DEFAULT_POLICIES: Dict[str, Policy] = {
    "Short-term Cloud (30 days)": Policy("Short-term Cloud (30 days)", 30, True, True),
    "Long-term Archive": Policy("Long-term Archive", 3650, True, False), # ~10 years
    "Compliance Vault": Policy("Compliance Vault", 3650, True, False),
    "General Archive": Policy("General Archive", 1825, True, True),
}

# -----------------------------
# Sample Data Generator
# -----------------------------
def generate_sample_metadata(n: int = 200) -> pd.DataFrame:
    vendors = ["GE", "Philips", "Siemens", "Canon", "Sectra"]
    body_parts = list(BODY_PART_LUT.keys())
    modalities = list(VALID_MODALITIES.keys())

    rows = []
    base_date = datetime.now() - timedelta(days=365)
    for i in range(n):
        pid = str(1000 + random.randint(0, 300))
        dt = base_date + timedelta(days=random.randint(0, 365))
        modality = random.choice(modalities)
        body = random.choice(body_parts)
        vendor = random.choice(vendors)
        accession = f"ACC{random.randint(100000, 999999)}"
        rows.append({
            "PatientID": pid,
            "AccessionNumber": accession,
            "StudyInstanceUID": f"{accession}.{random.randint(1000,9999)}",
            "Modality": modality,
            "StudyDate": dt.strftime("%Y-%m-%d"),
            "BodyPartExamined": body,
            "Vendor": vendor,
            "SizeMB": round(random.uniform(30, 800), 1),
        })
    return pd.DataFrame(rows)

# -----------------------------
# Normalization Logic
# -----------------------------
def normalize_metadata(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Ensure required cols
    required = ["PatientID", "AccessionNumber", "StudyInstanceUID", "Modality", "StudyDate", "BodyPartExamined", "Vendor", "SizeMB"]
    for col in required:
        if col not in out.columns:
            out[col] = None

    # Coerce types & normalize
    out["StudyDate"] = pd.to_datetime(out["StudyDate"], errors="coerce")
    out["BodyPartExamined"] = out["BodyPartExamined"].astype(str).str.upper().str.strip()
    out["BodyPartNormalized"] = out["BodyPartExamined"].map(BODY_PART_LUT).fillna("OTHER")

    out["Modality"] = out["Modality"].astype(str).str.upper().str.strip()
    out["ModalityNormalized"] = out["Modality"].map(VALID_MODALITIES).fillna("OTHER")

    out["Vendor"] = out["Vendor"].astype(str).str.title().str.strip()

    # Simple data quality flags
    out["DQ_MissingDate"] = out["StudyDate"].isna()
    out["DQ_UnknownModality"] = out["ModalityNormalized"].eq("OTHER")
    out["DQ_UnknownBodyPart"] = out["BodyPartNormalized"].eq("OTHER")

    return out

# -----------------------------
# Routing & Policy Application
# -----------------------------
def apply_routing(df: pd.DataFrame, routing_overrides: Dict[str, str] | None = None) -> pd.DataFrame:
    out = df.copy()
    m2tier = ROUTING_DEFAULTS.copy()
    if routing_overrides:
        m2tier.update(routing_overrides)

    out["StorageTier"] = out["ModalityNormalized"].map(m2tier).fillna("General Archive")
    # Attach policy details
    out["RetentionDays"] = out["StorageTier"].map(lambda t: DEFAULT_POLICIES.get(t, Policy(t, 365)).retention_days)
    out["EncryptAtRest"] = out["StorageTier"].map(lambda t: DEFAULT_POLICIES.get(t, Policy(t, 365)).encrypt)
    out["ExportAnalytics"] = out["StorageTier"].map(lambda t: DEFAULT_POLICIES.get(t, Policy(t, 365)).analytics_export)
    return out

# -----------------------------
# Cost & ROI Estimation (Demo)
# -----------------------------
def estimate_costs_and_savings(df: pd.DataFrame) -> Tuple[float, float, float]:
    """Return (monthly_storage_cost, egress_cost, estimated_time_saved_hours)."""
    # Demo assumptions (replace with real pricing):
    # - Cloud storage blended: $0.015/GB-month
    # - Egress per analytics export: $0.05/GB * 10% of data exported monthly
    # - Time saved: 0.25 hours per study due to normalization & automation
    gb = df["SizeMB"].sum() / 1024
    monthly_storage_cost = gb * 0.015
    egress_gb = gb * 0.10
    egress_cost = egress_gb * 0.05
    time_saved_hours = len(df) * 0.25
    return monthly_storage_cost, egress_cost, time_saved_hours

# -----------------------------
# Analytics Export (Simulated)
# -----------------------------
def export_dataframe(df: pd.DataFrame, fmt: str) -> io.BytesIO:
    buf = io.BytesIO()
    if fmt == "CSV":
        df.to_csv(buf, index=False)
    elif fmt == "JSON":
        buf.write(df.to_json(orient="records").encode("utf-8"))
    elif fmt == "PARQUET":
        # Parquet requires pyarrow/fastparquet at runtime; we simulate by CSV if missing
        try:
            import pyarrow as pa  # noqa: F401
            df.to_parquet(buf, index=False)
        except Exception:
            df.to_csv(buf, index=False)
    else:
        df.to_csv(buf, index=False)
    buf.seek(0)
    return buf

# -----------------------------
# Session State
# -----------------------------
if "raw_df" not in st.session_state:
    st.session_state.raw_df = generate_sample_metadata(350)
if "normalized_df" not in st.session_state:
    st.session_state.normalized_df = normalize_metadata(st.session_state.raw_df)
if "routed_df" not in st.session_state:
    st.session_state.routed_df = apply_routing(st.session_state.normalized_df)
if "audit_log" not in st.session_state:
    st.session_state.audit_log: List[Dict] = []

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.title("Controls")
role = st.sidebar.selectbox("Persona View", ["Radiologist", "IT", "Compliance"], index=0)

st.sidebar.markdown("---")
with st.sidebar.expander("Upload/Replace Metadata", expanded=False):
    up = st.file_uploader("Upload DICOM metadata CSV", type=["csv"])
    if up is not None:
        try:
            df_up = pd.read_csv(up)
            st.session_state.raw_df = df_up
            st.session_state.normalized_df = normalize_metadata(df_up)
            st.session_state.routed_df = apply_routing(st.session_state.normalized_df)
            st.success("Metadata uploaded and processed.")
            st.session_state.audit_log.append({
                "ts": datetime.now().isoformat(),
                "event": "UPLOAD_METADATA",
                "count": len(df_up),
            })
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")

st.sidebar.markdown("---")
with st.sidebar.expander("Routing Overrides", expanded=False):
    overrides: Dict[str, str] = {}
    for m in sorted(set(VALID_MODALITIES.values())):
        current = ROUTING_DEFAULTS.get(m, "General Archive")
        choice = st.selectbox(
            f"{m} → Storage Tier",
            options=list(DEFAULT_POLICIES.keys()),
            index=list(DEFAULT_POLICIES.keys()).index(current) if current in DEFAULT_POLICIES else 0,
        )
        overrides[m] = choice
    if st.button("Apply Routing Overrides"):
        st.session_state.routed_df = apply_routing(st.session_state.normalized_df, overrides)
        st.success("Routing overrides applied.")
        st.session_state.audit_log.append({
            "ts": datetime.now().isoformat(),
            "event": "APPLY_ROUTING",
            "overrides": overrides,
        })

# -----------------------------
# Header
# -----------------------------
st.title("🩻 Radiology Workflow Accelerator")
st.caption("Vendor-neutral layer to normalize metadata, apply routing & retention, and bridge imaging data to analytics — without replacing your PACS/VNA.")

# KPI Row
col1, col2, col3, col4 = st.columns(4)
raw_df = st.session_state.raw_df
norm_df = st.session_state.normalized_df
routed = st.session_state.routed_df

monthly_storage_cost, egress_cost, time_saved_hours = estimate_costs_and_savings(routed)

col1.metric("Studies (loaded)", f"{len(raw_df):,}")
col2.metric("Data Volume (GB)", f"{raw_df['SizeMB'].sum()/1024:,.1f}")
col3.metric("Monthly Storage ($)", f"{monthly_storage_cost:,.2f}")
col4.metric("Hours Saved / mo", f"{time_saved_hours:,.1f}")

# Tabs by Persona
if role == "Radiologist":
    t1, t2 = st.tabs(["Search & Triage", "My Queue"])

    with t1:
        st.subheader("Search & Triage")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            q_mod = st.multiselect("Modality", sorted(routed["ModalityNormalized"].unique().tolist()))
        with c2:
            q_bp = st.multiselect("Body Part", sorted(routed["BodyPartNormalized"].unique().tolist()))
        with c3:
            start = st.date_input("From", value=routed["StudyDate"].min().date() if not routed.empty else datetime.now().date())
        with c4:
            end = st.date_input("To", value=routed["StudyDate"].max().date() if not routed.empty else datetime.now().date())

        q = routed.copy()
        if q_mod:
            q = q[q["ModalityNormalized"].isin(q_mod)]
        if q_bp:
            q = q[q["BodyPartNormalized"].isin(q_bp)]
        if start:
            q = q[q["StudyDate"] >= pd.to_datetime(start)]
        if end:
            q = q[q["StudyDate"] <= pd.to_datetime(end) + pd.Timedelta(days=1)]

        st.dataframe(q[[
            "PatientID","AccessionNumber","StudyInstanceUID","ModalityNormalized","BodyPartNormalized","StudyDate","Vendor","SizeMB","StorageTier"
        ]], use_container_width=True, height=420)

        st.caption("Tip: This federated search simulates cross-PACS triage without freezing a workstation.")

    with t2:
        st.subheader("My Queue (Simulated async pulls)")
        sample = routed.sample(min(20, len(routed)), random_state=42) if not routed.empty else routed
        st.dataframe(sample[[
            "AccessionNumber","ModalityNormalized","BodyPartNormalized","StudyDate","StorageTier","ExportAnalytics"
        ]], use_container_width=True, height=420)
        st.info("In production: studies would fetch asynchronously from multiple vendor archives → local viewer.")

elif role == "IT":
    t1, t2, t3 = st.tabs(["Normalization DQ", "Routing & Retention", "Workflow Map"])

    with t1:
        st.subheader("Normalization & Data Quality")
        dq = norm_df.copy()
        dq_sum = pd.DataFrame({
            "Metric": ["Unknown Modality","Unknown Body Part","Missing Study Date"],
            "Count": [dq["DQ_UnknownModality"].sum(), dq["DQ_UnknownBodyPart"].sum(), dq["DQ_MissingDate"].sum()]
        })
        st.bar_chart(dq_sum.set_index("Metric"))
        st.dataframe(dq[dq[["DQ_UnknownModality","DQ_UnknownBodyPart","DQ_MissingDate"]].any(axis=1)][[
            "PatientID","AccessionNumber","Modality","BodyPartExamined","StudyDate","Vendor","DQ_UnknownModality","DQ_UnknownBodyPart","DQ_MissingDate"
        ]], use_container_width=True, height=360)
        st.caption("Fix LUTs once here instead of letting every department script their own patches.")

    with t2:
        st.subheader("Routing & Retention Policies")
        st.dataframe(routed[[
            "AccessionNumber","ModalityNormalized","BodyPartNormalized","StorageTier","RetentionDays","EncryptAtRest","ExportAnalytics","SizeMB"
        ]], use_container_width=True, height=380)

        dl_fmt = st.selectbox("Export normalized routing table", ["CSV","JSON","PARQUET"], index=0)
        buf = export_dataframe(routed, dl_fmt)
        st.download_button("Download Export", data=buf, file_name=f"routed.{dl_fmt.lower()}")

        st.caption("In production: push into Snowflake/Databricks, trigger downstream transformations, notify subscribers.")

    with t3:
        st.subheader("Workflow Visualization")
        st.graphviz_chart(
            """
            digraph {
                rankdir=LR;
                node [shape=box, style=filled, color=lightgrey];
                PACS [label="Multi‑vendor PACS/VNA"]
                INGEST [label="Ingest & Index"]
                NORM [label="Metadata Normalization\n(LUTs, QA)", color=lightgreen]
                ROUTE [label="Routing & Retention\n(Policies)", color=khaki]
                ARCH [label="Archive (Encrypted)"]
                ANALYTICS [label="Analytics Bridge\n(NIfTI/Parquet/FHIR)", color=lightpink]
                VIEW [label="Viewer / Worklists"]

                PACS -> INGEST -> NORM -> ROUTE
                ROUTE -> ARCH
                ROUTE -> ANALYTICS
                ANALYTICS -> VIEW
            }
            """
        )
        st.caption("Neutral layer operationalizes what you already paid for — without another storage contract.")

else:  # Compliance
    t1, t2 = st.tabs(["Retention & Encryption", "Audit Log"])

    with t1:
        st.subheader("Retention & Encryption Overview")
        comp = routed.groupby("StorageTier").agg(
            Studies=("AccessionNumber","count"),
            GB=("SizeMB", lambda s: round(s.sum()/1024, 2)),
            RetentionDays=("RetentionDays","median"),
            EncryptAtRest=("EncryptAtRest", lambda s: bool(pd.Series(s).all())),
        ).reset_index()
        st.dataframe(comp, use_container_width=True)
        st.caption("Show auditors: retention targets and encryption status per tier.")

    with t2:
        st.subheader("Audit Log (Key Events)")
        if st.session_state.audit_log:
            st.json(st.session_state.audit_log)
        else:
            st.info("No events yet. Upload metadata or apply routing to generate entries.")

# -----------------------------
# Footer actions
# -----------------------------
st.markdown("---")
colA, colB, colC = st.columns([2,2,3])
with colA:
    st.write("**Analytics Export (Simulated)**")
    fmt = st.selectbox("Format", ["CSV","JSON","PARQUET"], key="export_fmt")
    buf2 = export_dataframe(norm_df, fmt)
    st.download_button("Download Normalized Metadata", data=buf2, file_name=f"normalized.{fmt.lower()}")
with colB:
    st.write("**ROI Snapshot**")
    st.write(f"Monthly Storage: **${monthly_storage_cost:,.2f}** | Egress: **${egress_cost:,.2f}** | Hours Saved: **{time_saved_hours:,.1f}h**")
with colC:
    st.write("**Next Steps**")
    st.markdown("- Connect Orthanc for DICOM C-FIND/C-MOVE into Ingest.\n- Push routing table to Snowflake/Databricks.\n- Wire a FHIR endpoint (for report linkage).\n- Authenticate users (Okta/Azure AD) and apply RBAC.")
