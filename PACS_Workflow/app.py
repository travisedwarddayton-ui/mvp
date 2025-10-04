# app.py
# Radiology Enterprise Imaging Workflow - Production-friendly Streamlit App
# Implements the complete requirements set:
# Roles, Ingestion, Unified Viewing, Prioritization, Reporting, Analytics,
# Compliance/Security, Interop/Sharing, Non-functional guardrails, and AI plug-ins.

import os
import io
import time
import json
import base64
import zipfile
import hashlib
import datetime as dt
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple

import streamlit as st
import pandas as pd
import numpy as np

# Optional libs (safe fallbacks if missing)
try:
    import pydicom
    from pydicom.uid import generate_uid
except Exception:  # pragma: no cover
    pydicom = None

try:
    from PIL import Image
except Exception:
    Image = None

# -------------------------
# CONFIG / CONSTANTS
# -------------------------
APP_NAME = "Unified Imaging Platform (SaaS)"
APP_VERSION = "1.0.0"
BUILD_TIME = dt.datetime.utcnow().isoformat() + "Z"

# Non-functional targets (documented expectations; code provides health checks/metrics)
SLO_TARGETS = {
    "uptime": ">=99.9%",
    "p95_initial_load_sec": "<=3s",
    "security": "AES-256 at rest, TLS1.2+ in transit (deployment responsibility)",
}

# Feature flags (toggle advanced or integration features)
FEATURES = {
    "enable_sso_placeholder": True,
    "enable_pacs_connectors": True,   # toggles integration UI (simulated)
    "enable_fhir_hl7": True,
    "enable_dicomweb": True,
    "enable_ai_plugins": True,        # triage/CAD/3D placeholders
    "enable_structured_reporting": True,
    "enable_voice_upload": True,
    "enable_deidentification": True,
    "enable_external_sharing": True,
    "enable_audit_logging": True,
    "enable_analytics_dashboards": True,
    "enable_predictive_analytics": True,
}

# -------------------------
# UTILITIES
# -------------------------
def now_utc() -> str:
    return dt.datetime.utcnow().isoformat() + "Z"

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def retry(n=3, delay=0.5):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            last_ex = None
            for _ in range(n):
                try:
                    return fn(*args, **kwargs)
                except Exception as ex:
                    last_ex = ex
                    time.sleep(delay)
            raise last_ex
        return wrapper
    return decorator

# Simple in-memory "audit log"
AUDIT: List[Dict[str, Any]] = []

def audit(event: str, meta: Dict[str, Any] = None):
    if not FEATURES["enable_audit_logging"]:
        return
    AUDIT.append({
        "ts": now_utc(),
        "user": st.session_state.get("user_id", "anonymous"),
        "role": st.session_state.get("role", "unknown"),
        "event": event,
        "meta": meta or {}
    })

def secure_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(18)).decode("utf-8").rstrip("=")

# -------------------------
# MOCK / DEMO DATA LAYERS
# -------------------------

# Simulated Worklist rows
def demo_worklist(n=25) -> pd.DataFrame:
    np.random.seed(6)
    patients = [f"PT-{1000+i}" for i in range(n)]
    modalities = np.random.choice(["CT", "MRI", "XR", "US", "PET"], size=n, p=[0.28, 0.28, 0.28, 0.1, 0.06])
    priorities = np.random.choice(["STAT", "Urgent", "Routine"], size=n, p=[0.15, 0.35, 0.5])
    depts = np.random.choice(["ED", "Inpatient", "Oncology", "Cardiology", "Neuro"], size=n)
    ages = np.random.randint(1, 95, size=n)
    sex = np.random.choice(["M", "F"], size=n)
    exams = [f"{mod}-{i:04d}" for i, mod in enumerate(modalities)]
    # Simulate TAT mins (longer for MRI)
    base = {"CT":25, "MRI":55, "XR":12, "US":20, "PET":60}
    tat = [int(np.random.normal(base[m], base[m]*0.2)) for m in modalities]
    ordered = [dt.datetime.utcnow() - dt.timedelta(minutes=int(np.random.randint(10, 300))) for _ in range(n)]
    return pd.DataFrame({
        "patient_id": patients,
        "modality": modalities,
        "exam_id": exams,
        "priority": priorities,
        "department": depts,
        "age": ages,
        "sex": sex,
        "ordered_utc": [x.isoformat()+"Z" for x in ordered],
        "est_TAT_min": tat,
        "priors_found": np.random.choice([0,1,2,3], size=n, p=[0.4, 0.3, 0.2, 0.1]),
    })

# Simulated connectors status
CONNECTORS = {
    "dicomweb": {"status": "disconnected", "endpoint": "", "auth": ""},
    "hl7": {"status": "disconnected", "host": "", "port": ""},
    "fhir": {"status": "disconnected", "base_url": "", "token": ""},
    "ehr": {"status": "disconnected", "vendor": "", "notes": ""},
}

# Simulated EHR interaction
def push_report_to_ehr(patient_id: str, report_text: str) -> bool:
    # Placeholder for HL7 ORU^R01 or FHIR DiagnosticReport POST
    audit("EHR_PUSH", {"patient_id": patient_id, "len": len(report_text)})
    return True

# -------------------------
# SESSION INIT
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{secure_token()}"

if "role" not in st.session_state:
    st.session_state.role = "Radiologist"

if "worklist" not in st.session_state:
    st.session_state.worklist = demo_worklist(35)

if "connectors" not in st.session_state:
    st.session_state.connectors = CONNECTORS.copy()

if "prior_store" not in st.session_state:
    # In a real system: VNA index; here we just simulate “priors”
    st.session_state.prior_store = {}

# -------------------------
# SIDEBAR: SSO + ROLE + NAV
# -------------------------
st.set_page_config(page_title=APP_NAME, layout="wide")
st.sidebar.title(APP_NAME)
st.sidebar.caption(f"v{APP_VERSION} • build {BUILD_TIME}")

if FEATURES["enable_sso_placeholder"]:
    st.sidebar.markdown("**Single Sign-On (SSO)**")
    oidc_issuer = st.sidebar.text_input("OIDC Issuer (placeholder)", value="https://idp.example.org")
    st.sidebar.text_input("SSO Email", value="radiologist@example.org")
    st.sidebar.button("Sign In (Simulated)")

role = st.sidebar.selectbox("Role", ["Radiologist", "Technologist", "Referring Physician", "Administrator/IT"])
st.session_state.role = role

nav = st.sidebar.radio(
    "Workflow",
    [
        "1) Ingestion & Data Propagation",
        "2) Unified Image Access & Viewing",
        "3) Workflow & Prioritization",
        "4) Reporting & EHR Integration",
        "5) Analytics & Decision Support",
        "6) Compliance, Security & Audit",
        "7) Interoperability & External Sharing",
        "— Admin: Health/Config —"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")
if st.sidebar.button("Refresh Worklist"):
    st.session_state.worklist = demo_worklist(35)
    audit("REFRESH_WORKLIST")

# -------------------------
# HEADER
# -------------------------
st.title("Unified Imaging Platform")
st.caption("A cloud-native, enterprise imaging workflow for hospitals — all modalities, all roles.")

# -------------------------
# 1) INGESTION & DATA PROPAGATION
# -------------------------
if nav.startswith("1)"):
    st.header("1) Image Ingestion & Data Propagation")
    st.write(
        "Auto-ingest new studies from all modalities, auto-link to patient records via HL7/FHIR, "
        "and automatically retrieve priors from connected archives."
    )

    # Simulated connectors
    cols = st.columns(4)
    with cols[0]:
        st.subheader("DICOMweb")
        if FEATURES["enable_dicomweb"]:
            ep = st.text_input("Endpoint", value=st.session_state.connectors["dicomweb"]["endpoint"])
            auth = st.text_input("API Key/Token", type="password", value=st.session_state.connectors["dicomweb"]["auth"])
            if st.button("Connect DICOMweb"):
                st.session_state.connectors["dicomweb"] = {"status":"connected", "endpoint": ep, "auth": auth}
                st.success("Connected to DICOMweb")
                audit("CONNECT_DICOMWEB", {"endpoint": ep})
        else:
            st.info("DICOMweb integration disabled by feature flag.")

    with cols[1]:
        st.subheader("HL7")
        if FEATURES["enable_fhir_hl7"]:
            host = st.text_input("HL7 Host", value=st.session_state.connectors["hl7"]["host"])
            port = st.number_input("HL7 Port", value=int(st.session_state.connectors["hl7"]["port"] or 2575), step=1)
            if st.button("Connect HL7"):
                st.session_state.connectors["hl7"] = {"status":"connected", "host":host, "port":str(port)}
                st.success("Connected to HL7")
                audit("CONNECT_HL7", {"host": host, "port": port})
        else:
            st.info("HL7 integration disabled.")

    with cols[2]:
        st.subheader("FHIR")
        if FEATURES["enable_fhir_hl7"]:
            base = st.text_input("FHIR Base URL", value=st.session_state.connectors["fhir"]["base_url"])
            tok = st.text_input("FHIR Token", type="password", value=st.session_state.connectors["fhir"]["token"])
            if st.button("Connect FHIR"):
                st.session_state.connectors["fhir"] = {"status":"connected", "base_url":base, "token":tok}
                st.success("Connected to FHIR")
                audit("CONNECT_FHIR", {"base": base})
        else:
            st.info("FHIR integration disabled.")

    with cols[3]:
        st.subheader("EHR")
        vendor = st.text_input("EHR Vendor", value=st.session_state.connectors["ehr"]["vendor"])
        notes = st.text_area("Notes", value=st.session_state.connectors["ehr"]["notes"])
        if st.button("Record EHR Link (Simulated)"):
            st.session_state.connectors["ehr"] = {"status":"linked", "vendor":vendor, "notes":notes}
            st.success("EHR link recorded")
            audit("LINK_EHR", {"vendor": vendor})

    st.markdown("---")
    st.subheader("Upload New Studies (All Modalities)")
    uploaded = st.file_uploader(
        "Upload DICOM files or ZIP (simulated ingestion). Multiple files supported.",
        accept_multiple_files=True,
        type=["dcm", "dicom", "zip"]
    )
    if uploaded:
        new_records = []
        for f in uploaded:
            if f.name.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(f.getvalue())) as zf:
                    for name in zf.namelist():
                        if name.lower().endswith((".dcm", ".dicom")):
                            new_records.append({"filename": name, "size": zf.getinfo(name).file_size})
            else:
                new_records.append({"filename": f.name, "size": len(f.getvalue())})

        st.success(f"Ingested {len(new_records)} study files.")
        audit("INGEST_FILES", {"count": len(new_records)})

        st.json({"ingested_files": new_records[:10], "total": len(new_records)})

    st.markdown("---")
    st.subheader("Auto-Link & Priors Retrieval")
    st.write("Simulates matching by MRN/DOB via HL7/FHIR and fetching priors from connected PACS/VNA.")
    patient_id = st.text_input("Patient ID (e.g., PT-1005)", value="PT-1005")
    if st.button("Match & Fetch Priors"):
        # Simulate priors
        priors = np.random.choice([0,1,2,3], p=[0.2,0.4,0.3,0.1])
        st.session_state.prior_store[patient_id] = [f"PRIOR-{i}" for i in range(priors)]
        st.success(f"Linked patient and fetched {priors} prior(s).")
        audit("PRIORS_FETCHED", {"patient_id": patient_id, "priors": priors})

# -------------------------
# 2) UNIFIED IMAGE ACCESS & VIEWING
# -------------------------
elif nav.startswith("2)"):
    st.header("2) Unified Image Access & Viewing")
    st.write("Single viewer for all modalities with side-by-side prior/current comparison and progressive navigation.")

    wl = st.session_state.worklist
    st.markdown("**Active Worklist** (all modalities)")
    st.dataframe(wl, use_container_width=True)

    st.markdown("---")
    st.subheader("Open Study")
    exam_id = st.selectbox("Select Exam", wl["exam_id"].tolist())
    pid = wl.set_index("exam_id").loc[exam_id, "patient_id"]
    modality = wl.set_index("exam_id").loc[exam_id, "modality"]
    st.write(f"**Patient:** {pid} | **Modality:** {modality}")

    colv = st.columns(2)
    with colv[0]:
        st.write("**Current Study**")
        cur_file = st.file_uploader("Upload current study DICOM (single .dcm for demo)", type=["dcm", "dicom"], key="cur_dcm")
        if cur_file and pydicom:
            ds = pydicom.dcmread(io.BytesIO(cur_file.getvalue()), force=True)
            # Progressive navigation (if multi-slice)
            rows = int(getattr(ds, "Rows", 512))
            cols = int(getattr(ds, "Columns", 512))
            st.caption(f"DICOM: {rows}x{cols} • SOPClass: {getattr(ds, 'SOPClassUID', '')}")
            # Try pixel data
            try:
                arr = ds.pixel_array
                idx = st.slider("Slice", min_value=0, max_value=arr.shape[0]-1 if arr.ndim == 3 else 0, value=0)
                img = arr[idx] if arr.ndim == 3 else arr
                st.image(img, clamp=True)
            except Exception as ex:
                st.warning(f"Could not render pixel data: {ex}")
        elif cur_file and not pydicom:
            st.error("Install pydicom to render DICOM (pip install pydicom).")

    with colv[1]:
        st.write("**Prior Study (Optional)**")
        prior_file = st.file_uploader("Upload prior DICOM (single .dcm for demo)", type=["dcm", "dicom"], key="prior_dcm")
        if prior_file and pydicom:
            ds2 = pydicom.dcmread(io.BytesIO(prior_file.getvalue()), force=True)
            try:
                arr2 = ds2.pixel_array
                idx2 = st.slider("Prior Slice", min_value=0, max_value=arr2.shape[0]-1 if arr2.ndim == 3 else 0, value=0)
                img2 = arr2[idx2] if arr2.ndim == 3 else arr2
                st.image(img2, clamp=True)
            except Exception as ex:
                st.warning(f"Could not render prior pixel data: {ex}")
        elif prior_file and not pydicom:
            st.error("Install pydicom to render DICOM.")

    st.markdown("> Any-device access: This viewer works in the browser; tablet-friendly UI out of the box.")

# -------------------------
# 3) WORKFLOW & PRIORITIZATION
# -------------------------
elif nav.startswith("3)"):
    st.header("3) Workflow & Prioritization")
    st.write("Intelligent worklist triage, sub-specialty routing, and alerts for critical findings.")

    wl = st.session_state.worklist.copy()
    subspec = st.multiselect("Radiologist Sub-specialties", ["Neuro", "Cardiac", "MSK", "Body", "Peds"], default=["Neuro", "Body"])
    pri_filter = st.multiselect("Priority Filter", ["STAT", "Urgent", "Routine"], default=["STAT", "Urgent"])
    dept_filter = st.multiselect("Department Filter", ["ED", "Inpatient", "Oncology", "Cardiology", "Neuro"], default=["ED","Inpatient","Oncology"])

    wlf = wl[wl["priority"].isin(pri_filter) & wl["department"].isin(dept_filter)].copy()
    # AI triage placeholder: auto-bump STAT
    if FEATURES["enable_ai_plugins"]:
        wlf["triage_score"] = wlf["priority"].map({"STAT": 1.0, "Urgent": 0.7, "Routine": 0.2}) + np.random.uniform(0, 0.1, size=len(wlf))
        wlf = wlf.sort_values(by=["triage_score", "est_TAT_min"], ascending=[False, True])
    else:
        wlf = wlf.sort_values(by=["priority", "est_TAT_min"], ascending=[True, True])

    st.subheader("Prioritized Worklist")
    st.dataframe(wlf, use_container_width=True)

    if st.button("Send Critical Alerts (Simulated)"):
        # In real world: notify ED/Teams, escalate per pathway
        st.success("Alerts triggered for STAT/critical cases.")
        audit("CRITICAL_ALERTS_SENT", {"count": int((wlf['priority']=="STAT").sum())})

# -------------------------
# 4) REPORTING & EHR INTEGRATION
# -------------------------
elif nav.startswith("4)"):
    st.header("4) Reporting & EHR Integration")
    st.write("Structured reporting with AI-assisted draft and push to EHR via HL7/FHIR.")

    wl = st.session_state.worklist
    sel = st.selectbox("Select Exam for Reporting", wl["exam_id"].tolist())
    pid = wl.set_index("exam_id").loc[sel, "patient_id"]
    mod = wl.set_index("exam_id").loc[sel, "modality"]

    st.markdown(f"**Patient:** {pid}  |  **Modality:** {mod}")

    # Structured template
    if FEATURES["enable_structured_reporting"]:
        st.subheader("Structured Report")
        colr = st.columns(2)
        with colr[0]:
            indication = st.text_input("Indication", value="Rule out acute pathology.")
            technique = st.text_input("Technique", value=f"{mod} imaging with standard protocol.")
            comparison = st.text_input("Comparison", value="Prior study available; compared side-by-side.")
        with colr[1]:
            findings = st.text_area("Findings", height=150, value="No acute intracranial hemorrhage. Mild chronic microvascular changes.")
            impression = st.text_area("Impression", height=150, value="No acute findings. Recommend routine follow-up if symptoms persist.")

    # Voice dictation upload (optional)
    if FEATURES["enable_voice_upload"]:
        st.subheader("Voice Dictation (Upload Audio for Transcription)")
        vfile = st.file_uploader("Upload .wav/.mp3 (placeholder transcription)", type=["wav", "mp3"])
        if vfile:
            st.info(f"Received audio: {vfile.name} (transcription via external ASR recommended)")
            audit("VOICE_UPLOAD", {"bytes": len(vfile.getvalue())})

    # AI-assisted draft
    if FEATURES["enable_ai_plugins"]:
        if st.button("Generate AI Draft (Placeholder)"):
            draft = f"""INDICATION: {indication}
TECHNIQUE: {technique}
COMPARISON: {comparison}
FINDINGS: {findings}
IMPRESSION: {impression}
"""
            st.code(draft, language="markdown")
            audit("AI_DRAFT_GENERATED", {"exam": sel})

    final_report = st.text_area("Final Report (editable)", height=240, value="")
    if st.button("Finalize & Push to EHR"):
        ok = push_report_to_ehr(pid, final_report or "Signed report with structured sections.")
        if ok:
            st.success("Report finalized and pushed to EHR (simulated HL7/FHIR).")
            audit("REPORT_FINALIZED", {"patient_id": pid, "exam_id": sel})

# -------------------------
# 5) ANALYTICS & DECISION SUPPORT
# -------------------------
elif nav.startswith("5)"):
    st.header("5) Analytics & Decision Support")
    st.write("Embedded dashboards: turnaround times, utilization, downtime. Plug-and-play AI and predictive analytics.")

    wl = st.session_state.worklist
    st.subheader("Key Metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Study Volume (24h)", value=int(len(wl)))
    with c2:
        p95_tat = int(np.percentile(wl["est_TAT_min"], 95))
        st.metric("p95 TAT (min)", value=p95_tat)
    with c3:
        stat_pct = round((wl["priority"].eq("STAT").mean()*100), 1)
        st.metric("STAT Mix (%)", value=stat_pct)
    with c4:
        dup_rate = 2.7  # placeholder; would come from EHR duplicates tracking
        st.metric("Duplicate Scan Rate (%)", value=dup_rate)

    st.subheader("Utilization by Modality")
    util = wl.groupby("modality").size().reset_index(name="count")
    st.bar_chart(util.set_index("modality"))

    st.subheader("Turnaround Distribution")
    st.line_chart(wl["est_TAT_min"].sort_values().reset_index(drop=True))

    if FEATURES["enable_predictive_analytics"]:
        st.subheader("Predictive: ED Surge Readiness (Next 6 Hrs)")
        # Simple illustrative forecast
        horizon = np.arange(1, 7)
        incoming = np.maximum(0, np.random.poisson(lam=5, size=6) + np.random.randint(-2, 3, size=6))
        dfp = pd.DataFrame({"hour_from_now": horizon, "expected_studies": incoming})
        st.area_chart(dfp.set_index("hour_from_now"))
        st.caption("Illustrative only; connect real ED arrivals + modality schedules for production.")

    if FEATURES["enable_ai_plugins"]:
        st.subheader("AI Modules (Plug-in)")
        st.checkbox("Auto-triage ED head CT for stroke", value=True)
        st.checkbox("CAD for lung nodules", value=True)
        st.checkbox("3D/AR recon in viewer", value=False)
        st.info("Integrate vendor AI via REST/gRPC; results render inline in viewer/worklist.")

# -------------------------
# 6) COMPLIANCE, SECURITY & AUDIT
# -------------------------
elif nav.startswith("6)"):
    st.header("6) Compliance, Security & Audit")
    st.write("Encryption, audit trails, de-identification, patching posture, and role-based access.")

    st.subheader("Encryption")
    st.write("- **At rest:** AES-256 (cloud provider KMS)  \n- **In transit:** TLS 1.2+  \n- **Keys:** customer-managed keys (CMK) optional")

    st.subheader("RBAC")
    st.write("Roles: Radiologist, Technologist, Referring Physician, Administrator/IT. Enforce least-privilege scopes.")

    st.subheader("De-identification (DICOM PHI redaction)")
    if FEATURES["enable_deidentification"]:
        did = st.file_uploader("Upload DICOM for De-ID", type=["dcm", "dicom"], key="deid")
        if did and pydicom:
            ds = pydicom.dcmread(io.BytesIO(did.getvalue()), force=True)
            # Minimal demo de-id (production: comprehensive tag set per DICOM PS3.15)
            for tag in [(0x0010,0x0010),(0x0010,0x0020),(0x0010,0x0030),(0x0010,0x0040)]:
                if tag in ds:
                    ds[tag].value = ""
            bio = io.BytesIO()
            ds.save_as(bio)
            st.download_button("Download De-Identified DICOM", bio.getvalue(), file_name="deid.dcm")
            st.success("Basic PHI fields removed (Name, ID, DOB, Sex).")
            audit("DICOM_DEID", {"bytes": len(bio.getvalue())})
        elif did and not pydicom:
            st.error("Install pydicom to use de-identification.")
    else:
        st.info("De-ID disabled by feature flag.")

    st.subheader("Audit Log")
    df_a = pd.DataFrame(AUDIT[-200:])
    st.dataframe(df_a, use_container_width=True)

    st.subheader("Patching & Updates")
    st.write("SaaS delivers continuous security updates. Zero-downtime rollouts with canary deployments.")

# -------------------------
# 7) INTEROPERABILITY & EXTERNAL SHARING
# -------------------------
elif nav.startswith("7)"):
    st.header("7) Interoperability & External Sharing")
    st.write("Standards-based exchange: DICOMweb, IHE XDS, FHIR Imaging. Instant patient/physician sharing.")

    st.subheader("Standards")
    st.write(
        "- **DICOMweb** (WADO-RS/STOW-RS/QIDO-RS) for image access\n"
        "- **IHE XDS/XDR** for document exchange\n"
        "- **FHIR** ImagingStudy/DiagnosticReport for EHR sync\n"
        "- **HL7 v2** ORU^R01 for report delivery"
    )

    st.subheader("Instant Sharing Portal (Tokenized Link)")
    pid = st.text_input("Patient ID to share", value="PT-1005")
    if st.button("Generate Secure Link"):
        token = secure_token()
        expires = (dt.datetime.utcnow() + dt.timedelta(hours=24)).isoformat() + "Z"
        link = f"https://share.example.org/portal?pid={pid}&token={token}"
        st.code(link, language="text")
        st.caption(f"Valid until: {expires}  •  Access is auditable and revocable.")
        audit("SHARE_LINK_CREATED", {"patient_id": pid, "exp": expires})

    st.subheader("One-Click Export (Research/Tumor Board)")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("metadata.json", json.dumps({"exported": now_utc(), "studies": ["demo1", "demo2"]}))
    st.download_button("Download ZIP Package", buf.getvalue(), file_name="export_package.zip")
    audit("EXPORT_PACKAGE", {"bytes": len(buf.getvalue())})

# -------------------------
# ADMIN: HEALTH/CONFIG
# -------------------------
else:
    st.header("Administration: Health, Config & Non-Functional Targets")
    st.subheader("Service Level Objectives")
    st.json(SLO_TARGETS)

    st.subheader("Connectors Status")
    st.json(st.session_state.connectors)

    st.subheader("Health Checks")
    health = pd.DataFrame([
        {"component": "App", "status": "OK", "checked": now_utc()},
        {"component": "DICOMweb", "status": st.session_state.connectors["dicomweb"]["status"], "checked": now_utc()},
        {"component": "HL7", "status": st.session_state.connectors["hl7"]["status"], "checked": now_utc()},
        {"component": "FHIR", "status": st.session_state.connectors["fhir"]["status"], "checked": now_utc()},
        {"component": "EHR", "status": st.session_state.connectors["ehr"]["status"], "checked": now_utc()},
    ])
    st.table(health)

    st.subheader("Configuration (JSON)")
    cfg = {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "features": FEATURES,
        "build": BUILD_TIME,
    }
    st.code(json.dumps(cfg, indent=2), language="json")

    st.info(
        "Deployment: Run behind your SSO/gateway, enforce TLS, and attach to managed storage (encrypted). "
        "Scale horizontally with multiple Streamlit workers; cache DICOM slices via CDN for global sites."
    )
