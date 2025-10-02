import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Travel Data Federation Hub — CEO Edition", page_icon="✈️", layout="wide")

# -----------------------------
# Scenario Presets
# -----------------------------
scenarios = {
    "Conservative": {
        "gmv": 8_000_000,
        "take_rate": 11.0,
        "margin_uplift": 0.2,
        "personalization": 1.5,
        "advisors": 800,
        "hours_saved": 100,
        "hourly_cost": 35,
        "decision_speed": 40,
        "compliance_prob": 2.0,
        "compliance_impact": 5_000_000,
        "capex": 750_000,
        "opex": 100_000,
    },
    "Expected": {
        "gmv": 10_000_000,
        "take_rate": 12.0,
        "margin_uplift": 0.4,
        "personalization": 3.0,
        "advisors": 1000,
        "hours_saved": 150,
        "hourly_cost": 40,
        "decision_speed": 70,
        "compliance_prob": 1.0,
        "compliance_impact": 10_000_000,
        "capex": 500_000,
        "opex": 75_000,
    },
    "Aggressive": {
        "gmv": 12_000_000,
        "take_rate": 13.0,
        "margin_uplift": 0.7,
        "personalization": 5.0,
        "advisors": 1200,
        "hours_saved": 200,
        "hourly_cost": 50,
        "decision_speed": 90,
        "compliance_prob": 0.5,
        "compliance_impact": 15_000_000,
        "capex": 400_000,
        "opex": 70_000,
    }
}

# -----------------------------
# Helper: ROI Model (simplified)
# -----------------------------
def roi_projection(params, months=24, discount_rate=0.12):
    t = np.arange(1, months+1)
    base_net = params["gmv"] * (params["take_rate"]/100)

    # Adoption curve
    x = (t - months/2) / (months/10)
    adopt = 1/(1+np.exp(-x))
    adopt = (adopt - adopt.min())/(adopt.max()-adopt.min())

    rev_uplift = params["gmv"] * (
        params["personalization"]/100.0 + 0.2*(params["decision_speed"]/100.0)
    ) * adopt
    take_rate_uplift = (params["margin_uplift"]/100.0) * adopt
    net_from_gmv = (params["gmv"] + rev_uplift) * (
        params["take_rate"]/100.0 + take_rate_uplift
    )

    eff_savings = params["advisors"] * params["hours_saved"] * params["hourly_cost"] / 12.0 * adopt
    compliance_savings = (params["compliance_prob"]/100.0 * params["compliance_impact"]/12.0) * adopt

    inflows = (net_from_gmv - base_net) + eff_savings + compliance_savings
    outflows = np.zeros(months) + params["opex"]
    outflows[0] += params["capex"]
    net = inflows - outflows
    cum = np.cumsum(net)

    npv = float(np.sum(net / (1+discount_rate/12.0)**t))
    payback = int(np.argmax(cum>0))+1 if np.any(cum>0) else None
    per_million = (inflows.mean()*12) / (params["gmv"]/1_000_000)

    return npv, payback, per_million

# -----------------------------
# Layout
# -----------------------------
st.title("✈️ Travel Data Federation Hub — CEO Dashboard")
st.caption("Example dashboard focused on ROI & strategy. Results of data auditing and assessments are plugged into this dashbaord")

tab1, tab2, tab3 = st.tabs(["🏆 CEO Summary", "📈 ROI Details", "🛡️ Governance"])

# -----------------------------
# CEO SUMMARY TAB
# -----------------------------
with tab1:
    st.header("🏆 Executive Summary")
    scenario = st.selectbox("Choose Scenario", list(scenarios.keys()), index=1)
    params = scenarios[scenario]

    npv, payback, per_million = roi_projection(params)

    col1, col2, col3 = st.columns(3)
    col1.metric("NPV (12% DR)", f"${npv:,.0f}")
    col2.metric("Payback", f"{payback} months" if payback else "> horizon")
    col3.metric("Annual Net / $1M GMV", f"${per_million:,.0f}")

    # Narrative
    summary_text = f"""
    Under the **{scenario} scenario**, your agency achieves payback in 
    **{payback} months** with a projected NPV of **${npv:,.0f}**. 
    On average, each $1M in bookings generates **${per_million:,.0f} net uplift per year**.  

    Compared to peers, this outcome is {"above average" if per_million >= 30000 else "in line with industry benchmarks"}.  
    """

    st.success(summary_text)

    # Top initiatives (mocked from catalog)
    top_initiatives = ["Personalization & Cross-Sell", "Advisor Efficiency", "Compliance Automation"]
    st.subheader("📊 Top 3 Strategic Initiatives")
    st.write("1️⃣ " + top_initiatives[0])  
    st.write("2️⃣ " + top_initiatives[1])  
    st.write("3️⃣ " + top_initiatives[2])  

    st.markdown("---")

    # Export PDF
    def export_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Executive Summary — Travel Data Federation Hub", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, summary_text)
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Top Initiatives", ln=True)
        for i, init in enumerate(top_initiatives, 1):
            pdf.cell(0, 10, f"{i}. {init}", ln=True)
        pdf.output("CEO_Summary.pdf")

    if st.button("⬇️ Export CEO Board Pack (PDF)"):
        export_pdf()
        st.success("Board pack exported as CEO_Summary.pdf")

# -----------------------------
# ROI DETAIL TAB
# -----------------------------
with tab2:
    st.header("📈 ROI Model Details")
    st.caption("For CFO/analyst validation.")
    st.write("Detailed assumptions, inflows/outflows, projections… (reuse your full ROI model here)")

# -----------------------------
# GOVERNANCE TAB
# -----------------------------
with tab3:
    st.header("🛡️ Governance & Risk")
    st.write("Summarize regulatory readiness: GDPR, PCI, Audit Trails, KPI Library.")
    st.success("Embedded governance reduces compliance exposure by ~$X M annually.")
