import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Enterprise IVI Assessment", page_icon="📊", layout="wide")

# -----------------------------
# Config (weights for dimensions)
# -----------------------------
WEIGHTS = {
    "Accuracy": 0.3,
    "Completeness": 0.2,
    "Consistency": 0.15,
    "Timeliness": 0.15,
    "Validity": 0.1,
    "Uniqueness": 0.05,
    "Integrity": 0.05
}

# -----------------------------
# Header
# -----------------------------
st.title("🏢 Intrinsic Value of Information (IVI) Assessment")
st.caption("Enterprise-grade evaluation of data condition across quality dimensions")

col1, col2 = st.columns(2)
with col1:
    dataset_name = st.text_input("Dataset / Domain Name", "Patient Master Data")
with col2:
    st.metric("Assessment Date", datetime.now().strftime("%Y-%m-%d"))

st.divider()

# -----------------------------
# Capture Inputs
# -----------------------------
st.subheader("📋 Data Quality Inputs")

inputs = {}
for dim, weight in WEIGHTS.items():
    with st.expander(f"{dim} (Weight {int(weight*100)}%)", expanded=True):
        if dim == "Accuracy":
            score = st.slider("Percentage of records correct vs source of truth", 0, 100, 80)
        elif dim == "Completeness":
            score = st.slider("Percentage of mandatory fields populated", 0, 100, 75)
        elif dim == "Consistency":
            score = st.slider("Percentage of cross-system matches", 0, 100, 70)
        elif dim == "Timeliness":
            score = st.slider("Percentage of records within freshness SLA", 0, 100, 65)
        elif dim == "Validity":
            score = st.slider("Percentage of values passing format/business rules", 0, 100, 82)
        elif dim == "Uniqueness":
            score = st.slider("Percentage of records free of duplicates", 0, 100, 90)
        elif dim == "Integrity":
            score = st.slider("Percentage of referential integrity checks passed", 0, 100, 85)
        else:
            score = 0
        inputs[dim] = score

st.divider()

# -----------------------------
# Compute IVI Score
# -----------------------------
ivi_score = sum(inputs[dim] * weight for dim, weight in WEIGHTS.items())
ivi_score = round(ivi_score, 2)

# -----------------------------
# Output: Graph
# -----------------------------
st.subheader("📊 IVI Results")

colA, colB = st.columns([1,1])

with colA:
    st.metric(f"{dataset_name} IVI Score", f"{ivi_score}/100")

with colB:
    if ivi_score >= 85:
        st.success("🟢 Excellent intrinsic data value")
    elif ivi_score >= 70:
        st.warning("🟡 Moderate intrinsic data value")
    else:
        st.error("🔴 Low intrinsic data value — high risk")

# Radar chart of all dimensions
df_plot = pd.DataFrame({
    "Dimension": list(inputs.keys()),
    "Score": list(inputs.values())
})

fig = px.line_polar(df_plot, r="Score", theta="Dimension", line_close=True, range_r=[0,100])
fig.update_traces(fill="toself", name="IVI")
fig.update_layout(title=f"Intrinsic Value of Information — {dataset_name}", height=500)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Evidence Upload (Audit Trail)
# -----------------------------
st.subheader("📎 Upload Evidence")
st.file_uploader("Attach profiling reports, DQ dashboards, policies", 
                 type=["pdf","docx","xlsx","csv","png","jpg"], 
                 accept_multiple_files=True)

# -----------------------------
# Export
# -----------------------------
st.subheader("⬇️ Export Results")
df_export = pd.DataFrame([{"Dataset": dataset_name, **inputs, "IVI Score": ivi_score}])
st.download_button("Download CSV", df_export.to_csv(index=False).encode("utf-8"), "ivi_results.csv", "text/csv")
