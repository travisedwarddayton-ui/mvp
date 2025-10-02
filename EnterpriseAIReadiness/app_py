import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Enterprise AI Readiness & ROI Audit Visualizer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Helper Functions
# -----------------------------

def radar_chart(categories, values, benchmark=None, title="AI Readiness Radar"):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='Your Score'))
    if benchmark is not None:
        fig.add_trace(go.Scatterpolar(r=benchmark + [benchmark[0]], theta=categories + [categories[0]], fill='toself', name='Peer Benchmark', opacity=0.5))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        title=title,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def value_map_chart(df_ranked):
    fig = px.bar(
        df_ranked.sort_values('Priority Score', ascending=True),
        x='Priority Score', y='Use Case', orientation='h',
        hover_data=['Impact $/yr', 'Time-to-Value (mo)', 'Risk (1-5)'],
        title='Prioritized AI Use Cases',
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


def capex_opex_pie(capex, opex):
    df = pd.DataFrame({'Type': ['CapEx', 'OpEx'], 'Amount': [capex, opex]})
    fig = px.pie(df, names='Type', values='Amount', title='CapEx vs OpEx')
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


def roi_projection(initial_invest, monthly_opex, base_revenue, base_cost,
                   rev_uplift_pct, cost_reduce_pct, months=24, adoption_curve='S-curve', discount_rate=0.12):
    """Return monthly projection DataFrame and KPIs (NPV, Payback Month)."""
    t = np.arange(1, months + 1)

    # Adoption profile
    if adoption_curve == 'Linear':
        adopt = t / months
    elif adoption_curve == 'Front-loaded':
        adopt = np.clip(np.sqrt(t / months), 0, 1)
    else:  # S-curve
        x = (t - months/2) / (months/10)
        adopt = 1 / (1 + np.exp(-x))
        adopt = (adopt - adopt.min()) / (adopt.max() - adopt.min())

    monthly_rev_uplift = base_revenue * (rev_uplift_pct/100.0) * adopt
    monthly_cost_saving = base_cost * (cost_reduce_pct/100.0) * adopt

    cash_inflows = monthly_rev_uplift + monthly_cost_saving
    cash_outflows = np.zeros(months) + monthly_opex
    cash_outflows[0] += initial_invest  # place CapEx at month 1

    net_cashflow = cash_inflows - cash_outflows

    # NPV & Payback
    discount_factors = (1 + discount_rate/12) ** t
    npv = np.sum(net_cashflow / discount_factors)

    cum_cashflow = np.cumsum(net_cashflow)
    payback_month = int(np.argmax(cum_cashflow > 0)) + 1 if np.any(cum_cashflow > 0) else None

    df = pd.DataFrame({
        'Month': t,
        'Adoption(0-1)': adopt,
        'Revenue Uplift': monthly_rev_uplift,
        'Cost Savings': monthly_cost_saving,
        'Cash Inflows': cash_inflows,
        'Cash Outflows': cash_outflows,
        'Net Cashflow': net_cashflow,
        'Cumulative Cashflow': cum_cashflow
    })

    return df, npv, payback_month


def projection_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cash Inflows'], mode='lines', name='Cash Inflows'))
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cash Outflows'], mode='lines', name='Cash Outflows'))
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Net Cashflow'], mode='lines', name='Net Cashflow'))
    fig.add_trace(go.Scatter(x=df['Month'], y=df['Cumulative Cashflow'], mode='lines', name='Cumulative Cashflow'))
    fig.update_layout(title='12–24 Month ROI Projection', xaxis_title='Month', yaxis_title='Amount', margin=dict(l=10, r=10, t=50, b=10))
    return fig


def roadmap_timeline():
    data = [
        dict(Task='Week 1', Start=datetime.today(), Finish=datetime.today()+timedelta(days=7), Phase='Readiness Assessment'),
        dict(Task='Week 2', Start=datetime.today()+timedelta(days=7), Finish=datetime.today()+timedelta(days=14), Phase='Business Value Map'),
        dict(Task='Week 3', Start=datetime.today()+timedelta(days=14), Finish=datetime.today()+timedelta(days=21), Phase='Architecture & Guardrails'),
        dict(Task='Week 4', Start=datetime.today()+timedelta(days=21), Finish=datetime.today()+timedelta(days=28), Phase='ROI Model & Board Deck'),
        dict(Task='Day 30–90', Start=datetime.today()+timedelta(days=30), Finish=datetime.today()+timedelta(days=90), Phase='Quick Wins & Pilot'),
        dict(Task='Month 4–18', Start=datetime.today()+timedelta(days=120), Finish=datetime.today()+timedelta(days=540), Phase='Scale & Operate'),
    ]
    df = pd.DataFrame(data)
    fig = px.timeline(df, x_start='Start', x_end='Finish', y='Task', color='Phase', title='90-Day Execution Roadmap + Scale Plan')
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig

# -----------------------------
# Sidebar (Global Inputs & CTA)
# -----------------------------
st.sidebar.title("⚙️ Configure Preview")
industry = st.sidebar.selectbox("Industry", ["Healthcare", "Biopharma", "SaaS", "Financial Services", "Public Sector", "Other"], index=0)
company_size = st.sidebar.selectbox("Company Size", ["<100", "100–999", "1k–9k", "10k+"], index=1)
currency = st.sidebar.selectbox("Currency", ["$", "€", "£"], index=1)
cta_url = st.sidebar.text_input("CTA URL (Book your audit)", value="https://realtimedata.ai/")
email = st.sidebar.text_input("Your Email (for export)", value="ceo@example.com")

st.sidebar.markdown("---")
st.sidebar.subheader("Guarantee")
st.sidebar.success("30-Day Money Back Guarantee. If you don’t walk away with a clear, ROI-backed AI roadmap your board could act on tomorrow, you don’t pay.")

# Benchmarks by industry (demo values)
benchmarks = {
    "Healthcare": [3.2, 3.4, 2.8, 2.9],
    "Biopharma": [3.5, 3.2, 3.1, 2.7],
    "SaaS": [3.7, 3.8, 3.0, 3.3],
    "Financial Services": [3.4, 3.6, 3.5, 3.0],
    "Public Sector": [2.8, 3.0, 3.1, 2.5],
    "Other": [3.0, 3.1, 2.9, 2.7]
}

# -----------------------------
# Header / Hero
# -----------------------------
st.title("Enterprise AI Readiness & ROI Audit")
st.markdown(
    """
    Transform AI buzzwords into **board-ready ROI** with a 4-week, done-for-you executive roadmap. 
    Avoid disconnected pilots, vendor lock-in, and compliance blind spots.
    """
)
colA, colB, colC = st.columns([2,2,1])
with colA:
    st.info("Who it’s for: CEOs, CFOs, CIO/CTOs, and Healthcare & Biopharma leaders requiring compliance-first AI.")
with colB:
    st.warning("Outcomes: Clarity • Speed • Savings • 7–8 Figure Impact • Executive Confidence")
with colC:
    st.link_button("Book Audit", cta_url, type="primary")

st.markdown("---")

# -----------------------------
# Section 1: Readiness Assessment (Radar)
# -----------------------------
st.header("1) AI Readiness Assessment")
st.caption("Maturity scoring across data quality, infrastructure, governance, and culture — benchmarked to peers.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    dq = st.slider("Data Quality", 0.0, 5.0, 3.0, 0.1)
with c2:
    infra = st.slider("Infrastructure", 0.0, 5.0, 3.0, 0.1)
with c3:
    gov = st.slider("Governance", 0.0, 5.0, 3.0, 0.1)
with c4:
    culture = st.slider("Culture", 0.0, 5.0, 3.0, 0.1)

categories = ["Data Quality", "Infrastructure", "Governance", "Culture"]
user_vals = [dq, infra, gov, culture]
bench = benchmarks.get(industry, benchmarks["Other"])

radar = radar_chart(categories, user_vals, bench, title=f"AI Readiness vs {industry} Peers")
st.plotly_chart(radar, use_container_width=True)

st.markdown("---")

# -----------------------------
# Section 2: Business Value Map (Prioritization)
# -----------------------------
st.header("2) Business Value Map")
st.caption("Identify your top 3–5 AI initiatives by ROI potential, risk, and time-to-value.")

use_cases_catalog = {
    "Claims Denial Reduction": {"impact": 750000, "time": 4, "risk": 2},
    "Patient Outcome Prediction": {"impact": 1200000, "time": 6, "risk": 3},
    "Predictive Staffing": {"impact": 500000, "time": 3, "risk": 2},
    "Sales Forecasting": {"impact": 650000, "time": 3, "risk": 2},
    "Churn Propensity": {"impact": 400000, "time": 2, "risk": 2},
    "RPA for Back Office": {"impact": 300000, "time": 2, "risk": 1},
}

sel = st.multiselect("Select relevant use cases", list(use_cases_catalog.keys()), default=list(use_cases_catalog.keys())[:4])
rows = []
for uc in sel:
    base = use_cases_catalog[uc]
    with st.expander(f"Configure: {uc}"):
        col1, col2, col3 = st.columns(3)
        with col1:
            imp = st.number_input(f"Estimated Impact $/yr – {uc}", min_value=0, value=int(base['impact']), step=50000, key=f"imp_{uc}")
        with col2:
            ttv = st.slider(f"Time-to-Value (months) – {uc}", 1, 12, int(base['time']), key=f"ttv_{uc}")
        with col3:
            risk = st.slider(f"Risk (1=low, 5=high) – {uc}", 1, 5, int(base['risk']), key=f"risk_{uc}")
    # Priority Score: higher impact, lower risk, faster TTV
    score = (imp / 1_000_000) * (1 - (risk - 1) / 4) * (1 / (ttv / 6))
    rows.append({
        'Use Case': uc,
        'Impact $/yr': imp,
        'Time-to-Value (mo)': ttv,
        'Risk (1-5)': risk,
        'Priority Score': score
    })

if rows:
    df_ranked = pd.DataFrame(rows).sort_values('Priority Score', ascending=False)
    st.dataframe(df_ranked, use_container_width=True)
    st.plotly_chart(value_map_chart(df_ranked), use_container_width=True)
    st.success(f"Top 3 priority candidates: {', '.join(df_ranked['Use Case'].head(3).tolist())}")

st.markdown("---")

# -----------------------------
# Section 3: Enterprise Architecture Blueprint (Graph)
# -----------------------------
st.header("3) Enterprise Architecture Blueprint")
st.caption("High-level view of data flow, governance checkpoints, and AI model lifecycle.")

# Use Plotly Sankey to visualize a simplified flow
nodes = [
    "Source Systems\n(EHR/PACS/CRM)",
    "Ingestion & ETL", 
    "Data Lake/Lakehouse", 
    "Governance & Catalog\n(DQ, PII, Lineage)", 
    "Feature Store", 
    "Model Training", 
    "Model Registry", 
    "Deployment\n(API/Batch/BI)", 
    "Monitoring & Drift", 
    "Audit & Compliance\n(HIPAA/GDPR/FDA)"
]

node_idx = {n: i for i, n in enumerate(nodes)}

links = [
    ("Source Systems\n(EHR/PACS/CRM)", "Ingestion & ETL", 8),
    ("Ingestion & ETL", "Data Lake/Lakehouse", 8),
    ("Data Lake/Lakehouse", "Governance & Catalog\n(DQ, PII, Lineage)", 6),
    ("Data Lake/Lakehouse", "Feature Store", 6),
    ("Feature Store", "Model Training", 5),
    ("Model Training", "Model Registry", 4),
    ("Model Registry", "Deployment\n(API/Batch/BI)", 4),
    ("Deployment\n(API/Batch/BI)", "Monitoring & Drift", 4),
    ("Monitoring & Drift", "Audit & Compliance\n(HIPAA/GDPR/FDA)", 3),
]

fig_arch = go.Figure(data=[go.Sankey(
    node=dict(label=nodes, pad=20, thickness=18),
    link=dict(
        source=[node_idx[s] for s, t, v in links],
        target=[node_idx[t] for s, t, v in links],
        value=[v for s, t, v in links]
    )
)])
fig_arch.update_layout(title_text="Data → Governance → ML Lifecycle → Production", font_size=12, margin=dict(l=10, r=10, t=50, b=10))
st.plotly_chart(fig_arch, use_container_width=True)

st.markdown("---")

# -----------------------------
# Section 4: ROI & Investment Model
# -----------------------------
st.header("4) ROI & Investment Model")
st.caption("12–24 month projection with CFO-friendly assumptions.")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    initial_invest = st.number_input(f"Initial CapEx ({currency})", min_value=0, value=250_000, step=25_000)
with col2:
    monthly_opex = st.number_input(f"Monthly OpEx ({currency}/mo)", min_value=0, value=35_000, step=5_000)
with col3:
    base_rev = st.number_input(f"Baseline Monthly Revenue ({currency})", min_value=0, value=5_000_000, step=250_000)
with col4:
    base_cost = st.number_input(f"Baseline Monthly Addressable Cost ({currency})", min_value=0, value=2_000_000, step=100_000)
with col5:
    months = st.slider("Projection Horizon (months)", 12, 36, 24)

col6, col7, col8 = st.columns(3)
with col6:
    rev_uplift_pct = st.slider("Revenue Uplift (%)", 0.0, 15.0, 3.0, 0.1)
with col7:
    cost_reduce_pct = st.slider("Cost Reduction (%)", 0.0, 20.0, 5.0, 0.1)
with col8:
    adoption = st.selectbox("Adoption Curve", ["S-curve", "Linear", "Front-loaded"], index=0)

proj_df, npv, payback = roi_projection(initial_invest, monthly_opex, base_rev, base_cost, rev_uplift_pct, cost_reduce_pct, months=months)

st.plotly_chart(projection_chart(proj_df), use_container_width=True)

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("NPV (12% annual discount)", f"{currency}{npv:,.0f}")
with kpi2:
    st.metric("Payback Period (months)", payback if payback else "> horizon")
with kpi3:
    st.metric("Month {m} Annualized ROI".format(m=months), f"{((proj_df['Net Cashflow'].sum() - (initial_invest + months*monthly_opex)) / max(1, (initial_invest + months*monthly_opex)))*100:.1f}%")

cpa1, cpa2 = st.columns(2)
with cpa1:
    st.plotly_chart(capex_opex_pie(initial_invest, months*monthly_opex), use_container_width=True)
with cpa2:
    st.dataframe(proj_df, use_container_width=True)

# Download buttons
st.download_button(
    label="Download ROI Projection (CSV)",
    data=proj_df.to_csv(index=False).encode('utf-8'),
    file_name="roi_projection.csv",
    mime="text/csv",
)

st.markdown("---")

# -----------------------------
# Section 5: Compliance & Risk Guardrails
# -----------------------------
st.header("5) Compliance & Risk Guardrails")
st.caption("Alignment with HIPAA, GDPR, FDA/EMA, plus AI governance principles: bias, explainability, auditability.")
colx, coly, colz = st.columns(3)
with colx:
    hipaa = st.checkbox("HIPAA – PHI handling, BAA, minimum necessary")
    gdpr = st.checkbox("GDPR – Lawful basis, DPO, DPIA, data subject rights")
with coly:
    fda = st.checkbox("FDA/EMA – Software as a Medical Device guidance")
    audit = st.checkbox("Auditability – lineage, versioning, access logs")
with colz:
    bias = st.checkbox("Bias & Fairness – representative data, parity checks")
    xai = st.checkbox("Explainability – model cards, SHAP/LIME reporting")

if any([hipaa, gdpr, fda, audit, bias, xai]):
    st.success("These guardrails will be tailored in your Blueprint and codified in your governance checkpoints.")

st.markdown("---")

# -----------------------------
# Section 6: 90-Day Execution Roadmap
# -----------------------------
st.header("6) 90-Day Execution Roadmap")
st.caption("Concrete action steps for people, processes, and platforms — with quick wins inside 3 months.")
st.plotly_chart(roadmap_timeline(), use_container_width=True)

st.markdown("---")

# -----------------------------
# Deliverables & CTA
# -----------------------------
st.header("Deliverables")
col_d1, col_d2, col_d3, col_d4 = st.columns(4)
with col_d1:
    st.markdown("**📄 Executive Report (PDF)**\n25–40 pages, C‑suite ready")
with col_d2:
    st.markdown("**🖼️ Architecture Deck (PPT)**\nVisual blueprint for IT & data teams")
with col_d3:
    st.markdown("**📊 ROI Spreadsheet (Excel)**\nScenario models for CFO sign‑off")
with col_d4:
    st.markdown("**👥 Executive Workshop (2h)**\nLeadership walkthrough & Q&A")

st.info("We take on a limited number of audits per quarter to ensure C‑suite depth. Once slots are filled, the next opening may be 4–8 weeks out.")

col_cta1, col_cta2 = st.columns([1,3])
with col_cta1:
    st.link_button("Book Your Audit", cta_url, type="primary")
with col_cta2:
    st.caption("Have procurement questions? Email us: "+ email)

st.markdown("---")

st.caption("© {} Realtime Data Solutions — Enterprise AI Readiness & ROI Audit".format(datetime.now().year))
