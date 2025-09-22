# file: baseline_data_strategy_app.py
import streamlit as st
import pandas as pd

# -------------------------
# Mock Data (replace with Firebase, Sheets, or Snowflake later)
# -------------------------
kpis = {
    "ARR": {"defined": True, "owner": "CFO"},
    "CAC": {"defined": True, "owner": "CMO"},
    "Churn": {"defined": False, "owner": None},
    "LTV": {"defined": True, "owner": "CFO"},
    "Gross Margin": {"defined": False, "owner": None},
}

data_health = {
    "Finance": 0.92,
    "Sales": 0.78,
    "Product": 0.85,
    "Ops": 0.67,
}

# -------------------------
# Streamlit App
# -------------------------
st.set_page_config(page_title="Baseline Data Strategy", layout="wide")

st.title("📊 Baseline Data Strategy Dashboard")
st.write("An executive view of your data foundation readiness.")

# ---- KPI Definitions Progress ----
defined_kpis = sum(1 for k in kpis if kpis[k]["defined"])
total_kpis = len(kpis)
progress = defined_kpis / total_kpis

st.subheader("1. KPI Definitions")
st.progress(progress)
st.write(f"{defined_kpis}/{total_kpis} KPIs defined")

# Show KPI Table
df_kpis = pd.DataFrame([
    {"KPI": k, "Defined": "✅" if v["defined"] else "❌", "Owner": v["owner"] or "Unassigned"}
    for k, v in kpis.items()
])
st.table(df_kpis)

# ---- Data Health ----
st.subheader("2. Data Health Snapshot")
col1, col2, col3, col4 = st.columns(4)
for (domain, score), col in zip(data_health.items(), [col1, col2, col3, col4]):
    color = "🟢" if score > 0.85 else "🟡" if score > 0.7 else "🔴"
    col.metric(domain, f"{score*100:.0f}%", color)

# ---- Ownership ----
st.subheader("3. Ownership Tracker")
unassigned = [k for k, v in kpis.items() if not v["owner"]]
if unassigned:
    st.warning(f"⚠️ The following KPIs need owners: {', '.join(unassigned)}")
else:
    st.success("✅ All KPIs have owners assigned.")

# ---- Investor Readiness ----
st.subheader("4. Investor Readiness Meter")
readiness = round((progress + (sum(data_health.values())/len(data_health)))/2, 2)
st.metric("Investor Readiness", f"{readiness*100:.0f}%", "Target: 90%+")

# ---- Call to Action ----
st.subheader("Next Step")
st.info("📅 Schedule a Data Strategy Review to finalize ownership and improve readiness.")
