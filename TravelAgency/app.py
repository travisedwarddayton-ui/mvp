import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ============================
# Page Config
# ============================
st.set_page_config(
    page_title="Travel Data Federation Hub — Executive ROI Simulator",
    page_icon="✈️",
    layout="wide",
)

# ============================
# Helpers
# ============================

def radar_chart(categories, values, benchmark=None, title="Maturity Radar"):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='Your Scores'))
    if benchmark is not None:
        fig.add_trace(go.Scatterpolar(r=benchmark + [benchmark[0]], theta=categories + [categories[0]], fill='toself', name='Industry Benchmark', opacity=0.5))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,5])), showlegend=True, title=title, margin=dict(l=10,r=10,t=50,b=10))
    return fig


def priority_bar(df):
    fig = px.bar(df.sort_values('Priority Score', ascending=True), x='Priority Score', y='Initiative', orientation='h',
                 hover_data=['Impact $/yr','Time-to-Value (mo)','Risk (1-5)'], title='Prioritized Initiatives')
    fig.update_layout(margin=dict(l=10,r=10,t=50,b=10))
    return fig


def capex_opex_pie(capex, opex):
    df = pd.DataFrame({"Type":["CapEx","OpEx"],"Amount":[capex, opex]})
    fig = px.pie(df, names='Type', values='Amount', title='Investment Mix')
    fig.update_layout(margin=dict(l=10,r=10,t=40,b=10))
    return fig


def sankey_federation():
    nodes = [
        "Booking Platforms\n(GDS/Direct)",
        "Franchise CRMs\n& Advisor Tools",
        "Supplier APIs\n(air/hotel/cruise)",
        "Federation Layer\n(virtualized queries)",
        "Identity Resolution\n(Customer 360)",
        "Governance\n(PII/PCI/GDPR)",
        "Analytics Layer\n(BI/AI)",
        "Advisor Workspace",
        "Exec Dashboards",
        "Partner Portals"
    ]
    idx = {n:i for i,n in enumerate(nodes)}
    links = [
        ("Booking Platforms\n(GDS/Direct)", "Federation Layer\n(virtualized queries)", 8),
        ("Franchise CRMs\n& Advisor Tools", "Federation Layer\n(virtualized queries)", 7),
        ("Supplier APIs\n(air/hotel/cruise)", "Federation Layer\n(virtualized queries)", 7),
        ("Federation Layer\n(virtualized queries)", "Identity Resolution\n(Customer 360)", 6),
        ("Identity Resolution\n(Customer 360)", "Analytics Layer\n(BI/AI)", 6),
        ("Federation Layer\n(virtualized queries)", "Governance\n(PII/PCI/GDPR)", 4),
        ("Analytics Layer\n(BI/AI)", "Advisor Workspace", 4),
        ("Analytics Layer\n(BI/AI)", "Exec Dashboards", 5),
        ("Analytics Layer\n(BI/AI)", "Partner Portals", 3)
    ]
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=nodes, pad=18, thickness=18),
        link=dict(source=[idx[s] for s,t,v in links], target=[idx[t] for s,t,v in links], value=[v for s,t,v in links])
    )])
    fig.update_layout(title='How Federation Unifies Travel Data Without Moving It', margin=dict(l=10,r=10,t=50,b=10))
    return fig


def roi_projection_monthly(gmv, take_rate_pct, supplier_margin_uplift_pct, 
                           advisors, hours_saved_per_advisor, hourly_cost,
                           personalization_uplift_pct,
                           compliance_incident_prob_pct, compliance_impact_usd,
                           capex, monthly_opex, months=24, discount_rate=0.12,
                           decision_speed_gain_pct=70):
    """Return df + KPIs for a travel-specific model.
    gmv = gross bookings per month (baseline)
    take_rate = baseline net margin % on GMV (agency margin)
    supplier_margin_uplift_pct = point uplift on take rate from better negotiations/mix
    personalization_uplift_pct = % GMV uplift from cross-sell/personalization
    decision_speed_gain_pct = % faster decision cycles; we model as 0.2x of that applied to revenue for conservatism
    compliance_incident_prob_pct = annual probability; impact applied once expected-value style
    """
    t = np.arange(1, months+1)

    # Base economics
    base_take_rate = take_rate_pct/100.0
    base_net = gmv * base_take_rate  # baseline net per month

    # Uplifts (assume phased S-curve adoption)
    x = (t - months/2) / (months/10)
    adopt = 1/(1+np.exp(-x))
    adopt = (adopt - adopt.min())/(adopt.max()-adopt.min())

    # Revenue uplift from personalization + decision speed (conservative factor 0.2 on decision speed)
    rev_uplift_gmv = gmv * (personalization_uplift_pct/100.0 + 0.2*(decision_speed_gain_pct/100.0)) * adopt

    # Supplier margin uplift (raise take rate)
    take_rate_uplift = supplier_margin_uplift_pct/100.0 * adopt
    net_from_gmv = (gmv + rev_uplift_gmv) * (base_take_rate + take_rate_uplift)

    # Advisor efficiency savings
    eff_savings = advisors * hours_saved_per_advisor * (hourly_cost) / 12.0 * adopt  # spread annually into monthly

    # Compliance risk avoidance (expected value) apportioned monthly
    annual_expected_savings = (compliance_incident_prob_pct/100.0) * compliance_impact_usd
    compliance_savings = (annual_expected_savings/12.0) * adopt

    inflows = (net_from_gmv - (gmv*base_take_rate)) + eff_savings + compliance_savings  # incremental benefit vs baseline

    # Costs
    outflows = np.zeros(months) + monthly_opex
    outflows[0] += capex

    net = inflows - outflows
    cum = np.cumsum(net)
    df = pd.DataFrame({
        'Month': t,
        'Adoption(0-1)': adopt,
        'Incremental Net from GMV': net_from_gmv - (gmv*base_take_rate),
        'Advisor Efficiency Savings': eff_savings,
        'Compliance Savings (EV)': compliance_savings,
        'Cash Inflows (Incremental)': inflows,
        'Cash Outflows': outflows,
        'Net Cashflow': net,
        'Cumulative Cashflow': cum
    })

    # KPIs
    disc = (1+discount_rate/12.0)**t
    npv = float(np.sum(net / disc))
    payback = int(np.argmax(cum>0))+1 if np.any(cum>0) else None

    # Normalized per $1M GMV heuristic
    per_million = (inflows.mean()*12) / (gmv/1_000_000)  # yearly net impact per $1M GMV

    return df, npv, payback, per_million


def projection_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cash Inflows (Incremental)'], mode='lines', name='Inflows'))
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cash Outflows'], mode='lines', name='Outflows'))
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Net Cashflow'], mode='lines', name='Net'))
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative Cashflow'], mode='lines', name='Cumulative'))
    fig.update_layout(title='24-Month Projection', xaxis_title='Month', yaxis_title='Amount', margin=dict(l=10,r=10,t=50,b=10))
    return fig

# ============================
# Sidebar
# ============================
st.sidebar.title("⚙️ Configure Preview")
segment = st.sidebar.selectbox("Primary Segment", ["Leisure", "Corporate", "Mixed Portfolio"], index=2)
region = st.sidebar.selectbox("Region", ["North America","EU/UK","Global"], index=2)
currency = st.sidebar.selectbox("Currency", ["$","€","£"], index=0)
cta_url = st.sidebar.text_input("CTA URL (Book a call)", value="https://realtimedata.ai/")

st.sidebar.markdown("---")
st.sidebar.subheader("Guarantee")
st.sidebar.success("30-Day Money Back Guarantee. If this framework doesn’t surface a clear path to ROI your board can act on, you don’t pay.")

# Industry benchmark (demo)
benchmarks = {
    "Leisure": [2.6, 2.8, 2.4, 2.9, 2.5],
    "Corporate": [3.0, 3.2, 2.9, 3.1, 2.8],
    "Mixed Portfolio": [2.8, 3.0, 2.6, 3.0, 2.7],
}

# ============================
# Header
# ============================
st.title("Travel Data Federation Hub — CEO Dashboard")
st.markdown(
    """
    Unify booking, customer, and supplier systems into a **single query layer** — no massive data migrations. 
    Unlock hidden revenue, boost advisor productivity, and cut compliance risk with **federated analytics in real time**.
    """
)
colh1, colh2, colh3 = st.columns([2,2,1])
with colh1:
    st.info("Outcomes: Hidden Revenue • Advisor Productivity • Faster Decisions • Consistent KPIs • Lower Risk")
with colh2:
    st.warning("Rule of Thumb: For every $1M in bookings, expect **$20K–$40K** net financial impact from federation.")
with colh3:
    st.link_button("Book a Call", cta_url, type="primary")

st.markdown("---")

# ============================
# 1) Federation Readiness Assessment (Radar)
# ============================
st.header("1) Federation Readiness Assessment")
st.caption("Score your current state across the five pillars. Compare with peers.")

c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    p_integration = st.slider("System Integration", 0.0, 5.0, 2.5, 0.1)
with c2:
    p_identity = st.slider("Identity Resolution (Customer 360)", 0.0, 5.0, 2.5, 0.1)
with c3:
    p_realtime = st.slider("Real-Time Access", 0.0, 5.0, 2.5, 0.1)
with c4:
    p_governance = st.slider("Governance & Compliance", 0.0, 5.0, 2.5, 0.1)
with c5:
    p_kpis = st.slider("KPI Standardization", 0.0, 5.0, 2.5, 0.1)

radar_categories = ["Integration","Identity 360","Real-Time","Governance","KPIs"]
user_vals = [p_integration, p_identity, p_realtime, p_governance, p_kpis]
bench = benchmarks.get(segment, benchmarks["Mixed Portfolio"])

st.plotly_chart(radar_chart(radar_categories, user_vals, bench, title=f"Readiness vs {segment} Peers"), use_container_width=True)

st.markdown("---")

# ============================
# 2) Value Map — Initiatives & Prioritization
# ============================
st.header("2) Value Map — Prioritize High-Impact Initiatives")
st.caption("Select initiatives. Tune assumptions. See an auto-ranking by ROI potential, time-to-value, and risk.")

catalog = {
    "Personalization & Cross-Sell": {"impact": 100_000, "time": 3, "risk": 2},
    "Advisor Efficiency (Unified Workspace)": {"impact": 8_000 * 150, "time": 2, "risk": 2},  # $/hr * hours/yr
    "Supplier Margin Optimization": {"impact": 125_000, "time": 4, "risk": 3},
    "Real-Time Ops & Disruption Response": {"impact": 90_000, "time": 2, "risk": 2},
    "KPI Standardization & Error Reduction": {"impact": 70_000, "time": 3, "risk": 2},
    "Compliance & Audit Automation": {"impact": 150_000, "time": 5, "risk": 2},
}

sel = st.multiselect("Choose initiatives to evaluate", list(catalog.keys()), default=list(catalog.keys())[:4])
rows = []
for name in sel:
    base = catalog[name]
    with st.expander(f"Configure: {name}"):
        cA,cB,cC = st.columns(3)
        with cA:
            imp = st.number_input(f"Estimated Impact $/yr — {name}", min_value=0, value=int(base['impact']), step=10_000, key=f"imp_{name}")
        with cB:
            ttv = st.slider(f"Time-to-Value (months) — {name}", 1, 12, int(base['time']), key=f"ttv_{name}")
        with cC:
            risk = st.slider(f"Risk (1=low,5=high) — {name}", 1, 5, int(base['risk']), key=f"risk_{name}")
    score = (imp/100_000) * (1 - (risk-1)/4) * (1/(ttv/6))
    rows.append({"Initiative": name, "Impact $/yr": imp, "Time-to-Value (mo)": ttv, "Risk (1-5)": risk, "Priority Score": score})

if rows:
    df_rank = pd.DataFrame(rows).sort_values('Priority Score', ascending=False)
    st.dataframe(df_rank, use_container_width=True)
    st.plotly_chart(priority_bar(df_rank), use_container_width=True)
    st.success("Top 3 candidates: " + ", ".join(df_rank['Initiative'].head(3).tolist()))

st.markdown("---")

# ============================
# 3) Architecture — Federated Model
# ============================
st.header("3) Architecture — Federated Access Without Data Movement")
st.caption("Single query layer across systems, with governance and identity stitched in.")
st.plotly_chart(sankey_federation(), use_container_width=True)

st.markdown("---")

# ============================
# 4) ROI & Investment Model — Travel Specific
# ============================
st.header("4) ROI & Investment Model — Travel Specific")
st.caption("Model incremental net impact over 24 months. Inputs are conservative by default.")

c1,c2,c3,c4 = st.columns(4)
with c1:
    gmv = st.number_input(f"Baseline Monthly Bookings (GMV) ({currency})", min_value=0, value=10_000_000, step=500_000)
with c2:
    take_rate_pct = st.slider("Baseline Take Rate (%)", 5.0, 18.0, 12.0, 0.5)
with c3:
    supplier_margin_uplift_pct = st.slider("Supplier Margin Uplift (pp)", 0.0, 2.0, 0.4, 0.1)
with c4:
    personalization_uplift_pct = st.slider("Personalization GMV Uplift (%)", 0.0, 10.0, 3.0, 0.5)

c5,c6,c7,c8 = st.columns(4)
with c5:
    advisors = st.number_input("# of Advisors", min_value=1, value=1000, step=50)
with c6:
    hours_saved = st.slider("Hours Saved per Advisor / year", 50, 300, 150, 10)
with c7:
    hourly_cost = st.number_input(f"Fully-Loaded Hourly Cost ({currency})", min_value=0, value=40, step=5)
with c8:
    decision_speed_gain_pct = st.slider("Decision Speed Gain (%)", 0, 100, 70, 5)

c9,c10,c11 = st.columns(3)
with c9:
    compliance_prob = st.slider("Annual Compliance Incident Probability (%)", 0.0, 10.0, 1.0, 0.1)
with c10:
    compliance_impact = st.number_input(f"Incident Cost Impact ({currency})", min_value=0, value=10_000_000, step=500_000)
with c11:
    months = st.slider("Projection Horizon (months)", 12, 36, 24)

c12,c13 = st.columns(2)
with c12:
    capex = st.number_input(f"Initial CapEx ({currency})", min_value=0, value=500_000, step=50_000)
with c13:
    opex = st.number_input(f"Monthly OpEx ({currency}/mo)", min_value=0, value=75_000, step=5_000)

# Compute projection
(df_proj, npv, payback, per_million) = roi_projection_monthly(
    gmv=gmv,
    take_rate_pct=take_rate_pct,
    supplier_margin_uplift_pct=supplier_margin_uplift_pct,
    advisors=advisors,
    hours_saved_per_advisor=hours_saved,
    hourly_cost=hourly_cost,
    personalization_uplift_pct=personalization_uplift_pct,
    compliance_incident_prob_pct=compliance_prob,
    compliance_impact_usd=compliance_impact,
    capex=capex,
    monthly_opex=opex,
    months=months,
    decision_speed_gain_pct=decision_speed_gain_pct,
)

st.plotly_chart(projection_chart(df_proj), use_container_width=True)

k1,k2,k3,k4 = st.columns(4)
with k1:
    st.metric("NPV (12% annual)", f"{currency}{npv:,.0f}")
with k2:
    st.metric("Payback (months)", payback if payback else "> horizon")
with k3:
    st.metric("Annualized Net Impact / $1M GMV", f"{currency}{per_million:,.0f}")
with k4:
    rule_of_thumb = "✅ within $20K–$40K band" if 20_000 <= per_million <= 40_000 else "⚠️ outside $20K–$40K band"
    st.metric("Rule-of-Thumb Check", rule_of_thumb)

cpa, ctable = st.columns([1,2])
with cpa:
    st.plotly_chart(capex_opex_pie(capex, months*opex), use_container_width=True)
with ctable:
    st.dataframe(df_proj, use_container_width=True)

st.download_button(
    label="Download Projection (CSV)",
    data=df_proj.to_csv(index=False).encode('utf-8'),
    file_name="travel_federation_roi_projection.csv",
    mime="text/csv",
)

st.markdown("---")

# ============================
# 5) Compliance & KPI Guardrails
# ============================
st.header("5) Compliance & KPI Guardrails")
st.caption("Centralized governance and standardized metrics reduce disputes and risk.")
colg1,colg2,colg3 = st.columns(3)
with colg1:
    gdpr = st.checkbox("GDPR/PCI Governance")
    pii = st.checkbox("PII Tokenization & Access Controls")
with colg2:
    audit = st.checkbox("Audit Trails & Lineage")
    dpia = st.checkbox("DPIA / Risk Register")
with colg3:
    kpi_lib = st.checkbox("Standard KPI Library (RPA, CLV, Wallet Share)")
    qa = st.checkbox("Automated Data Quality Checks")

if any([gdpr,pii,audit,dpia,kpi_lib,qa]):
    st.success("These guardrails are embedded in the federation layer and analytics policies.")

st.markdown("---")

# ============================
# Deliverables & CTA
# ============================
st.header("Deliverables")
cd1,cd2,cd3,cd4 = st.columns(4)
with cd1:
    st.markdown("**📄 Executive Report (PDF)**\nBoard-ready summary of ROI & roadmap")
with cd2:
    st.markdown("**🗺️ Architecture Deck (PPT)**\nFederation blueprint & governance checkpoints")
with cd3:
    st.markdown("**📊 ROI Workbook (Excel)**\nScenario models for finance approval")
with cd4:
    st.markdown("**👥 Leadership Workshop (2h)**\nAlignment & decisions on next steps")

st.info("We limit onboardings per quarter to ensure C‑suite focus. When slots fill, the next window opens in 4–8 weeks.")

ccta1,ccta2 = st.columns([1,3])
with ccta1:
    st.link_button("Book a Call", cta_url, type="primary")
with ccta2:
    st.caption("Questions from procurement? Reply to your rep and we’ll provide security & compliance docs.")

st.markdown("---")

st.caption(f"© {datetime.now().year} — Travel Data Federation Hub (product overview)")
