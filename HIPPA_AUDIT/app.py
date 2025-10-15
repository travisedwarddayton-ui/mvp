# app.py
import streamlit as st
import math
from datetime import date, datetime
from io import StringIO
import csv

import matplotlib.pyplot as plt

st.set_page_config(page_title="Data Readiness & Compliance Audit", layout="wide")

# ---------------------------
#  SCHEMA (Executive + Regulatory + Visual)
# ---------------------------
SCHEMA = {
    "current_state_summary": {
        "assessment_date": "2025-10-15",
        "organization": "Upperline Health",
        "data_sources": [
            {"name": "AthenaHealth EHR", "records": 1850000, "systems": 3},
            {"name": "Billing Platform",   "records": 950000,  "systems": 1},
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
        # ----------------- Administrative Safeguards -----------------
        "Administrative Safeguards (HIPAA §164.308)": {
            "weight": 0.15,
            "description": "Administrative controls for policies, risk analysis, workforce training, vendor oversight.",
            "mandatory_columns": [
                {"name": "last_modified_by",      "description": "Who changed PHI/governance docs.",                                "violation_cost_usd": 5000},
                {"name": "last_modified_date",    "description": "When record/doc last changed (audit correlation §164.312(b)).",   "violation_cost_usd": 10000},
                {"name": "record_version",        "description": "Versioning for SOPs, SRAs, policies.",                            "violation_cost_usd": 7500},
                {"name": "baa_vendor_id",         "description": "FK from PHI/system to vendor to prove BAA coverage.",             "violation_cost_usd": 100000},
                {"name": "training_completion_date","description": "Annual HIPAA training completion per user.",                     "violation_cost_usd": 15000}
            ],
            "subdomains": {
                "Risk Management Program": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Annual Risk Analysis",
                            "observation": "No HIPAA risk analysis in last 12 months.",
                            "regulation": "HIPAA §164.308(a)(1)(ii)(A)",
                            "impact_category": "Legal / Financial",
                            "estimated_penalty": 50000,
                            "impact_description": "OCR fines and corrective action plans.",
                            "recommended_action": "Conduct/document annual SRA; track remediation."
                        }
                    ]
                },
                "Business Associate Oversight": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "% Vendors with Valid BAAs",
                            "observation": "One or more vendors lack current BAAs.",
                            "regulation": "HIPAA §164.502(e)",
                            "impact_category": "Legal / Reputational",
                            "estimated_penalty": 100000,
                            "impact_description": "Missing BAAs often result in six-figure settlements.",
                            "recommended_action": "Execute/upload BAAs; enable expiry alerts.",
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
                            "observation": "< 90% staff completed annual HIPAA training.",
                            "regulation": "HIPAA §164.308(a)(5)(i)",
                            "impact_category": "Operational / Legal",
                            "estimated_penalty": 15000,
                            "impact_description": "Elevated breach likelihood and OCR findings.",
                            "recommended_action": "Implement LMS tracking; enforce annual re-cert."
                        }
                    ]
                }
            }
        },

        # ----------------- Technical Safeguards -----------------
        "Technical Safeguards (HIPAA §164.312 & 21 CFR 11.10)": {
            "weight": 0.20,
            "description": "Access control, authentication, encryption, audit trails; HIPAA + FDA Part 11.",
            "mandatory_columns": [
                {"name": "user_id",         "description": "Unique authenticated user ID per transaction.",     "violation_cost_usd": 10000},
                {"name": "access_role",     "description": "RBAC role granting least privilege.",               "violation_cost_usd": 25000},
                {"name": "mfa_enabled",     "description": "Multi-factor authentication status.",               "violation_cost_usd": 25000},
                {"name": "encryption_status","description": "AES-256 at rest / TLS in transit.",               "violation_cost_usd": 150000},
                {"name": "audit_log_id",    "description": "Immutable link to audit trail entry.",              "violation_cost_usd": 50000}
            ],
            "subdomains": {
                "Access Control & Authentication": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Unique ID / MFA",
                            "observation": "Shared accounts or missing MFA detected.",
                            "regulation": "HIPAA §164.312(d); 21 CFR 11.10(d)",
                            "impact_category": "Security / Operational",
                            "estimated_penalty": 25000,
                            "impact_description": "Unauthorized access remains top breach vector.",
                            "recommended_action": "Enforce unique IDs and MFA."
                        }
                    ]
                },
                "Encryption & Transmission Security": {
                    "weight": 0.35,
                    "metrics": [
                        {
                            "name": "Encryption-at-Rest",
                            "observation": "PHI stored unencrypted on local DB.",
                            "regulation": "HIPAA §164.312(a)(2)(iv)",
                            "impact_category": "Legal / Financial",
                            "estimated_penalty": 150000,
                            "impact_description": "Unencrypted breach penalties often six figures.",
                            "recommended_action": "Enable AES-256; manage keys & rotation."
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

        # ----------------- Physical & Infrastructure -----------------
        "Physical & Infrastructure Safeguards (HIPAA §164.310)": {
            "weight": 0.10,
            "description": "Facility, hardware, environment; availability & secure disposal of PHI media.",
            "mandatory_columns": [
                {"name": "hosting_environment",     "description": "Cloud/on-prem; maps to facility access controls.", "violation_cost_usd": 5000},
                {"name": "backup_frequency_days",   "description": "Interval for full backups.",                       "violation_cost_usd": 10000},
                {"name": "backup_last_tested_date", "description": "Most recent successful restore test.",            "violation_cost_usd": 15000},
                {"name": "system_uptime_percent",   "description": "Monthly availability to evidence resilience.",     "violation_cost_usd": 5000},
                {"name": "retention_expiration_date","description": "Data disposal schedule per policy/contract.",     "violation_cost_usd": 25000}
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
                            "recommended_action": "Quarterly restores with logs & sign-off."
                        }
                    ]
                },
                "Device & Media Control": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "Secure Media Disposal",
                            "observation": "Retired servers not wiped (NIST 800-88).",
                            "regulation": "HIPAA §164.310(d)(2)(i)",
                            "impact_category": "Legal / Financial",
                            "estimated_penalty": 25000,
                            "impact_description": "PHI exposure on disposed media triggers breach duties.",
                            "recommended_action": "Certified destruction/wipe logs; chain of custody."
                        }
                    ]
                }
            }
        },

        # ----------------- Data Integrity & Quality -----------------
        "Data Integrity & Quality (HIPAA §164.312(c)(1); 21 CFR 11.10(b))": {
            "weight": 0.15,
            "description": "Assures ePHI is accurate, complete, and protected from improper alteration or destruction.",
            "mandatory_columns": [
                {"name": "record_id",            "description": "Immutable unique ID for each record.",                   "violation_cost_usd": 10000},
                {"name": "record_checksum",      "description": "SHA-256 (or similar) hash to detect alteration.",       "violation_cost_usd": 25000},
                {"name": "created_date",         "description": "When record was created; chronology.",                   "violation_cost_usd": 5000},
                {"name": "last_modified_date",   "description": "When record last changed; alteration tracking.",         "violation_cost_usd": 10000},
                {"name": "last_modified_by",     "description": "Who changed the record; attribution.",                   "violation_cost_usd": 7500},
                {"name": "validation_status",    "description": "Pass/fail integrity check result.",                      "violation_cost_usd": 10000},
                {"name": "validation_timestamp", "description": "Last time integrity validation executed.",               "violation_cost_usd": 7500},
                {"name": "system_signature",     "description": "System-generated signature binding record + version.",   "violation_cost_usd": 20000}
            ],
            "subdomains": {
                "Completeness & Accuracy Controls": {
                    "weight": 0.40,
                    "metrics": [
                        {
                            "name": "Required Field Population",
                            "observation": "10% patient files missing MRN/diagnosis.",
                            "regulation": "21 CFR 11.10(b)",
                            "impact_category": "Financial / Compliance",
                            "estimated_penalty": 25000,
                            "impact_description": "Invalidates electronic submissions; affects CMS measures.",
                            "recommended_action": "Hard-stop validations; stewardship review."
                        }
                    ]
                },
                "Alteration & Destruction Protection": {
                    "weight": 0.30,
                    "metrics": [
                        {
                            "name": "Hash Verification",
                            "observation": "No checksums for data-at-rest.",
                            "regulation": "HIPAA §164.312(c)(1)",
                            "impact_category": "Legal / Security",
                            "estimated_penalty": 25000,
                            "impact_description": "No tamper detection for ePHI.",
                            "recommended_action": "Generate/verify hashes on write and periodically."
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

        # ----------------- Interoperability & Exchange -----------------
        "Interoperability & Electronic Exchange (21 CFR 11.30; ONC Cures Act)": {
            "weight": 0.10,
            "description": "Standardized, patient-accessible data exchange; API readiness and terminology normalization.",
            "mandatory_columns": [
                {"name": "fhir_resource_type",     "description": "Mapped FHIR resource.",                       "violation_cost_usd": 15000},
                {"name": "standard_mapping_status","description": "Mapping completeness to standards.",          "violation_cost_usd": 10000},
                {"name": "last_sync_timestamp",    "description": "Most recent API/interface exchange time.",    "violation_cost_usd": 5000},
                {"name": "external_system_id",     "description": "Partner system identifier for lineage.",      "violation_cost_usd": 5000}
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
                            "impact_description": "May affect program participation/incentives.",
                            "recommended_action": "Deploy certified endpoints; uptime/error monitoring."
                        }
                    ]
                },
                "Terminology Normalization": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Standard Code Utilization",
                            "observation": "Labs missing LOINC; diagnoses not SNOMED.",
                            "regulation": "USCDI / ONC Interop guidance",
                            "impact_category": "Operational / Financial",
                            "estimated_penalty": 10000,
                            "impact_description": "Breaks quality reporting & exchange semantics.",
                            "recommended_action": "Normalize during ETL; maintain code dictionaries."
                        }
                    ]
                }
            }
        },

        # ----------------- Electronic Signatures -----------------
        "Electronic Signatures & Attribution (21 CFR 11.100–11.200)": {
            "weight": 0.10,
            "description": "Non-repudiation and signer accountability for approvals, authorship, and reviews.",
            "mandatory_columns": [
                {"name": "electronic_signature", "description": "Signature token/hash binding signer to record.", "violation_cost_usd": 30000},
                {"name": "signature_meaning",    "description": "Reason/meaning (approval/review/authorship).",  "violation_cost_usd": 10000},
                {"name": "signature_timestamp",  "description": "When signature applied.",                        "violation_cost_usd": 5000},
                {"name": "signature_user_id",    "description": "Authenticated signer identity.",                "violation_cost_usd": 10000}
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
                            "recommended_action": "Require password + biometric/token; periodic re-auth."
                        }
                    ]
                },
                "Signature Linkage": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Signature ↔ Record Version Binding",
                            "observation": "Signatures not bound to specific version.",
                            "regulation": "21 CFR 11.70",
                            "impact_category": "Legal / Operational",
                            "estimated_penalty": 15000,
                            "impact_description": "Weak linkage undermines record trust.",
                            "recommended_action": "Bind signature to checksum + version + user."
                        }
                    ]
                }
            ]
        },

        # ----------------- Information Governance & Infonomics -----------------
        "Information Governance & Infonomics (Value of Data)": {
            "weight": 0.15,
            "description": "Translates compliance maturity into measurable ROI, reduced denials, and operational gains.",
            "mandatory_columns": [
                {"name": "financial_impact_estimate", "description": "Estimated $ impact per issue/remediation.", "violation_cost_usd": 10000},
                {"name": "readiness_score",           "description": "Computed Data Readiness Index (0–100).",    "violation_cost_usd": 5000},
                {"name": "risk_level",                "description": "LOW/MEDIUM/HIGH exposure categorization.",  "violation_cost_usd": 5000}
            ],
            "subdomains": {
                "Data ROI Tracking": {
                    "weight": 0.50,
                    "metrics": [
                        {
                            "name": "Claims Denial Correlation",
                            "observation": "No linkage of data errors to denial rates.",
                            "regulation": "CMS Program Integrity guidance (best practice)",
                            "impact_category": "Financial",
                            "estimated_penalty": 50000,
                            "impact_description": "5–10% margin erosion from preventable denials.",
                            "recommended_action": "Correlate DQ issues with denials; prioritize fixes."
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
                            "recommended_action": "Adopt uniform scoring & heatmaps across clinics."
                        }
                    ]
                }
            ]
        }
    },

    "visual_summary": {
        "diagram_type": "spider_web",
        "description": "Radar chart showing readiness level per compliance domain (0–100).",
        "metrics": [
            {"domain": "Administrative Safeguards (HIPAA §164.308)", "score": 72},
            {"domain": "Technical Safeguards (HIPAA §164.312 & 21 CFR 11.10)", "score": 68},
            {"domain": "Physical & Infrastructure Safeguards (HIPAA §164.310)", "score": 75},
            {"domain": "Data Integrity & Quality (HIPAA §164.312(c)(1); 21 CFR 11.10(b))", "score": 70},
            {"domain": "Interoperability & Electronic Exchange (21 CFR 11.30; ONC Cures Act)", "score": 62},
            {"domain": "Electronic Signatures & Attribution (21 CFR 11.100–11.200)", "score": 80},
            {"domain": "Information Governance & Infonomics (Value of Data)", "score": 65}
        ],
        "scoring_methodology": {
            "scale": "0-100",
            "computation": "Weighted avg across subdomain compliance indicators (mandatory_columns + metric results)."
        }
    }
}

# ---------------------------
#  Helpers
# ---------------------------
DOMAIN_KEYS = list(SCHEMA["compliance_domains"].keys())

def init_state():
    if "metric_flags" not in st.session_state:
        st.session_state.metric_flags = {}   # key: (domain, subdomain, metric_name) -> bool
    if "mandatory_flags" not in st.session_state:
        st.session_state.mandatory_flags = {} # key: (domain, column_name) -> bool (exists)
    if "baa_records" not in st.session_state:
        st.session_state.baa_records = []     # list of dicts
    if "domain_scores" not in st.session_state:
        st.session_state.domain_scores = {}   # key: domain -> score (0..100)
    if "domain_costs" not in st.session_state:
        st.session_state.domain_costs = {}    # key: domain -> $
init_state()

def money(n):
    return "${:,.0f}".format(n)

def calc_domain_score_and_cost(domain_name, domain):
    """Compute domain readiness score from metric flags and mandatory columns.
       Score: % metrics satisfied (weighted by subdomain weights) * (mandatory coverage factor).
       Cost: sum of estimated_penalty for unmet metrics + violation_cost_usd for missing mandatory columns.
    """
    # Mandatory columns
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

    # Metrics by subdomain
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
        # Weight by subdomain weight normalized
        if total_weight > 0:
            metric_score += sub_score * (s_weight / total_weight)

    # Blend with mandatory coverage (mandatory acts as a multiplier)
    readiness = metric_score * mandatory_coverage * 100.0
    total_cost = metric_cost + mandatory_cost
    return readiness, total_cost

def export_summary_csv(domain_scores, domain_costs, overall_score, overall_cost):
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["Domain", "Score (0-100)", "Estimated Exposure ($)"])
    for d in DOMAIN_KEYS:
        writer.writerow([d, f"{domain_scores.get(d,0):.1f}", int(domain_costs.get(d,0))])
    writer.writerow([])
    writer.writerow(["OVERALL", f"{overall_score:.1f}", int(overall_cost)])
    return sio.getvalue()

def radar_chart(domain_scores):
    labels = DOMAIN_KEYS
    values = [max(0.0, min(100.0, domain_scores.get(d, 0.0))) for d in labels]

    # radar needs closed loop
    N = len(labels)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]

    fig = plt.figure(figsize=(6,6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([d.split(" (")[0] for d in labels], fontsize=9)

    ax.set_rlabel_position(0)
    ax.set_yticks([20,40,60,80,100])
    ax.set_yticklabels(["20","40","60","80","100"], fontsize=8)
    ax.set_ylim(0, 100)

    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.1)

    return fig

# ---------------------------
#  UI Sections
# ---------------------------
st.title("Data Readiness & Compliance Audit (HIPAA + 21 CFR Part 11)")

# ===== Current State Summary =====
with st.expander("📊 Current State Summary (Executive Snapshot)", expanded=True):
    css = SCHEMA["current_state_summary"]
    cols = st.columns(4)
    with cols[0]:
        st.metric("Assessment Date", css["assessment_date"])
        st.metric("Organization", css["organization"])
    with cols[1]:
        st.metric("Total Records", f"{css['total_records']:,}")
        st.metric("Systems", css["total_systems"])
    with cols[2]:
        st.metric("Identified Violations", css["identified_violations"])
    with cols[3]:
        st.metric("Estimated Exposure", money(css["estimated_total_exposure_usd"]))

    st.markdown("**Data Sources**")
    dcols = st.columns(len(css["data_sources"]))
    for i, ds in enumerate(css["data_sources"]):
        with dcols[i]:
            st.write(f"**{ds['name']}**")
            st.write(f"Records: {ds['records']:,}")
            st.write(f"Systems: {ds['systems']}")

    st.markdown("**Violations by Category**")
    vc1, vc2, vc3, vc4, vc5, vc6, vc7 = st.columns(7)
    cats = list(css["violations_by_category"].items())
    for (col, (name, val)) in zip([vc1,vc2,vc3,vc4,vc5,vc6,vc7], cats):
        with col:
            st.metric(name, val)

    st.markdown("**Top Risks**")
    for r in css["top_risks"]:
        st.write(f"• {r}")

st.markdown("---")

# ===== Domain Drilldown =====
st.header("Compliance Domains")

overall_cost = 0
overall_weight_sum = 0
overall_weighted_score = 0

for dname in DOMAIN_KEYS:
    dom = SCHEMA["compliance_domains"][dname]
    with st.expander(f"🧭 {dname}", expanded=False):
        st.caption(dom["description"])

        # Mandatory Columns Section
        mand = dom.get("mandatory_columns", [])
        if mand:
            st.subheader("Mandatory Columns (Controls-as-Data)")
            mcols = st.columns([3,4,2,2])
            mcols[0].markdown("**Column**")
            mcols[1].markdown("**Description**")
            mcols[2].markdown("**Exists?**")
            mcols[3].markdown("**Violation Cost**")

            for col in mand:
                row = st.columns([3,4,2,2])
                row[0].write(col["name"])
                row[1].write(col["description"])
                key = (dname, col["name"])
                exists_flag = row[2].checkbox(" ", key=key, value=False)
                row[3].write(money(col["violation_cost_usd"]))

        # Subdomains & Metrics
        subs = dom.get("subdomains", {})
        if subs:
            st.subheader("Controls & Metrics")
            for sname, sobj in subs.items():
                st.markdown(f"**{sname}**  \n_weight {sobj.get('weight',0):.2f}_")
                for m in sobj.get("metrics", []):
                    mkey = (dname, sname, m["name"])
                    cols = st.columns([0.05, 0.55, 0.2, 0.2])
                    ok = cols[0].checkbox("", key=mkey, value=False)
                    cols[1].write(f"**{m['name']}** — {m['observation']}")
                    cols[2].write(f"*{m['regulation']}*")
                    cols[3].write(money(m.get("estimated_penalty", 0)))
                st.divider()

        # Special BAA Upload section (if present)
        if "Business Associate Oversight" in subs:
            metrics = subs["Business Associate Oversight"]["metrics"]
            for m in metrics:
                if m.get("upload_config", {}).get("enabled", False):
                    st.subheader("📄 BAA Uploads & Tracking")
                    upcfg = m["upload_config"]
                    files = st.file_uploader(
                        "Upload BAAs (PDF/DOCX/IMG)", type=[t.replace(".","") for t in upcfg["file_types"]],
                        accept_multiple_files=True, key=f"_upload_{dname}"
                    )
                    if files:
                        for f in files:
                            with st.popover(f"Metadata for {f.name}"):
                                vname = st.text_input("Vendor Name", key=f"v_{f.name}")
                                sdate = st.date_input("Signed Date", key=f"s_{f.name}", value=date.today())
                                edate = st.date_input("Expiration Date", key=f"e_{f.name}", value=date.today())
                                cp    = st.text_input("Contact Person", key=f"p_{f.name}")
                                cem   = st.text_input("Contact Email", key=f"e2_{f.name}")
                                if st.button("Save BAA Record", key=f"save_{f.name}"):
                                    status = "Expired" if edate < date.today() else "Valid"
                                    st.session_state.baa_records.append({
                                        "filename": f.name,
                                        "vendor": vname,
                                        "signed": sdate.isoformat(),
                                        "expires": edate.isoformat(),
                                        "contact": cp,
                                        "email": cem,
                                        "status": status
                                    })
                                    st.success("BAA saved.")

                    if st.session_state.baa_records:
                        st.write("**BAA Records**")
                        # Simple table view
                        hdr = ["filename","vendor","signed","expires","contact","email","status"]
                        st.table([{k:r.get(k,"")} for r in st.session_state.baa_records for k in [*hdr]][::len(hdr)])

                        valid = sum(1 for r in st.session_state.baa_records if r["status"] == "Valid")
                        total = len(st.session_state.baa_records)
                        score = (valid/total)*100 if total else 0
                        st.metric("BAA Compliance Score", f"{score:.0f}%")

        # Calculate domain score & cost
        score, cost = calc_domain_score_and_cost(dname, dom)
        st.session_state.domain_scores[dname] = score
        st.session_state.domain_costs[dname] = cost

        lcol, rcol = st.columns(2)
        lcol.metric("Domain Readiness Score", f"{score:.1f} / 100")
        rcol.metric("Estimated Exposure", money(cost))

        overall_weight_sum += dom.get("weight", 0)
        overall_weighted_score += score * dom.get("weight", 0)
        overall_cost += cost

st.markdown("---")

# ===== Aggregate Results + Export =====
overall_score = (overall_weighted_score / overall_weight_sum) if overall_weight_sum else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall Readiness Index", f"{overall_score:.1f} / 100")
c2.metric("Aggregate Estimated Exposure", money(overall_cost))
c3.metric("Total Domains", len(DOMAIN_KEYS))
c4.metric("Assessment Date", SCHEMA["current_state_summary"]["assessment_date"])

csv_data = export_summary_csv(st.session_state.domain_scores, st.session_state.domain_costs, overall_score, overall_cost)
st.download_button("⬇️ Download Summary CSV", data=csv_data, file_name="readiness_summary.csv", mime="text/csv")

st.markdown("---")

# ===== Spider Web Diagram (Radar) =====
st.header("Spider Web Diagram — Compliance Readiness by Domain")
fig = radar_chart(st.session_state.domain_scores)
st.pyplot(fig)

st.caption("Scoring methodology: weighted average across subdomain indicators multiplied by mandatory-column coverage.")
