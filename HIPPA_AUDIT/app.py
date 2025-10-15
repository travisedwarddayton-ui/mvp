# app.py
import streamlit as st
import math
from datetime import date
from io import StringIO
import csv
import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Readiness & Compliance Audit", layout="wide")

# ----------------------------------------------------------------
# Initialize Session State
# ----------------------------------------------------------------
def init_state():
    if "metric_flags" not in st.session_state:
        st.session_state.metric_flags = {}
    if "mandatory_flags" not in st.session_state:
        st.session_state.mandatory_flags = {}
    if "baa_records" not in st.session_state:
        st.session_state.baa_records = []
    if "domain_scores" not in st.session_state:
        st.session_state.domain_scores = {}
    if "domain_costs" not in st.session_state:
        st.session_state.domain_costs = {}
init_state()

# ----------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------
def money(n):
    return "${:,.0f}".format(n)

def calc_domain_score_and_cost(domain_name, domain):
    mandatory = domain.get("mandatory_columns", [])
    if mandatory:
        exists_flags = []
        mandatory_cost = 0
        for col in mandatory:
            key = (domain_name, col["name"])
            exists = st.session_state.mandatory_flags.get(key, False)
            exists_flags.append(exists)
            if not exists:
                mandatory_cost += int(col.get("violation_cost_usd", 0))
        mandatory_coverage = (sum(exists_flags) / len(exists_flags)) if exists_flags else 1.0
    else:
        mandatory_coverage = 1.0
        mandatory_cost = 0

    subs = domain.get("subdomains", {})
    total_weight = sum([subs[s]["weight"] for s in subs]) if subs else 0
    metric_score = 0.0
    metric_cost = 0

    for sname, sobj in subs.items():
        s_weight = sobj.get("weight", 0)
        metrics = sobj.get("metrics", [])
        if not metrics:
            continue
        satisfied = 0
        for m in metrics:
            mkey = (domain_name, sname, m["name"])
            ok = st.session_state.metric_flags.get(mkey, False)
            if ok:
                satisfied += 1
            else:
                metric_cost += int(m.get("estimated_penalty", 0))
        sub_score = (satisfied / len(metrics)) if metrics else 1.0
        if total_weight > 0:
            metric_score += sub_score * (s_weight / total_weight)

    readiness = metric_score * mandatory_coverage * 100.0
    total_cost = metric_cost + mandatory_cost
    return readiness, total_cost

def export_summary_csv(domain_scores, domain_costs, overall_score, overall_cost):
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["Domain", "Score (0-100)", "Estimated Exposure ($)"])
    for d, s in domain_scores.items():
        writer.writerow([d, f"{s:.1f}", int(domain_costs.get(d, 0))])
    writer.writerow([])
    writer.writerow(["OVERALL", f"{overall_score:.1f}", int(overall_cost)])
    return sio.getvalue()

def radar_chart(domain_scores):
    labels = list(domain_scores.keys())
    values = [max(0.0, min(100.0, domain_scores.get(d, 0.0))) for d in labels]

    N = len(labels)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]

    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([d.split(" (")[0] for d in labels], fontsize=9)
    ax.set_rlabel_position(0)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8)
    ax.set_ylim(0, 100)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.1)
    return fig

# ----------------------------------------------------------------
# Simplified Example Schema (Trimmed for Space)
# ----------------------------------------------------------------
SCHEMA = {
    "current_state_summary": {
        "assessment_date": "2025-10-15",
        "organization": "Upperline Health",
        "data_sources": [
            {"name": "AthenaHealth EHR", "records": 1850000, "systems": 3},
            {"name": "Billing Platform", "records": 950000, "systems": 1}
        ],
        "total_records": 2800000,
        "total_systems": 4,
        "identified_violations": 8,
        "estimated_total_exposure_usd": 250000
    },
    "compliance_domains": {
        "Administrative Safeguards": {
            "weight": 0.2,
            "description": "Administrative controls for policies and BAAs.",
            "mandatory_columns": [
                {"name": "baa_vendor_id", "description": "Vendor BAA linkage", "violation_cost_usd": 100000},
                {"name": "training_completion_date", "description": "Annual HIPAA training", "violation_cost_usd": 15000}
            ],
            "subdomains": {
                "Business Associate Oversight": {
                    "weight": 0.5,
                    "metrics": [
                        {
                            "name": "% Vendors with Valid BAAs",
                            "observation": "Missing BAAs",
                            "regulation": "HIPAA §164.502(e)",
                            "estimated_penalty": 100000,
                            "recommended_action": "Upload valid BAAs and set expiry alerts",
                            "upload_config": {"enabled": True, "file_types": [".pdf", ".docx"]}
                        }
                    ]
                }
            }
        },
        "Data Integrity & Quality": {
            "weight": 0.2,
            "description": "Ensures ePHI is accurate and complete.",
            "mandatory_columns": [
                {"name": "record_id", "description": "Unique ID", "violation_cost_usd": 10000},
                {"name": "record_checksum", "description": "SHA-256 hash", "violation_cost_usd": 25000}
            ],
            "subdomains": {
                "Completeness": {
                    "weight": 1.0,
                    "metrics": [
                        {
                            "name": "Required Field Population",
                            "observation": "10% missing DOB",
                            "regulation": "21 CFR 11.10(b)",
                            "estimated_penalty": 25000,
                            "recommended_action": "Enforce mandatory validation"
                        }
                    ]
                }
            }
        }
    }
}

DOMAIN_KEYS = list(SCHEMA["compliance_domains"].keys())

# ----------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------
st.title("Data Readiness & Compliance Audit")

# --- Current State Summary ---
summary = SCHEMA["current_state_summary"]
cols = st.columns(4)
cols[0].metric("Assessment Date", summary["assessment_date"])
cols[1].metric("Organization", summary["organization"])
cols[2].metric("Records", f"{summary['total_records']:,}")
cols[3].metric("Exposure", money(summary["estimated_total_exposure_usd"]))

st.markdown("---")

# --- Domains ---
overall_cost = 0
overall_score = 0
total_weight = 0

for domain_name in DOMAIN_KEYS:
    domain = SCHEMA["compliance_domains"][domain_name]
    with st.expander(domain_name, expanded=False):
        st.caption(domain["description"])

        st.subheader("Mandatory Columns")
        for col in domain["mandatory_columns"]:
            key = (domain_name, col["name"])
            exists_flag = st.checkbox(
                f"{col['name']} — {col['description']} ({money(col['violation_cost_usd'])})",
                key=key
            )

        st.subheader("Metrics")
        for sub, sobj in domain["subdomains"].items():
            st.write(f"**{sub}**")
            for m in sobj["metrics"]:
                mkey = (domain_name, sub, m["name"])
                st.session_state.metric_flags[mkey] = st.checkbox(
                    f"{m['name']} — {m['observation']} ({money(m['estimated_penalty'])})",
                    key=mkey
                )

                if m.get("upload_config", {}).get("enabled", False):
                    files = st.file_uploader(
                        f"Upload Files for {m['name']}",
                        type=[t.replace(".", "") for t in m["upload_config"]["file_types"]],
                        accept_multiple_files=True
                    )
                    if files:
                        for f in files:
                            st.success(f"Uploaded {f.name}")

        score, cost = calc_domain_score_and_cost(domain_name, domain)
        st.metric("Domain Readiness Score", f"{score:.1f} / 100")
        st.metric("Estimated Exposure", money(cost))

        overall_score += score * domain["weight"]
        overall_cost += cost
        total_weight += domain["weight"]

st.markdown("---")

# --- Overall Results ---
overall_score = (overall_score / total_weight) if total_weight else 0.0
st.metric("Overall Readiness Index", f"{overall_score:.1f}")
st.metric("Aggregate Exposure", money(overall_cost))

csv_data = export_summary_csv(st.session_state.domain_scores, st.session_state.domain_costs, overall_score, overall_cost)
st.download_button("Download Summary CSV", data=csv_data, file_name="readiness_summary.csv", mime="text/csv")

st.markdown("---")

# --- Spider Web Diagram ---
st.header("Spider Web Diagram")
scores = {}
for domain_name in DOMAIN_KEYS:
    s, _ = calc_domain_score_and_cost(domain_name, SCHEMA["compliance_domains"][domain_name])
    scores[domain_name] = s
fig = radar_chart(scores)
st.pyplot(fig)
