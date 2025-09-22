# file: ceo_data_strategy_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import datetime

# -------------------------
# Mock Data
# -------------------------
kpis = [
    {"KPI": "ARR", "Definition": "Annual Recurring Revenue", "Status": "Approved", "Owner": "CFO", "Investor Relevance": "High"},
    {"KPI": "CAC", "Definition": "Customer Acquisition Cost", "Status": "Approved", "Owner": "CMO", "Investor Relevance": "High"},
    {"KPI": "Churn", "Definition": "Lost revenue ÷ starting revenue", "Status": "Draft", "Owner": "", "Investor Relevance": "High"},
    {"KPI": "LTV", "Definition": "Customer Lifetime Value", "Status": "Approved", "Owner": "CFO", "Investor Relevance": "High"},
    {"KPI": "Gross Margin", "Definition": "Revenue – COGS", "Status": "Misaligned", "Owner": "", "Investor Relevance": "High"},
]

systems = [
    {"System": "CRM (Salesforce)", "Status": "Connected"},
    {"System": "Finance (NetSuite)", "Status": "Partial"},
    {"System": "Product Telemetry", "Status": "Missing"},
    {"System": "Marketing (HubSpot)", "Status": "Connected"},
]

data_health = {
    "Finance": {"Duplicates": 0.05, "Nulls": 0.08, "FreshnessHrs": 24},
    "Sales": {"Duplicates": 0.12, "Nulls": 0.18, "FreshnessHrs": 72},
    "Product": {"Duplicates": 0.07, "Nulls": 0.10, "FreshnessHrs": 48},
    "Ops": {"Duplicates": 0.04, "Nulls": 0.05, "FreshnessHrs": 12},
}

# -------------------------
# Helper Functions
# -------------------------
def gauge_chart(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={"axis": {"range": [0, 100]}},
        title={"text": title}
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def export_pdf(kpi_df, readiness_score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Baseline Data Strategy – Investor Readiness Report", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, f"Overall Readiness Score: {readiness_score}%", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, "KPI Alignment Status:", ln=True)
    pdf.ln(10)
    for _, row in kpi_df.iterrows():
        pdf.cell(0, 8, f"{row['KPI']} – {row['Status']} – Owner: {row['Owner']}", ln=True)
    filename = "data_strategy_report.pdf"
    pdf.output(filename)
    return filename

# -------------------------
# Streamlit App
# -------------------------
st.set_page_config(page_title="CEO Data Strategy Dashboard", layout="wide")
st.title("📊 CEO Data Strategy Dashboard")
st.write("Executive view of baseline readiness, risks, and next steps.")

# ---- Executive Overview ----
col1, col2, col3 = st.columns(3)
col1.plotly_chart(gauge_chart(68, "Readiness Score"))
col2.plotly_chart(gauge_chart(72, "Confidence in Data"))
col3.plotly_chart(gauge_chart(55, "Investor Risk Index"))

st.markdown("👉 **Interpretation:** Your readiness is progressing but investors may question KPI ownership and data health. Closing these gaps will raise confidence quickly.")

# ---- KPI Definitions ----
st.subheader("1. KPI & Metric Alignment")
kpi_df = pd.DataFrame(kpis)
st.dataframe(kpi_df)

misaligned = kpi_df[kpi_df["Status"].isin(["Draft", "Misaligned"])]
if not misaligned.empty:
    st.warning(f"⚠️ {len(misaligned)} KPIs need alignment: {', '.join(misaligned['KPI'])}")

# ---- System Inventory ----
st.subheader("2. System Inventory & Integration")
sys_df = pd.DataFrame(systems)
st.table(sys_df)

coverage = round((sys_df["Status"].eq("Connected").sum() / len(sys_df)) * 100, 1)
st.progress(coverage/100)
st.write(f"System coverage: {coverage}%")

# ---- Data Health ----
st.subheader("3. Data Quality Deep Dive")
dh_df = pd.DataFrame.from_dict(data_health, orient="index")
dh_df["HealthScore"] = (1 - dh_df["Duplicates"] - dh_df["Nulls"]) * 100
st.dataframe(dh_df)

low_health = dh_df[dh_df["HealthScore"] < 80]
if not low_health.empty:
    st.error(f"⚠️ Issues detected in: {', '.join(low_health.index)}")

# ---- Ownership ----
st.subheader("4. Ownership & Accountability")
owners_missing = kpi_df[kpi_df["Owner"] == ""]
if not owners_missing.empty:
    st.error(f"⚠️ The following KPIs have no owners: {', '.join(owners_missing['KPI'])}")
else:
    st.success("✅ All KPIs have assigned owners.")

# ---- Roadmap ----
st.subheader("5. Roadmap & Recommendations")
st.markdown("""
- **Short-Term (0–3 months):** Define Churn, assign owners for Gross Margin.  
- **Medium-Term (3–6 months):** Connect product telemetry, improve Sales data health.  
- **Long-Term (6–12 months):** Enable cohort analysis, forecasting, and AI readiness.  
""")

# ---- PDF Export ----
if st.button("📄 Export Investor Report"):
    pdf_file = export_pdf(kpi_df, 68)
    with open(pdf_file, "rb") as f:
        st.download_button("Download Report", f, file_name=pdf_file)
