# app.py
# Radiology Workflow Accelerator — Hospital-Scale MVP (Feature-Complete Demo)
# ---------------------------------------------------------------------------
# Goal: A demo you can show tomorrow that feels like a *product*, not a toy.
# It simulates a large hospital with many vendors, departments, prioritization,
# assignment, SLA timers, policy config, parallel AI processing, audit trail,
# error/retry handling, exports, and persona-specific views.
#
# Notes:
# - Uses in-memory state (Streamlit session). For real prod, wire DB + auth.
# - Safe, defensive pandas access to avoid KeyErrors.

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
    # (Retention days, Storage Tier, Needs Encryption, Export to Analytics)
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
# Helpers
# -----------------------------

def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def ensure_columns(df: pd.DataFrame, cols: Dict[str, object]):
    for c, default in cols.items():
        if c not in df.columns:
            df[c] = default
    return df


def generate_studies(n=5000) -> pd.DataFrame:
    base_date = datetime.now() - timedelta(days=60)
    rows = []
    for i in range(n):
        pr = random.choices(PRIORITIES, weights=[0.1, 0.3, 0.6])[0]  # bias toward Routine
        dept = random.choice(DEPARTMENTS)
        sla = {"STAT": 60, "Urgent": 240, "Routine": 1440}[pr]  # minutes to deliver
        ai_initial = random.choices(AI_STATES, weights=[0.6, 0.3, 0.1, 0.0])[0]
        dt = base_date + timedelta(days=random.randint(0, 60))
        rows.append({
            "StudyID": f"S{i+1:06}",
            "PatientID": str(500000 + i),
            "Vendor": random.choice(VENDORS),
            "Modality": random.choice(MODALITIES),
            "BodyPart": random.choice(BODYPARTS),
            "Department": dept,
            "Priority": pr,
            "SLA_Minutes": sla,
            "StudyDate": dt.strftime("%Y-%m-%d"),
            "Status": "Ingested",
            "Error": None,
            "AssignedTo": None,
            "AIStatus": ai_initial,
            "Timeline": json.dumps([{"ts": now_iso(), "event": "Ingested"}]),
        })
    df = pd.DataFrame(rows)
    df = ensure_columns(df, {"Error": None, "AssignedTo": None, "AIStatus": "Pending", "Timeline": "[]"})
    return df


def append_timeline(row: pd.Series, event: str) -> str:
    try:
        tl = json.loads(row.get("Timeline", "[]"))
    except Exception:
        tl = []
    tl.append({"ts": now_iso(), "event": event})
    return json.dumps(tl)


def auto_assign(studies: pd.DataFrame) -> pd.DataFrame:
    # Assign Delivered (ready) studies to radiologists by department and capacity
    ready = studies[studies["Status"] == "Delivered"].index
    load = {r["name"]: 0 for r in RADIOLOGISTS}
    for idx in ready:
        row = studies.loc[idx]
        if pd.notna(row.get("AssignedTo")) and row.get("AssignedTo"):
            continue
        dept = row.get("Department")
        # pick radiologist in same dept with lowest load under capacity
        candidates = [r for r in RADIOLOGISTS if r["dept"] == dept]
        if not candidates:
            candidates = RADIOLOGISTS  # fallback any
        # choose lowest load/capacity ratio
        candidates.sort(key=lambda r: load[r["name"]] / max(1, r["capacity"]))
        chosen = candidates[0]
        if load[chosen["name"]] < chosen["capacity"]:
            studies.at[idx, "AssignedTo"] = chosen["name"]
            load[chosen["name"]] += 1
            studies.at[idx, "Timeline"] = append_timeline(row, f"Assigned to {chosen['name']}")
    return studies


def advance_workflow(df: pd.DataFrame, policies: Dict[str, Dict]):
    df = ensure_columns(df, {"Error": None, "AIStatus": "Pending", "Timeline": "[]"})

    for i, row in df.iterrows():
        status = row.get("Status", "Ingested")
        err = row.get("Error")

        # Resolve previous error with some probability
        if err:
            if random.random() > 0.8:
                df.at[i, "Error"] = None
                df.at[i, "Timeline"] = append_timeline(row, f"Retry cleared ({status})")
            continue

        # AI parallel progression (if Routed or beyond)
        ai = row.get("AIStatus", "Pending")
        if status in ["Routed", "Processed", "Delivered"]:
            if ai in ("Pending", "Running"):
                df.at[i, "AIStatus"] = "Running" if ai == "Pending" else ("Complete" if random.random() > 0.7 else "Running")
            elif ai == "Complete":
                pass
            elif ai == "Failed":
                # occasional retry to running
                if random.random() > 0.9:
                    df.at[i, "AIStatus"] = "Running"

        # Main pipeline progression with failure chance
        if status != "Archived":
            if random.random() > 0.1:  # 90% progress
                next_s = STEP_NEXT.get(status, status)
                if next_s != status:
                    df.at[i, "Status"] = next_s
                    df.at[i, "Timeline"] = append_timeline(row, f"→ {next_s}")

                    # Apply policy at Routing
                    if next_s == "Routed":
                        pol = policies.get(row.get("Modality"), DEFAULT_POLICIES.get(row.get("Modality"), {}))
                        df.at[i, "RetentionDays"] = pol.get("retention", 1825)
                        df.at[i, "StorageTier"] = pol.get("tier", "General Archive")
                        df.at[i, "EncryptAtRest"] = pol.get("encrypt", True)
                        df.at[i, "ExportAnalytics"] = pol.get("export", True)
                # Auto-assign when Delivered
                if next_s == "Delivered":
                    pass  # handled in auto_assign()
            else:
                df.at[i, "Error"] = f"Failed at {status}"
                df.at[i, "Timeline"] = append_timeline(row, f"Error at {status}")

    # After progression, assign Delivered cases
    df = auto_assign(df)
    return df


def paginate(df: pd.DataFrame, page_size: int, key_prefix: str = "pg"):
    total = len(df)
    pages = max(1, math.ceil(total / page_size))
    page = st.session_state.get(f"{key_prefix}_page", 1)
    page = st.number_input("Page", min_value=1, max_value=pages, value=page, key=f"{key_prefix}_page_input")
    start, end = (page - 1) * page_size, min(page * page_size, total)
    st.caption(f"Showing {start+1}-{end} of {total}")
    return df.iloc[start:end]


def export_json(df: pd.DataFrame, name: str):
    js = df.to_json(orient="records").encode("utf-8")
    st.download_button("Download JSON", js, file_name=name)


# -----------------------------
# Initialize State
# -----------------------------
if "studies" not in st.session_state:
    st.session_state.studies = generate_studies(6000)

if "policies" not in st.session_state:
    st.session_state.policies = DEFAULT_POLICIES.copy()

if "audit" not in st.session_state:
    st.session_state.audit: List[Dict] = []

# Ensure columns exist across reloads
st.session_state.studies = ensure_columns(
    st.session_state.studies,
    {
        "Error": None,
        "AssignedTo": None,
        "AIStatus": "Pending",
        "Timeline": "[]",
        "RetentionDays": 0,
        "StorageTier": "",
        "EncryptAtRest": True,
        "ExportAnalytics": True,
    },
)

# -----------------------------
# Sidebar — Persona & Policy Config
# -----------------------------
st.sidebar.title("Controls")
role = st.sidebar.selectbox("Persona", ["Radiologist", "IT", "Compliance"], index=0)

with st.sidebar.expander("Retention & Routing Policies", expanded=False):
    for mod in MODALITIES:
        pol = st.session_state.policies.get(mod, DEFAULT_POLICIES.get(mod, {})).copy()
        pol["retention"] = st.number_input(f"{mod} retention (days)", 30, 3650, int(pol.get("retention", 1825)))
        pol["tier"] = st.selectbox(
            f"{mod} storage tier",
            ["Short-term + Archive", "Long-term Archive", "Compliance Vault", "General Archive"],
            index=["Short-term + Archive", "Long-term Archive", "Compliance Vault", "General Archive"].index(pol.get("tier", "General Archive"))
        )
        pol["encrypt"] = st.checkbox(f"{mod} encrypt at rest", value=bool(pol.get("encrypt", True)))
        pol["export"] = st.checkbox(f"{mod} export to analytics", value=bool(pol.get("export", True)))
        st.session_state.policies[mod] = pol
    if st.button("Save Policy Changes"):
        st.success("Policies updated for this session.")
        st.session_state.audit.append({"ts": now_iso(), "event": "POLICY_UPDATE", "details": st.session_state.policies})

with st.sidebar.expander("Simulation", expanded=False):
    steps = st.slider("Advance workflow steps (batch)", 0, 5, 1)
    if st.button("Run Batch"): 
        for _ in range(steps or 1):
            st.session_state.studies = advance_workflow(st.session_state.studies, st.session_state.policies)
        st.success("Workflow advanced.")

with st.sidebar.expander("Data", expanded=False):
    if st.button("Reset Dataset (6k studies)"):
        st.session_state.studies = generate_studies(6000)
        st.session_state.audit.append({"ts": now_iso(), "event": "RESET_DATA"})
        st.success("Dataset regenerated.")

# -----------------------------
# Header & KPIs
# -----------------------------
st.title("🏥 Radiology Workflow Accelerator — Hospital Scale")
st.caption("Vendor-neutral workflow with prioritization, SLA timers, assignment, AI parallel processing, and compliance policies.")

studies = st.session_state.studies

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Studies", f"{len(studies):,}")
col2.metric("Delivered", int((studies["Status"] == "Delivered").sum()))
col3.metric("Archived", int((studies["Status"] == "Archived").sum()))
col4.metric("Errors", int(studies["Error"].notna().sum()))
col5.metric("Running AI", int((studies["AIStatus"] == "Running").sum()))
col6.metric("AI Complete", int((studies["AIStatus"] == "Complete").sum()))

# -----------------------------
# Persona Tabs
# -----------------------------
if role == "Radiologist":
    st.subheader("My Worklists (Priority & SLA)")
    # Choose radiologist
    names = [r["name"] for r in RADIOLOGISTS]
    me = st.selectbox("Radiologist", names)
    mine = studies[(studies["AssignedTo"] == me) & (studies["Status"] == "Delivered")].copy()
    # SLA remaining in minutes assuming StudyDate is creation (demo simplification)
    now_dt = datetime.now()
    mine["SLA_Remaining_min"] = mine.apply(lambda r: r.get("SLA_Minutes", 0) - int((now_dt - datetime.strptime(str(r.get("StudyDate")), "%Y-%m-%d")).total_seconds()/60), axis=1)
    mine.sort_values(by=["Priority", "SLA_Remaining_min"], ascending=[True, True], inplace=True, key=lambda s: s.map({"STAT":0, "Urgent":1, "Routine":2}) if s.name=="Priority" else s)

    st.dataframe(mine[["StudyID","PatientID","Department","Modality","BodyPart","Priority","SLA_Remaining_min","AIStatus"]].head(200), use_container_width=True)
    st.caption("Sorted by Priority then closest SLA. Shows assigned, delivered studies only.")

    with st.expander("Timeline for a case"):
        if not mine.empty:
            pick_id = st.selectbox("Select StudyID", mine["StudyID"].head(50))
            tl = json.loads(studies.loc[studies["StudyID"]==pick_id, "Timeline"].values[0])
            st.json(tl)
        else:
            st.info("No assigned cases yet. Run a batch to advance workflow and auto-assign.")

elif role == "IT":
    t1, t2, t3, t4 = st.tabs(["Workflow Monitor", "Errors & Retries", "Vendor & Dept Mix", "Exports"])

    with t1:
        st.subheader("Workflow Monitor (Paginated)")
        # Filters
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_mod = st.multiselect("Modality", MODALITIES)
        with c2:
            f_dep = st.multiselect("Department", DEPARTMENTS)
        with c3:
            f_status = st.multiselect("Status", WORKFLOW_STEPS)
        with c4:
            f_vendor = st.multiselect("Vendor", VENDORS)
        q = studies
        if f_mod: q = q[q["Modality"].isin(f_mod)]
        if f_dep: q = q[q["Department"].isin(f_dep)]
        if f_status: q = q[q["Status"].isin(f_status)]
        if f_vendor: q = q[q["Vendor"].isin(f_vendor)]
        page = paginate(q, 200, key_prefix="it")
        st.dataframe(page[["StudyID","PatientID","Vendor","Department","Modality","BodyPart","Priority","Status","AIStatus","AssignedTo"]], use_container_width=True, height=420)
        st.graphviz_chart("""
        digraph workflow {
            rankdir=LR;
            Ingested -> Normalized -> Routed -> Processed -> Delivered -> Archived;
        }
        """)

    with t2:
        st.subheader("Errors & Retries")
        errs = studies[studies["Error"].notna()][["StudyID","Department","Modality","Status","Error"]]
        if errs.empty:
            st.success("No errors right now.")
        else:
            page_e = paginate(errs, 100, key_prefix="err")
            st.dataframe(page_e, use_container_width=True)
            if st.button("Retry All Visible"):
                ids = page_e["StudyID"].tolist()
                st.session_state.studies.loc[st.session_state.studies["StudyID"].isin(ids), "Error"] = None
                st.session_state.audit.append({"ts": now_iso(), "event": "RETRY", "count": len(ids)})
                st.success("Retries queued. Run a batch to progress.")

    with t3:
        st.subheader("Vendor & Department Mix")
        vc = studies.groupby("Vendor").size().reset_index(name="Studies")
        st.bar_chart(vc.set_index("Vendor"))
        dc = studies.groupby("Department").size().reset_index(name="Studies")
        st.bar_chart(dc.set_index("Department"))

    with t4:
        st.subheader("Exports")
        subset = q if 'q' in locals() else studies
        export_json(subset, "studies.json")
        st.caption("Hook here to push to Snowflake/Databricks in production.")

else:  # Compliance
    t1, t2, t3 = st.tabs(["Archiving & Retention", "Audit Trail", "Policy Evidence"])

    with t1:
        st.subheader("Archiving & Retention")
        arc = studies[studies["Status"] == "Archived"]
        by_mod = studies.groupby("Modality").agg(
            Total=("StudyID", "count"),
            Archived=("Status", lambda s: int((s == "Archived").sum())),
            Errors=("Error", lambda s: int(s.notna().sum())),
            Exportable=("Modality", lambda m: int(sum(st.session_state.policies.get(x, {}).get("export", True) for x in m)))
        ).reset_index()
        st.dataframe(by_mod, use_container_width=True)
        st.caption("Retention values applied at routing time; encryption flag per policy.")

    with t2:
        st.subheader("Audit Trail (Key Events)")
        if st.session_state.audit:
            st.json(st.session_state.audit)
        else:
            st.info("No admin events yet. Policy changes and retries will appear here.")

    with t3:
        st.subheader("Policy Evidence Snapshot")
        pol_df = pd.DataFrame.from_dict(st.session_state.policies, orient="index")
        st.dataframe(pol_df, use_container_width=True)
        st.caption("Export this table for auditors. In prod, sign each policy set with approver identity & timestamp.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Simulated hospital workflow: run batches from the sidebar to progress studies; policies control routing, retention, encryption, and analytics export.")
