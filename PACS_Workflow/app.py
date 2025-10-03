# app.py
# Radiology Workflow Accelerator — Hospital-Scale MVP (Enhanced with Cover Page, Executive Summary, Simulation Controls, KPI Dashboard, SLA Tracking, PDF with Charts, Audit Logs & Policies)

import json
import random
from datetime import datetime

import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import matplotlib.pyplot as plt

st.set_page_config(page_title="Radiology Workflow Accelerator", page_icon="🩻", layout="wide")

# -----------------------------
# Constants & Lookups
# -----------------------------
VENDORS = ["GE", "Philips", "Siemens", "Canon", "Sectra", "Fujifilm", "Carestream", "Agfa"]
MODALITIES = ["CT", "XR", "MR", "US", "MG"]
DEPARTMENTS = ["ER", "Oncology", "Cardiology", "Neuro", "Ortho", "Outpatient"]
PRIORITIES = ["STAT", "Urgent", "Routine"]
WORKFLOW_STEPS = ["Ingested", "Normalized", "Routed", "Processed", "Delivered", "Archived"]

RADIOLOGISTS = [
    {"name": "Dr. Smith", "dept": "ER"},
    {"name": "Dr. Chen", "dept": "Oncology"},
    {"name": "Dr. Patel", "dept": "Neuro"},
    {"name": "Dr. García", "dept": "Cardiology"},
    {"name": "Dr. Rossi", "dept": "Ortho"},
    {"name": "Dr. Lee", "dept": "Outpatient"},
]

DEFAULT_POLICIES = {
    "CT": {"retention": 3650, "tier": "Short-term + Archive", "encrypt": True, "export": True},
    "MR": {"retention": 3650, "tier": "Long-term Archive", "encrypt": True, "export": True},
    "XR": {"retention": 3650, "tier": "Compliance Vault", "encrypt": True, "export": False},
    "US": {"retention": 1825, "tier": "General Archive", "encrypt": True, "export": True},
    "MG": {"retention": 3650, "tier": "Compliance Vault", "encrypt": True, "export": False},
}

# -----------------------------
# Sidebar role selection
# -----------------------------
st.sidebar.title("Persona")
role = st.sidebar.radio("Select persona", ["Radiologist", "IT", "Compliance"], index=0)

# -----------------------------
# Simulated dataset
# -----------------------------
if "studies" not in st.session_state:
    rows = []
    for i in range(500):
        rows.append({
            "StudyID": f"S{i+1:04}",
            "PatientID": str(1000+i),
            "Department": random.choice(DEPARTMENTS),
            "Modality": random.choice(MODALITIES),
            "Priority": random.choice(PRIORITIES),
            "Vendor": random.choice(VENDORS),
            "Status": random.choice(WORKFLOW_STEPS),
            "AssignedTo": random.choice([r["name"] for r in RADIOLOGISTS] + [None]),
            "StudyDate": datetime.now().strftime("%Y-%m-%d"),
            "AIStatus": random.choice(["Pending","Running","Complete"]),
            "Timeline": json.dumps([{"ts": datetime.now().isoformat(), "event": "Created"}])
        })
    st.session_state.studies = pd.DataFrame(rows)

studies = st.session_state.studies

# -----------------------------
# Simulation Controls
# -----------------------------
st.sidebar.title("Simulation Controls")
if st.sidebar.button("Advance Workflow Batch"):
    for i in studies.index:
        if studies.at[i, "Status"] != "Archived":
            if random.random() > 0.2:
                current = studies.at[i, "Status"]
                idx = WORKFLOW_STEPS.index(current)
                if idx < len(WORKFLOW_STEPS)-1:
                    studies.at[i, "Status"] = WORKFLOW_STEPS[idx+1]
                    studies.at[i, "Timeline"] = json.dumps(json.loads(studies.at[i, "Timeline"]) + [{"ts": datetime.now().isoformat(), "event": f"→ {WORKFLOW_STEPS[idx+1]}"}])
    st.success("Workflow advanced.")

if st.sidebar.button("Inject Errors"):
    for i in random.sample(list(studies.index), 10):
        studies.at[i, "Error"] = f"Failed at {studies.at[i, 'Status']}"
    st.success("Errors injected.")

# -----------------------------
# KPI Dashboard (Top-level)
# -----------------------------
st.title("🏥 Radiology Workflow Accelerator — KPI Dashboard")

if "SLA_Remaining_min" not in studies.columns:
    studies["SLA_Remaining_min"] = [random.randint(-60, 300) for _ in range(len(studies))]

sla_breaches = (studies["SLA_Remaining_min"] < 0).sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Studies", len(studies))
col2.metric("Archived", (studies["Status"]=="Archived").sum())
col3.metric("Delivered", (studies["Status"]=="Delivered").sum())
col4.metric("Errors", (studies.get("Error").notna().sum() if "Error" in studies.columns else 0))
col5.metric("AI Running", (studies["AIStatus"]=="Running").sum())
col6.metric("SLA Breaches", sla_breaches)

if "kpi_trends" not in st.session_state:
    st.session_state.kpi_trends = []

st.session_state.kpi_trends.append({
    "ts": datetime.now().isoformat(),
    "Errors": (studies.get("Error").notna().sum() if "Error" in studies.columns else 0),
    "SLA_Breaches": sla_breaches
})

trend_df = pd.DataFrame(st.session_state.kpi_trends)

st.subheader("📈 Trends Over Time")
if not trend_df.empty:
    st.line_chart(trend_df.set_index("ts")[ ["Errors", "SLA_Breaches"] ])
    
    csv = trend_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download KPI Trends as CSV",
        data=csv,
        file_name="kpi_trends.csv",
        mime="text/csv",
    )

    # PDF Report Export with Cover Page, Trends, Audit Logs & Policies
    def generate_pdf():
        file_path = "/tmp/kpi_report.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Cover page with title and summary
        elements.append(Paragraph("🏥 Radiology Workflow Accelerator", styles['Title']))
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Executive KPI & Compliance Report", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("This report provides a hospital-wide overview of radiology workflow performance, errors, SLA breaches, compliance posture, and retention policies.", styles['Normal']))
        elements.append(Spacer(1, 24))
        elements.append(Paragraph("Prepared for Hospital Leadership", styles['Italic']))
        elements.append(PageBreak())

        elements.append(Paragraph("Radiology Workflow Accelerator — Executive KPI Report", styles['Title']))
        elements.append(Spacer(1, 12))

        # KPI summary table
        data = [["Metric", "Value"],
                ["Total Studies", len(studies)],
                ["Archived", (studies["Status"]=="Archived").sum()],
                ["Delivered", (studies["Status"]=="Delivered").sum()],
                ["Errors", (studies.get("Error").notna().sum() if "Error" in studies.columns else 0)],
                ["AI Running", (studies["AIStatus"]=="Running").sum()],
                ["SLA Breaches", sla_breaches]]

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND',(0,1),(-1,-1),colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 12))

        # Add trend chart image
        plt.figure()
        plt.plot(trend_df["ts"], trend_df["Errors"], label="Errors")
        plt.plot(trend_df["ts"], trend_df["SLA_Breaches"], label="SLA Breaches")
        plt.xticks(rotation=45, ha="right")
        plt.legend()
        chart_path = "/tmp/trends.png"
        plt.savefig(chart_path, bbox_inches="tight")
        elements.append(Image(chart_path, width=400, height=200))
        elements.append(Spacer(1, 12))

        # Add audit logs if exist
        if "audit" in st.session_state and st.session_state.audit:
            elements.append(Paragraph("Compliance Audit Logs (Last 10)", styles['Heading2']))
            audit_data = [["Timestamp", "Event"]] + [[a["ts"], a["event"]] for a in st.session_state.audit[-10:]]
            audit_table = Table(audit_data)
            audit_table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            elements.append(audit_table)

        # Add policy evidence table
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Policy Evidence", styles['Heading2']))
        policy_data = [["Modality", "Retention (days)", "Tier", "Encrypt", "Export"]]
        for modality, pol in DEFAULT_POLICIES.items():
            policy_data.append([modality, pol["retention"], pol["tier"], str(pol["encrypt"]), str(pol["export"])] )
        policy_table = Table(policy_data)
        policy_table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(policy_table)

        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Generated on: "+datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles['Normal']))

        doc.build(elements)
        return file_path

    if st.button("⬇️ Download KPI Report as PDF"):
        pdf_path = generate_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Save PDF Report",
                data=f,
                file_name="kpi_report.pdf",
                mime="application/pdf",
            )

# -----------------------------
# Radiologist View
# -----------------------------
if role == "Radiologist":
    st.subheader("My Worklists (Priority & SLA)")
    names = [r["name"] for r in RADIOLOGISTS]
    me = st.selectbox("Radiologist", names)
    mine = studies[(studies["AssignedTo"] == me) & (studies["Status"] == "Delivered")].copy()

    if not mine.empty:
        mine["SLA_Remaining_min"] = [random.randint(-60, 300) for _ in range(len(mine))]
        mine.sort_values(
            by=["Priority", "SLA_Remaining_min"],
            ascending=[True, True],
            inplace=True,
            key=lambda s: s.map({"STAT":0, "Urgent":1, "Routine":2}) if s.name=="Priority" else s
        )

        def highlight_sla(val):
            if val < 0:
                return "color: red; font-weight: bold"
            elif val < 60:
                return "color: orange"
            return ""

        styled = mine[["StudyID","PatientID","Department","Modality","Priority","SLA_Remaining_min","AIStatus"]].head(100).style.applymap(highlight_sla, subset=["SLA_Remaining_min"])
        st.dataframe(styled, use_container_width=True)

        with st.expander("Timeline for a case"):
            pick_id = st.selectbox("Select StudyID", mine["StudyID"].head(20))
            tl = json.loads(studies.loc[studies["StudyID"]==pick_id, "Timeline"].values[0])
            st.json(tl)
    else:
        st.info("No assigned cases yet.")

# -----------------------------
# IT View
# -----------------------------
elif role == "IT":
    st.subheader("Workflow Monitor")
    st.dataframe(studies.head(200), use_container_width=True)

    st.subheader("Errors & Retries")
    errors = studies[studies.get("Error").notna()] if "Error" in studies.columns else pd.DataFrame()
    if errors.empty:
        st.info("No errors currently.")
    else:
        st.dataframe(errors.head(20), use_container_width=True)
        if st.button("Retry All Failed"):
            studies.loc[errors.index, "Error"] = None
            st.success("Retries cleared. Advance workflow to continue.")

    st.subheader("Vendor & Department Mix")
    vc = studies.groupby("Vendor").size().reset_index(name="Studies")
    st.bar_chart(vc.set_index("Vendor"))
    dc = studies.groupby("Department").size().reset_index(name="Studies")
    st.bar_chart(dc.set_index("Department"))

# -----------------------------
# Compliance View
# -----------------------------
else:
    st.subheader("Archiving & Retention")
    by_mod = studies.groupby("Modality").agg(
        Total=("StudyID","count"),
        Archived=("Status", lambda s: (s=="Archived").sum()),
    ).reset_index()
    st.dataframe(by_mod, use_container_width=True)

    st.subheader("Audit Trail")
    if "audit" not in st.session_state:
        st.session_state.audit = []
    st.session_state.audit.append({"ts": datetime.now().isoformat(), "event": "Viewed Compliance"})
    st.json(st.session_state.audit[-10:])

    st.subheader("Policy Evidence")
    st.dataframe(pd.DataFrame.from_dict(DEFAULT_POLICIES, orient="index"), use_container_width=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Simulated hospital workflow: KPIs on top (with SLA breach count & trends, exportable to CSV & PDF with cover page, charts, audit logs, and policies), radiologists see prioritized worklists with SLA highlighting, IT monitors pipelines, compliance reviews retention and audit logs. Use sidebar controls to advance workflow or inject errors.")
