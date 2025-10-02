
import json
import math
from datetime import datetime
from io import StringIO, BytesIO

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Data Management Maturity Intake",
    page_icon="📊",
    layout="wide",
)

# -------------------------------
# Load Config
# -------------------------------
@st.cache_data
@st.cache_data
def load_dimensions():
    return {
        "level_labels": {
            "1": "Initial (Ad hoc)",
            "2": "Managed (Repeatable)",
            "3": "Defined",
            "4": "Quantitatively Managed",
            "5": "Optimized"
        },
        "peer_benchmark": {
            "governance": 3.2,
            "quality": 3.0,
            "metadata": 2.6,
            "architecture": 3.4,
            "security": 3.6,
            "analytics": 3.1
        },
        "dimensions": [ 
            {
  "level_labels": {
    "1": "Initial (Ad hoc)",
    "2": "Managed (Repeatable)",
    "3": "Defined",
    "4": "Quantitatively Managed",
    "5": "Optimized"
  },
  "peer_benchmark": {
    "governance": 3.2,
    "quality": 3.0,
    "metadata": 2.6,
    "architecture": 3.4,
    "security": 3.6,
    "analytics": 3.1
  },
  "dimensions": [
    {
      "key": "governance",
      "name": "Data Governance & Stewardship",
      "icon": "\ud83c\udfdb\ufe0f",
      "weight": 1.2,
      "description": "Ownership, policies, standards, and stewardship for enterprise data assets.",
      "next_steps": [
        "Establish a formal Data Governance Council and RACI for critical domains.",
        "Publish enterprise data policies and standards; enforce via change management.",
        "Stand up a stewardship workflow with issue intake, triage, and remediation SLAs."
      ],
      "sub_dimensions": [
        {
          "key": "ownership",
          "name": "Ownership & Roles",
          "levels": {
            "1": "No defined data owners or stewards; responsibilities unclear.",
            "2": "Some owners identified in key systems; informal responsibilities.",
            "3": "Owners and stewards defined across most domains; onboarding process exists.",
            "4": "Formal RACI; stewardship capacity planned; KPIs for policy adherence.",
            "5": "Ownership embedded in org design; continuous improvement & automation."
          }
        },
        {
          "key": "policy",
          "name": "Policy & Standards",
          "levels": {
            "1": "No enterprise data policies or standards.",
            "2": "Draft policies exist; adoption inconsistent.",
            "3": "Approved policies and standards exist; broad adoption.",
            "4": "Policies measured and enforced; periodic audits.",
            "5": "Policies embedded in SDLC/tooling; auto-conformance checks."
          }
        },
        {
          "key": "issue_mgmt",
          "name": "Issue Management",
          "levels": {
            "1": "Issues handled ad hoc; no central log.",
            "2": "Issues tracked in spreadsheets; limited ownership.",
            "3": "Central issue register with owners and due dates.",
            "4": "Root-cause analysis and trend reporting; SLA-based.",
            "5": "Proactive detection and auto-remediation for recurring issues."
          }
        }
      ]
    },
    {
      "key": "quality",
      "name": "Data Quality",
      "icon": "\u2705",
      "weight": 1.3,
      "description": "Profiling, monitoring, business rules, and remediation across critical data elements.",
      "next_steps": [
        "Profile critical data elements and define data quality dimensions and thresholds.",
        "Automate rule checks and alerting; integrate remediation workflows.",
        "Publish quality scorecards to business owners with trend analysis."
      ],
      "sub_dimensions": [
        {
          "key": "profiling",
          "name": "Profiling & Monitoring",
          "levels": {
            "1": "No routine profiling; unknown data quality.",
            "2": "Periodic manual profiling on select systems.",
            "3": "Automated profiling for key domains with dashboards.",
            "4": "Continuous monitoring with alerts and SLA responses.",
            "5": "Predictive quality with prevention embedded in pipelines."
          }
        },
        {
          "key": "rules",
          "name": "Business Rules & Thresholds",
          "levels": {
            "1": "No documented rules or thresholds.",
            "2": "Some rules defined by teams; inconsistent.",
            "3": "Enterprise rule library with owners and change control.",
            "4": "Rules versioned, tested, and measured for impact.",
            "5": "Rules auto-generated from metadata/lineage; continuous learning."
          }
        },
        {
          "key": "remediation",
          "name": "Remediation Workflow",
          "levels": {
            "1": "Manual fixes; no systematic approach.",
            "2": "Email-driven fixes; scattered ownership.",
            "3": "Ticketed workflow with owners and SLAs.",
            "4": "Root-cause standardization; playbooks for common issues.",
            "5": "Automated remediation for recurring patterns; human-in-the-loop."
          }
        }
      ]
    },
    {
      "key": "metadata",
      "name": "Metadata & Catalog",
      "icon": "\ud83d\uddc2\ufe0f",
      "weight": 1.1,
      "description": "Business glossary, technical lineage, and catalog practices to enable discoverability and trust.",
      "next_steps": [
        "Stand up a data catalog; seed with priority systems and glossary terms.",
        "Define lineage for critical pipelines; connect glossary \u2194 technical assets.",
        "Enable social features (ratings, certifications) to drive adoption."
      ],
      "sub_dimensions": [
        {
          "key": "glossary",
          "name": "Business Glossary",
          "levels": {
            "1": "No glossary; terms ambiguous across teams.",
            "2": "Team-specific glossaries; inconsistent definitions.",
            "3": "Enterprise glossary with owners and review cadence.",
            "4": "Glossary integrated with BI and catalog; change control in place.",
            "5": "Glossary linked to policies, controls, and KPIs; usage analytics."
          }
        },
        {
          "key": "lineage",
          "name": "Technical Lineage",
          "levels": {
            "1": "Unknown lineage; tribal knowledge.",
            "2": "Manual lineage diagrams for select pipelines.",
            "3": "Tool-supported lineage for priority datasets.",
            "4": "End-to-end lineage integrated into CI/CD and impact analysis.",
            "5": "Automated lineage with quality gates and drift detection."
          }
        },
        {
          "key": "cataloging",
          "name": "Cataloging Practices",
          "levels": {
            "1": "No central catalog or inventory.",
            "2": "Partial inventory; not actively maintained.",
            "3": "Central catalog with curation responsibilities.",
            "4": "Certification, usage telemetry, and deprecation lifecycle.",
            "5": "Active curation with recommendations and semantic enrichment."
          }
        }
      ]
    },
    {
      "key": "architecture",
      "name": "Architecture & Integration",
      "icon": "\ud83c\udfd7\ufe0f",
      "weight": 1.0,
      "description": "Integration patterns, platform reliability, and interoperability across the data estate.",
      "next_steps": [
        "Standardize integration patterns (batch, CDC, streaming) with reference designs.",
        "Harden environments with IaC, observability, and cost governance.",
        "Adopt domain-oriented data products with clear SLAs and APIs."
      ],
      "sub_dimensions": [
        {
          "key": "integration",
          "name": "Integration Methods",
          "levels": {
            "1": "Ad hoc file drops and manual imports.",
            "2": "Point-to-point integrations; fragile dependencies.",
            "3": "Standardized patterns (ETL/ELT/CDC) for core systems.",
            "4": "Streaming/CDC and orchestration; reusable connectors.",
            "5": "Self-serve data products and federated gateways."
          }
        },
        {
          "key": "platform",
          "name": "Platform Reliability & Ops",
          "levels": {
            "1": "Unreliable pipelines; outages common.",
            "2": "Basic monitoring; manual recoveries.",
            "3": "Observability and alerting; RTO/RPO targets",
            "4": "IaC, blue/green, cost guardrails; routine DR tests.",
            "5": "SLOs with error budgets; automated scaling and resilience."
          }
        },
        {
          "key": "interoperability",
          "name": "Interoperability",
          "levels": {
            "1": "Closed systems; custom adapters everywhere.",
            "2": "Some APIs; inconsistent standards.",
            "3": "Adopts open standards (FHIR, HL7, DICOM) in key domains.",
            "4": "Enterprise-level contract testing and schema governance.",
            "5": "Semantic interoperability and knowledge graph layer."
          }
        }
      ]
    },
    {
      "key": "security",
      "name": "Security & Privacy",
      "icon": "\ud83d\udd10",
      "weight": 1.2,
      "description": "Access controls, privacy engineering, and compliance-aligned data protection.",
      "next_steps": [
        "Implement role-based access and least privilege with periodic reviews.",
        "Data classification and masking for sensitive attributes; audit logging.",
        "Automate privacy impact assessments and consent management."
      ],
      "sub_dimensions": [
        {
          "key": "access",
          "name": "Access Control",
          "levels": {
            "1": "Shared credentials; over-privileged access.",
            "2": "Role-based access for some systems.",
            "3": "Central IAM with periodic access reviews.",
            "4": "Attribute-based access; fine-grained policies in pipelines.",
            "5": "Just-in-time access with continuous verification."
          }
        },
        {
          "key": "privacy",
          "name": "Privacy Engineering",
          "levels": {
            "1": "No systematic handling of PII/PHI.",
            "2": "Manual redaction/masking as needed.",
            "3": "Standardized masking/tokenization for sensitive data.",
            "4": "Differential privacy/k-anonymity considered for analytics.",
            "5": "Privacy by design with automated policy enforcement."
          }
        },
        {
          "key": "compliance",
          "name": "Compliance Alignment",
          "levels": {
            "1": "Unclear regulatory obligations.",
            "2": "Reactive compliance fixes post-audit.",
            "3": "Mapped controls to regulations (HIPAA, GDPR, etc.).",
            "4": "Continuous control monitoring and evidence collection.",
            "5": "Integrated GRC with automated attestations."
          }
        }
      ]
    },
    {
      "key": "analytics",
      "name": "Analytics & AI Readiness",
      "icon": "\ud83e\udd16",
      "weight": 1.0,
      "description": "Business intelligence adoption, ML/AI foundations, and responsible AI practices.",
      "next_steps": [
        "Harden data marts and semantic layers for governed BI self-service.",
        "Establish ML ops foundations (feature store, experiment tracking, model registry).",
        "Adopt responsible AI guidelines and bias/robustness evaluation."
      ],
      "sub_dimensions": [
        {
          "key": "bi_adoption",
          "name": "BI Adoption",
          "levels": {
            "1": "Reports built manually; spreadsheets dominate.",
            "2": "Central BI exists; low adoption.",
            "3": "Departmental self-service with governed datasets.",
            "4": "Enterprise metrics store; usage telemetry drives improvements.",
            "5": "Decision automation with business-owned analytics products."
          }
        },
        {
          "key": "ml_foundations",
          "name": "ML/AI Foundations",
          "levels": {
            "1": "Ad hoc notebooks; no formal lifecycle.",
            "2": "Isolated pilots; limited reproducibility.",
            "3": "Versioned data/models; basic MLOps in place.",
            "4": "Feature store, CI/CD for ML, monitoring of drift/perf.",
            "5": "Responsible AI by default; continuous training and governance."
          }
        },
        {
          "key": "ethics",
          "name": "Responsible AI",
          "levels": {
            "1": "No policy for AI ethics/bias.",
            "2": "Awareness but no formal practices.",
            "3": "Documented guidelines and review board.",
            "4": "Bias/robustness tests integrated in lifecycle.",
            "5": "Auditable AI with human-in-the-loop and red-teaming."
          }
        }
      ]
    }
  ]
}
        ]
    }

cfg = load_dimensions()


cfg = load_dimensions()

DIMENSIONS = cfg["dimensions"]
LEVEL_LABELS = cfg["level_labels"]  # 1..5
PEER_BENCHMARK = cfg.get("peer_benchmark", {})  # optional benchmark overlay 1..5 per dimension
OVERALL_WEIGHTS = {d["key"]: d.get("weight", 1.0) for d in DIMENSIONS}

# -------------------------------
# Helper Functions
# -------------------------------
def maturity_to_text(level: float) -> str:
    # map to label (round to nearest int 1..5)
    k = int(round(level))
    k = max(1, min(5, k))
    return LEVEL_LABELS[str(k)]

def compute_scores(responses: dict):
    """Compute per sub-dimension, per dimension, and overall maturity scores (1..5)."""
    sub_scores = {}
    dim_scores = {}
    for dim in DIMENSIONS:
        dkey = dim["key"]
        sub_list = dim["sub_dimensions"]
        d_scores = []
        for sub in sub_list:
            skey = f"{dkey}:{sub['key']}"
            val = responses.get(skey, None)
            if val is None:
                continue
            d_scores.append(val)
            sub_scores[skey] = val
        dim_scores[dkey] = sum(d_scores)/len(d_scores) if d_scores else 0.0

    # overall weighted average, plus weakest link note
    total_w = 0.0
    total = 0.0
    for dkey, dscore in dim_scores.items():
        w = OVERALL_WEIGHTS.get(dkey, 1.0)
        total += dscore * w
        total_w += w
    overall = (total / total_w) if total_w else 0.0
    weakest = min(dim_scores.items(), key=lambda kv: kv[1]) if dim_scores else (None, 0.0)

    return sub_scores, dim_scores, overall, weakest

def next_step_recommendations(dim_scores):
    """Generate targeted next steps for any dimension < 3.5."""
    recs = []
    for dim in DIMENSIONS:
        dkey = dim["key"]
        score = dim_scores.get(dkey, 0.0)
        if score < 3.5:
            recs.append({
                "dimension": dim["name"],
                "score": score,
                "recommendations": dim.get("next_steps", [])
            })
    return recs

def build_radar(dim_scores):
    cats = [d["name"] for d in DIMENSIONS]
    vals = [dim_scores.get(d["key"], 0.0) for d in DIMENSIONS]
    # Close the radar
    cats += [cats[0]]
    vals += [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals, theta=cats, fill="toself", name="Your score"))
    # Optional peer overlay
    if PEER_BENCHMARK:
        bvals = [PEER_BENCHMARK.get(d["key"], None) for d in DIMENSIONS]
        if all(v is not None for v in bvals):
            bvals += [bvals[0]]
            fig.add_trace(go.Scatterpolar(r=bvals, theta=cats, fill="none", name="Peer benchmark"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5], tickvals=[1,2,3,4,5])), showlegend=True, height=520)
    return fig

def build_heatmap(responses):
    # Build a matrix of sub-dimensions (rows) vs score, grouped by dimension
    rows = []
    y_labels = []
    x_labels = ["Score (1-5)"]
    for dim in DIMENSIONS:
        for sub in dim["sub_dimensions"]:
            skey = f"{dim['key']}:{sub['key']}"
            score = responses.get(skey, 0.0)
            rows.append([score])
            y_labels.append(f"{dim['name']} — {sub['name']}")
    z = rows
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        zmin=1, zmax=5,
        colorbar=dict(title="Maturity")
    ))
    fig.update_layout(height=640, yaxis=dict(autorange="reversed"))
    return fig

def overall_badge(overall):
    label = maturity_to_text(overall)
    if overall >= 4.5:
        color = "✅"
    elif overall >= 3.5:
        color = "🟢"
    elif overall >= 2.5:
        color = "🟡"
    else:
        color = "🟠"
    return f"{color} **Overall Level {overall:.1f} — {label}**"

def to_results_dataframe(responses, dim_scores, overall):
    rows = []
    for dim in DIMENSIONS:
        dkey = dim["key"]
        # dimension row
        rows.append({
            "type": "dimension",
            "key": dkey,
            "name": dim["name"],
            "score": dim_scores.get(dkey, 0.0),
            "descriptor": maturity_to_text(dim_scores.get(dkey, 0.0))
        })
        for sub in dim["sub_dimensions"]:
            skey = f"{dkey}:{sub['key']}"
            rows.append({
                "type": "sub-dimension",
                "key": skey,
                "name": f"{dim['name']} — {sub['name']}",
                "score": responses.get(skey, 0.0),
                "descriptor": sub["levels"].get(str(int(round(responses.get(skey, 0.0) or 1)))),  # nearest descriptor
            })
    rows.append({
        "type": "overall",
        "key": "overall",
        "name": "Overall",
        "score": overall,
        "descriptor": maturity_to_text(overall)
    })
    return rows

# -------------------------------
# Sidebar (Meta & Actions)
# -------------------------------
st.sidebar.title("📋 Assessment Controls")

with st.sidebar.popover("ℹ️ How scoring works"):
    st.markdown("""
- Each **sub-dimension** is scored **1–5** using anchored descriptors.
- A **dimension score** is the average of its sub-dimensions.
- The **overall score** is a weighted average across dimensions.
- Graphs update **in real time** as you answer.
""")

client_name = st.sidebar.text_input("Client / Org name", value="Acme Health")
assessor = st.sidebar.text_input("Assessor", value="Travis Dayton")
date_str = st.sidebar.text_input("Assessment date", value=datetime.now().strftime("%Y-%m-%d"))
peer_toggle = st.sidebar.checkbox("Show peer benchmark overlay", value=True)

st.sidebar.divider()

# Results export
export_requested = st.sidebar.checkbox("Prepare results for export", value=False)

# -------------------------------
# Main Layout
# -------------------------------
st.title("📊 Data Management Maturity — Interactive Intake")
st.caption("Answer each area with the statement that best describes your current practice. Charts update live.")

responses = {}

# -------------------------------
# Intake Form (Interactive)
# -------------------------------
for dim in DIMENSIONS:
    st.subheader(f"{dim['icon']} {dim['name']}")
    cols = st.columns([2, 1], vertical_alignment="top")
    with cols[0]:
        st.markdown(dim["description"])
    with cols[1]:
        st.markdown(f"**Weight:** {dim.get('weight',1.0)}")

    with st.expander("Answer the sub-dimensions", expanded=True):
        for sub in dim["sub_dimensions"]:
            skey = f"{dim['key']}:{sub['key']}"
            st.markdown(f"**{sub['name']}**")
            # Anchored radio with 5 descriptors
            options = [1,2,3,4,5]
            labels = [f"{i}. {sub['levels'][str(i)]}" for i in options]
            # Show radio with index labels
            idx = st.radio(
                label=f"Choose the statement that best matches",
                options=list(range(5)),
                format_func=lambda i: labels[i],
                key=skey
            )
            responses[skey] = options[idx]
            st.markdown("---")

    # Optional evidence upload
    with st.expander("📎 (Optional) Upload evidence (policies, screenshots, logs)"):
        st.file_uploader(
            "Drop files here (not uploaded to server unless you implement storage)",
            type=["pdf","docx","pptx","xlsx","csv","png","jpg"],
            accept_multiple_files=True,
            key=f"upload-{dim['key']}"
        )

    st.divider()

# -------------------------------
# Compute Scores
# -------------------------------
sub_scores, dim_scores, overall, weakest = compute_scores(responses)

# -------------------------------
# KPI Header
# -------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(overall_badge(overall))
with col2:
    if weakest[0] is not None:
        wdim_key, wscore = weakest
        wname = next((d["name"] for d in DIMENSIONS if d["key"]==wdim_key), wdim_key)
        st.markdown(f"🔎 **Weakest area:** {wname} — {wscore:.1f}")
with col3:
    # Progress to next whole level
    next_level = math.floor(overall) + 1 if overall < 5 else 5
    to_next = max(0.0, next_level - overall)
    prog = (overall - math.floor(overall)) if overall < 5 else 1.0
    st.markdown(f"🎯 **Progress to Level {next_level}:**")
    st.progress(min(max(prog,0.0),1.0), text=f"{(prog*100):.0f}% toward Level {next_level}")

st.markdown("---")

# -------------------------------
# Charts
# -------------------------------
left, right = st.columns([1,1])

with left:
    st.markdown("### 🧭 Radar (by dimension)")
    if not peer_toggle:
        # Remove overlay if user turned it off
        backup = cfg.get("peer_benchmark", {}).copy()
        cfg["peer_benchmark"] = {}
        fig = build_radar(dim_scores)
        cfg["peer_benchmark"] = backup
    else:
        fig = build_radar(dim_scores)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### 🔥 Heatmap (by sub-dimension)")
    h = build_heatmap(responses)
    st.plotly_chart(h, use_container_width=True)

# -------------------------------
# Recommendations
# -------------------------------
st.markdown("### 🧩 Targeted Recommendations")
recs = next_step_recommendations(dim_scores)
if recs:
    for r in recs:
        with st.expander(f"Improve **{r['dimension']}** (current {r['score']:.1f})"):
            for i, step in enumerate(r["recommendations"], start=1):
                st.markdown(f"- {step}")
else:
    st.success("Nice! All dimensions are ≥ 3.5. Consider optimization/automation roadmaps.")

# -------------------------------
# Export
# -------------------------------
if export_requested:
    st.markdown("### ⤵️ Export Results")
    rows = to_results_dataframe(responses, dim_scores, overall)
    out_df = px.data.tips()  # placeholder to keep namespace warm
    # Build CSV
    import pandas as pd
    df = pd.DataFrame(rows)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV (scores + descriptors)",
        data=csv_bytes,
        file_name=f"{client_name.replace(' ','_')}_DMM_{date_str}.csv",
        mime="text/csv"
    )

    # Export JSON
    export_payload = {
        "client": client_name,
        "assessor": assessor,
        "date": date_str,
        "dimension_scores": dim_scores,
        "overall": overall,
        "level_text": maturity_to_text(overall),
        "responses": responses,
    }
    json_bytes = json.dumps(export_payload, indent=2).encode("utf-8")
    st.download_button(
        "Download JSON (detailed results)",
        data=json_bytes,
        file_name=f"{client_name.replace(' ','_')}_DMM_{date_str}.json",
        mime="application/json"
    )

st.markdown("---")
st.caption("© 2025 Realtime Data Solutions — Data Management Maturity Intake")
