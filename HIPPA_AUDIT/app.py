# app.py
import streamlit as st
import pandas as pd
import math
from datetime import date
from io import StringIO
import csv
import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Readiness & Compliance Audit", layout="wide")

# ======================================================================
# Schema (Executive Summary + Compliance Domains + Visual Summary)
# ======================================================================
SCHEMA = {
    "current_state_summary": {
        "assessment_date": "2025-10-15",
        "organization": "Upperline Health",
        "data_sources": [
            {"name": "AthenaHealth EHR", "records": 1850000, "systems": 3},
            {"name": "Billing Platform", "records": 950000, "systems": 1},
            {"name": "Lab Interfaces (HL7)", "records": 425000, "systems": 2}
        ],
        "total_records": 3225000,
        "total_systems": 6,
        "identified_violations": 37,
        "violations_by_category": {
            "Administrative": 8,
            "Technical": 10,
            "Physical": 4,
            "Integrity": 5,
            "Interoperability": 3,
            "Signatures": 2,
            "Infonomics": 5
        },
        "estimated_total_exposure_usd": 845000,
        "top_risks": [
            "Missing Business Associate Agreements (BAAs)",
            "Unencrypted PHI storage in local cache",
            "Incomplete audit trail for EHR modifications",
            "Lack of checksum validation for data integrity"
        ]
    },

    "compliance_domains": {
        # 1) Administrative Safeguards
        "Administrative Safeguards (HIPAA §164.308)": {
            "weight": 0.15,
            "description": "Administrative controls covering risk analysis, workforce training, and vendor oversight.",
            "mandatory_columns": [
                {"name": "last_modified_by", "description": "Who changed PHI/governance docs (accountability).", "violation_cost_usd": 5000},
                {"name": "last_modified_date", "description": "When record/document last changed (audit trail).", "violation_cost_usd": 10000},
                {"name": "record_version", "description": "Version control for SOPs and risk assessments.", "violation_cost_usd": 7500},
                {"name": "baa_vendor_id", "description": "FK linking PHI/system to vendor for BAA proof.", "violation_cost_usd": 100000},
                {"name": "training_completion_date", "description": "Workforce HIPAA training date.", "violation_cost_usd": 15000}
            ],
            "subdomains": {
                "Risk Management Program": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Annual Risk Analysis",
                            "observation": "No HIPAA risk analysis completed within the last 12 months.",
                            "regulation": "HIPAA §164.308(a)(1)(ii)(A)",
                            "impact_category": "Legal / Financial",
                            "estimated_penalty": 50000,
                            "impact_description": "OCR fines and corrective action plans.",
                            "recommended_action": "Conduct and document an annual security risk analysis."
                        }
                    ]
                },
                "Business Associate Oversight": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "% of Vendors with Valid BAAs",
                            "observation": "One or more vendors lack current BAAs.",
                            "regulation": "HIPAA §164.502(e)",
                            "impact_category": "Legal / Reputational",
                            "estimated_penalty": 100000,
                            "impact_description": "Missing BAAs often result in six-figure settlements.",
                            "recommended_action": "Execute and upload BAAs; set renewal alerts.",
                            "upload_config": {
                                "enabled": True,
                                "file_types": [".pdf", ".docx", ".png", ".jpg"],
                                "metadata_fields": {
                                    "vendor_name": "string",
                                    "signed_date": "date",
                                    "expiration_date": "date",
                                    "contact_person": "string",
                                    "contact_email": "string"
                                },
                                "validation_rules": {
                                    "require_vendor_name": True,
                                    "require_expiration_date": True,
                                    "flag_if_expired": True
                                }
                            }
                        }
                    ]
                },
                "Workforce Security & Training": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Training Completion Rate",
                            "observation": "Under 90% of staff completed annual HIPAA training.",
                            "regulation": "HIPAA §164.308(a)(5)(i)",
                            "impact_category": "Operational / Legal",
                            "estimated_penalty": 15000,
                            "impact_description": "Higher breach likelihood and OCR findings.",
                            "recommended_action": "Automate training tracking; enforce recertification."
                        }
                    ]
                }
            }
        },

        # 2) Technical Safeguards
        "Technical Safeguards (HIPAA §164.312 & 21 CFR 11.10)": {
            "weight": 0.20,
            "description": "Access control, authentication, encryption, and audit trails for HIPAA and FDA Part 11.",
            "mandatory_columns": [
                {"name": "user_id", "description": "Unique authenticated user per transaction.", "violation_cost_usd": 10000},
                {"name": "access_role", "description": "Role-based access control for least privilege.", "violation_cost_usd": 25000},
                {"name": "mfa_enabled", "description": "Multi-factor authentication status.", "violation_cost_usd": 25000},
                {"name": "encryption_status", "description": "AES-256 at rest / TLS in transit applied to ePHI.", "violation_cost_usd": 150000},
                {"name": "audit_log_id", "description": "Immutable link to audit entry for the event.", "violation_cost_usd": 50000}
            ],
            "subdomains": {
                "Access Control & Authentication": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Unique ID and MFA Enforcement",
                            "observation": "Shared accounts or missing MFA detected.",
                            "regulation": "HIPAA §164.312(d); 21 CFR 11.10(d)",
                            "impact_category": "Security / Operational",
                            "estimated_penalty": 25000,
                            "impact_description": "Unauthorized access is a leading breach vector.",
                            "recommended_action": "Enforce unique IDs and MFA for all users."
                        }
                    ]
                },
                "Encryption & Transmission Security": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Encryption-at-Rest Compliance",
                            "observation": "PHI stored unencrypted on local database.",
                            "regulation": "HIPAA §164.312(a)(2)(iv)",
                            "impact_category": "Legal / Financial",
                            "estimated_penalty": 150000,
                            "impact_description": "Unencrypted breaches regularly incur six-figure penalties.",
                            "recommended_action": "Enable AES-256 and key rotation."
                        }
                    ]
                },
                "System Audit Trails": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "Immutable Audit Logs",
                            "observation": "No tamper-evident change logs.",
                            "regulation": "21 CFR 11.10(e–k); HIPAA §164.312(b)",
                            "impact_category": "Legal / Operational",
                            "estimated_penalty": 50000,
                            "impact_description": "FDA warning letters and OCR findings for missing logs.",
                            "recommended_action": "Implement append-only audit store with time sync."
                        }
                    ]
                }
            }
        },

        # 3) Physical & Infrastructure Safeguards
        "Physical & Infrastructure Safeguards (HIPAA §164.310)": {
            "weight": 0.10,
            "description": "Facility, hardware, environment; availability and secure disposal of PHI media.",
            "mandatory_columns": [
                {"name": "hosting_environment", "description": "Cloud/on-prem; maps to facility access controls.", "violation_cost_usd": 5000},
                {"name": "backup_frequency_days", "description": "Interval for full backups.", "violation_cost_usd": 10000},
                {"name": "backup_last_tested_date", "description": "Most recent successful restore test date.", "violation_cost_usd": 15000},
                {"name": "system_uptime_percent", "description": "Monthly availability to evidence resilience.", "violation_cost_usd": 5000},
                {"name": "retention_expiration_date", "description": "Data disposal schedule per policy/contract.", "violation_cost_usd": 25000}
            ],
            "subdomains": {
                "Contingency Planning": {
                    "weight": 0.40,
                    "metrics": [
                        {
                            "name": "Backup Verification",
                            "observation": "No quarterly restore tests documented.",
                            "regulation": "HIPAA §164.308(a)(7)",
                            "impact_category": "Operational / Legal",
                            "estimated_penalty": 10000,
                            "impact_description": "Contingency plan non-compliance.",
                            "recommended_action": "Quarterly restores with logs and sign-off."
                        }
                    ]
                },
                "Device & Media Control": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "Secure Media Disposal",
                            "observation": "Retired servers not wiped per NIST 800-88.",
                            "regulation": "HIPAA §164.310(d)(2)(i)",
                            "impact_category": "Legal / Financial",
                            "estimated_penalty": 25000,
                            "impact_description": "PHI exposure on disposed media triggers breach duties.",
                            "recommended_action": "Certified destruction and chain-of-custody logs."
                        }
                    ]
                }
            }
        },

        # 4) Data Integrity & Quality
        "Data Integrity & Quality (HIPAA §164.312(c)(1); 21 CFR 11.10(b))": {
            "weight": 0.15,
            "description": "Assures electronic records are accurate, complete, and protected from improper alteration or destruction.",
            "mandatory_columns": [
                {"name": "record_id", "description": "Immutable unique ID for each record.", "violation_cost_usd": 10000},
                {"name": "record_checksum", "description": "Cryptographic hash (e.g., SHA-256) for tamper detection.", "violation_cost_usd": 25000},
                {"name": "created_date", "description": "When the record was created (chronology).", "violation_cost_usd": 5000},
                {"name": "last_modified_date", "description": "When the record last changed (alteration tracking).", "violation_cost_usd": 10000},
                {"name": "last_modified_by", "description": "Who changed the record (attribution).", "violation_cost_usd": 7500},
                {"name": "validation_status", "description": "Pass/fail integrity check result.", "violation_cost_usd": 10000},
                {"name": "validation_timestamp", "description": "Last time integrity validation executed.", "violation_cost_usd": 7500},
                {"name": "system_signature", "description": "System-generated signature binding record and version.", "violation_cost_usd": 20000}
            ],
            "subdomains": {
                "Completeness & Accuracy Controls": {
                    "weight": 0.40,
                    "metrics": [
                        {
                            "name": "Required Field Population",
                            "observation": "10% of patient files missing MRN/diagnosis.",
                            "regulation": "21 CFR 11.10(b)",
                            "impact_category": "Financial / Compliance",
                            "estimated_penalty": 25000,
                            "impact_description": "Can invalidate electronic submissions; impacts CMS measures.",
                            "recommended_action": "Hard-stop validations and stewardship review."
                        }
                    ]
                },
                "Alteration & Destruction Protection": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "Hash Verification",
                            "observation": "No checksum verification for data-at-rest.",
                            "regulation": "HIPAA §164.312(c)(1)",
                            "impact_category": "Legal / Security",
                            "estimated_penalty": 25000,
                            "impact_description": "No tamper detection for ePHI.",
                            "recommended_action": "Generate and periodically verify hashes."
                        }
                    ]
                },
                "Audit & Traceability Controls": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "Change Traceability",
                            "observation": "Modifications not linked to audit entries.",
                            "regulation": "21 CFR 11.10(e); HIPAA §164.312(b)",
                            "impact_category": "Legal / Operational",
                            "estimated_penalty": 30000,
                            "impact_description": "Cannot verify proper handling of ePHI.",
                            "recommended_action": "Immutable append-only audit with time sync."
                        }
                    ]
                }
            }
        },

        # 5) Interoperability & Exchange
        "Interoperability & Electronic Exchange (21 CFR 11.30; ONC Cures Act)": {
            "weight": 0.10,
            "description": "Standardized, patient-accessible data exchange; API readiness and terminology normalization.",
            "mandatory_columns": [
                {"name": "fhir_resource_type", "description": "Mapped FHIR resource.", "violation_cost_usd": 15000},
                {"name": "standard_mapping_status", "description": "Mapping completeness to LOINC/SNOMED/RxNorm.", "violation_cost_usd": 10000},
                {"name": "last_sync_timestamp", "description": "Most recent API/interface exchange time.", "violation_cost_usd": 5000},
                {"name": "external_system_id", "description": "Partner system identifier for lineage.", "violation_cost_usd": 5000}
            ],
            "subdomains": {
                "FHIR / HL7 Readiness": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "API Endpoint Coverage",
                            "observation": "Observation endpoint not implemented.",
                            "regulation": "ONC Cures Act; 21 CFR 11.30",
                            "impact_category": "Operational / Legal",
                            "estimated_penalty": 15000,
                            "impact_description": "May affect program eligibility and incentives.",
                            "recommended_action": "Deploy certified endpoints and monitor uptime/errors."
                        }
                    ]
                },
                "Terminology Normalization": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Standard Code Utilization",
                            "observation": "Labs lack LOINC; diagnoses not mapped to SNOMED.",
                            "regulation": "USCDI / ONC Interop Guidance",
                            "impact_category": "Operational / Financial",
                            "estimated_penalty": 10000,
                            "impact_description": "Breaks quality reporting and exchange semantics.",
                            "recommended_action": "Normalize during ETL; maintain code dictionaries."
                        }
                    ]
                }
            }
        },

        # 6) Electronic Signatures
        "Electronic Signatures & Attribution (21 CFR 11.100–11.200)": {
            "weight": 0.10,
            "description": "Non-repudiation and signer accountability for approvals, authorship, and reviews.",
            "mandatory_columns": [
                {"name": "electronic_signature", "description": "Signature token/hash binding signer to record.", "violation_cost_usd": 30000},
                {"name": "signature_meaning", "description": "Purpose of signature (approval, review, authorship).", "violation_cost_usd": 10000},
                {"name": "signature_timestamp", "description": "Date/time of signature.", "violation_cost_usd": 5000},
                {"name": "signature_user_id", "description": "Authenticated signer identity.", "violation_cost_usd": 10000}
            ],
            "subdomains": {
                "Identity Verification": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Dual-Credential Verification",
                            "observation": "Single-factor signatures in use.",
                            "regulation": "21 CFR 11.100(a)",
                            "impact_category": "Legal / Security",
                            "estimated_penalty": 20000,
                            "impact_description": "Signatures may be deemed invalid by FDA.",
                            "recommended_action": "Require password plus biometric or token; periodic re-auth."
                        }
                    ]
                },
                "Signature Linkage": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Signature to Version Binding",
                            "observation": "Signatures not bound to specific record version.",
                            "regulation": "21 CFR 11.70",
                            "impact_category": "Legal / Operational",
                            "estimated_penalty": 15000,
                            "impact_description": "Weak linkage undermines record trust.",
                            "recommended_action": "Bind signature to checksum, version, and user."
                        }
                    ]
                }
            ]
        },

        # 7) Information Governance & Infonomics
        "Information Governance & Infonomics (Value of Data)": {
            "weight": 0.15,
            "description": "Translates compliance maturity into measurable ROI, reduced denials, and operational gains.",
            "mandatory_columns": [
                {"name": "financial_impact_estimate", "description": "Estimated dollar impact per issue/remediation.", "violation_cost_usd": 10000},
                {"name": "readiness_score", "description": "Computed Data Readiness Index (0–100).", "violation_cost_usd": 5000},
                {"name": "risk_level", "description": "LOW/MEDIUM/HIGH exposure categorization.", "violation_cost_usd": 5000}
            ],
            "subdomains": {
                "Data ROI Tracking": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Claim Denial Correlation",
                            "observation": "No linkage of data errors to denial rates.",
                            "regulation": "CMS Program Integrity (best practice)",
                            "impact_category": "Financial",
                            "estimated_penalty": 50000,
                            "impact_description": "Five to ten percent margin erosion from preventable denials.",
                            "recommended_action": "Correlate data quality issues with denials; prioritize fixes."
                        }
                    ]
                },
                "Portfolio Readiness Benchmarking": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Clinic Readiness Index",
                            "observation": "No standardized scoring across sites.",
                            "regulation": "Governance best practice",
                            "impact_category": "Operational / Strategic",
                            "estimated_penalty": 10000,
                            "impact_description": "Hard to prioritize remediation and M&A sequencing.",
                            "recommended_action": "Adopt uniform scoring and heatmaps across clinics."
                        }
                    ]
                }
            ]
        }
    },

    "visual_summary": {
        "diagram_type": "spider_web",
        "description": "Radar chart illustrating readiness level per compliance domain (0–100)."
    }
}

# ======================================================================
# State and Helpers
# ======================================================================
def init_state():
    if "metric_flags" not in st.session_state:
        st.session_state.metric_flags = {}     # (domain, subdomain, metric) -> bool
    if "mandatory_flags" not in st.session_state:
        st.session_state.mandatory_flags = {}  # (domain, column_name) -> bool
    if "baa_records" not in st.session_state:
        st.session_state.baa_records = []      # list of dicts
    if "domain_scores" not in st.session_state:
        st.session_state.domain_scores = {}    # domain -> float
    if "domain_costs" not in st.session_state:
        st.session_state.domain_costs = {}     # domain -> float

def money(n):
    return "${:,.0f}".format(n)

def calc_domain_score_and_cost(domain_name, domain_obj):
    # Mandatory coverage
    mandatory = domain_obj.get("mandatory_columns", [])
    mandatory_cost = 0
    if mandatory:
        flags = []
        for col in mandatory:
            key = (domain_name, col["name"])
            exists = st.session_state.mandatory_flags.get(key, False)
            flags.append(exists)
            if not exists:
                mandatory_cost += int(col.get("violation_cost_usd", 0))
        mandatory_coverage = (sum(flags) / len(flags)) if flags else 1.0
    else:
        mandatory_coverage = 1.0

    # Metrics weighted by subdomain weights
    subs = domain_obj.get("subdomains", {})
    total_w = sum([sobj.get("weight", 0) for sobj in subs.values()]) if subs else 0
    metric_score = 0.0
    metric_cost = 0
    for sname, sobj in subs.items():
        s_weight = sobj.get("weight", 0)
        metrics = sobj.get("metrics", [])
        if not metrics:
            continue
        satisfied = 0
        for m in metrics:
            key = (domain_name, sname, m["name"])
            ok = st.session_state.metric_flags.get(key, False)
            if ok:
                satisfied += 1
            else:
                metric_cost += int(m.get("estimated_penalty", 0))
        sub_pct = (satisfied / len(metrics)) if metrics else 1.0
        if total_w > 0:
            metric_score += sub_pct * (s_weight / total_w)

    readiness = metric_score * mandatory_coverage * 100.0
    total_cost = mandatory_cost + metric_cost
    return readiness, total_cost

def export_summary_csv(domain_scores, domain_costs, overall_score, overall_cost):
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["Domain", "Score (0-100)", "Estimated Exposure ($)"])
    for d in domain_scores:
        writer.writerow([d, f"{domain_scores[d]:.1f}", int(domain_costs.get(d, 0))])
    writer.writerow([])
    writer.writerow(["OVERALL", f"{overall_score:.1f}", int(overall_cost)])
    return sio.getvalue()

def radar_chart(domain_scores):
    labels = list(domain_scores.keys())
    values = [max(0.0, min(100.0, domain_scores.get(d, 0.0))) for d in labels]

    N = len(labels)
    if N == 0:
        fig = plt.figure(figsize=(6,6))
        return fig

    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]

    fig = plt.figure(figsize=(7,7))
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

init_state()

# ======================================================================
# UI — Current State Summary
# ======================================================================
st.title("Data Readiness & Compliance Audit (HIPAA + 21 CFR Part 11)")

css = SCHEMA["current_state_summary"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Assessment Date", css["assessment_date"])
c2.metric("Organization", css["organization"])
c3.metric("Total Records", f"{css['total_records']:,}")
c4.metric("Estimated Exposure", money(css["estimated_total_exposure_usd"]))

ds_cols = st.columns(len(css["data_sources"]))
for i, ds in enumerate(css["data_sources"]):
    with ds_cols[i]:
        st.subheader(ds["name"])
        st.write(f"Records: {ds['records']:,}")
        st.write(f"Systems: {ds['systems']}")

vcols = st.columns(7)
for (i, (k, v)) in enumerate(css["violations_by_category"].items()):
    with vcols[i]:
        st.metric(k, v)

st.subheader("Top Risks")
for r in css["top_risks"]:
    st.write(f"- {r}")

st.markdown("---")

# ======================================================================
# UI — Domains
# ======================================================================
overall_cost = 0
overall_weighted_score = 0
overall_weight_sum = 0

for domain_name, domain in SCHEMA["compliance_domains"].items():
    with st.expander(domain_name, expanded=False):
        st.caption(domain["description"])

        # Mandatory columns checkboxes
        mand = domain.get("mandatory_columns", [])
        if mand:
            st.subheader("Mandatory Columns")
            for col in mand:
                key = (domain_name, col["name"])
                st.session_state.mandatory_flags[key] = st.checkbox(
                    f"{col['name']} — {col['description']} (Violation Cost {money(col['violation_cost_usd'])})",
                    value=st.session_state.mandatory_flags.get(key, False)
                )

        # Subdomains and metrics
        subs = domain.get("subdomains", {})
        if subs:
            st.subheader("Controls and Metrics")
            for sname, sobj in subs.items():
                st.markdown(f"**{sname}** (weight {sobj.get('weight', 0):.2f})")
                for m in sobj.get("metrics", []):
                    mkey = (domain_name, sname, m["name"])
                    st.session_state.metric_flags[mkey] = st.checkbox(
                        f"{m['name']} — {m['observation']} [{m['regulation']}] (Penalty {money(m.get('estimated_penalty', 0))})",
                        value=st.session_state.metric_flags.get(mkey, False)
                    )

                    # BAA file upload if configured
                    ucfg = m.get("upload_config", {})
                    if ucfg.get("enabled", False):
                        files = st.file_uploader(
                            "Upload BAA documents",
                            type=[t.replace(".", "") for t in ucfg.get("file_types", [])],
                            accept_multiple_files=True,
                            key=f"upload_{domain_name}_{sname}"
                        )
                        if files:
                            for f in files:
                                with st.expander(f"Metadata for {f.name}", expanded=True):
                                    vname = st.text_input("Vendor Name", key=f"vn_{f.name}")
                                    sdate = st.date_input("Signed Date", key=f"sd_{f.name}", value=date.today())
                                    edate = st.date_input("Expiration Date", key=f"ed_{f.name}", value=date.today())
                                    cper  = st.text_input("Contact Person", key=f"cp_{f.name}")
                                    cem   = st.text_input("Contact Email", key=f"ce_{f.name}")
                                    if st.button("Save BAA Record", key=f"save_{f.name}"):
                                        status = "Expired" if edate < date.today() else "Valid"
                                        st.session_state.baa_records.append({
                                            "filename": f.name,
                                            "vendor": vname,
                                            "signed": sdate.isoformat(),
                                            "expires": edate.isoformat(),
                                            "contact": cper,
                                            "email": cem,
                                            "status": status
                                        })
                                        st.success("Saved")

                        if st.session_state.baa_records:
                            df = pd.DataFrame(st.session_state.baa_records)
                            st.dataframe(df, use_container_width=True)
                            valid = (df["status"] == "Valid").sum()
                            total = len(df)
                            baa_score = (valid / total) * 100 if total else 0
                            st.metric("BAA Compliance Score", f"{baa_score:.0f}%")

        # Compute domain score and cost
        d_score, d_cost = calc_domain_score_and_cost(domain_name, domain)
        st.session_state.domain_scores[domain_name] = d_score
        st.session_state.domain_costs[domain_name] = d_cost

        cL, cR = st.columns(2)
        cL.metric("Domain Readiness Score", f"{d_score:.1f} / 100")
        cR.metric("Estimated Exposure", money(d_cost))

        overall_weighted_score += d_score * domain.get("weight", 0)
        overall_weight_sum += domain.get("weight", 0)
        overall_cost += d_cost

st.markdown("---")

# ======================================================================
# UI — Overall Summary and Export
# ======================================================================
overall_score = (overall_weighted_score / overall_weight_sum) if overall_weight_sum else 0.0

oc1, oc2, oc3, oc4 = st.columns(4)
oc1.metric("Overall Readiness Index", f"{overall_score:.1f} / 100")
oc2.metric("Aggregate Estimated Exposure", money(overall_cost))
oc3.metric("Domains", len(SCHEMA["compliance_domains"]))
oc4.metric("Assessment Date", SCHEMA["current_state_summary"]["assessment_date"])

csv_payload = export_summary_csv(st.session_state.domain_scores, st.session_state.domain_costs, overall_score, overall_cost)
st.download_button(
    "Download Summary CSV",
    data=csv_payload,
    file_name="readiness_summary.csv",
    mime="text/csv"
)

st.markdown("---")

# ======================================================================
# UI — Spider Web Diagram
# ======================================================================
st.header("Spider Web Diagram — Compliance Readiness by Domain")
fig = radar_chart(st.session_state.domain_scores)
st.pyplot(fig)

st.caption("Scoring = weighted average across subdomain indicators times mandatory-column coverage. Estimated exposure = penalties for unmet metrics plus violation-costs for missing mandatory columns.")
