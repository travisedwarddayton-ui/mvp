import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Enterprise BVI Dashboard", page_icon="💼", layout="wide")

# -----------------------------
# Weights (enterprise defaults)
# -----------------------------
WEIGHTS = {
    "Decision Dependency": 0.35,
    "Revenue Impact": 0.35,
    "Risk & Compliance": 0.2,
    "Utilization": 0.1
}

# Peer benchmarks (example — replace with industry data)
PEER_BENCHMARKS = {
    "Claims Data": 88,
    "Patient Master Data": 85,
    "Scheduling Data": 70,
    "Marketing Data": 60
}

# -----------------------------
# Functions
# -----------------------------
def compute_bvi(inputs: dict) -> float:
    return round(sum(inputs[dim] * WEIGHTS[dim] for dim in WEIGHTS), 2)

def crit_label(score):
    if score >= 85:
        return "🟢 Mission-Critical"
    elif score >= 70:
        return "🟡 Important"
    else:
        return "🔴 Low Relevance"

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.title("📋 Enterprise Controls")
st.sidebar.caption("Manage datasets to assess business value of information.")
portfolio_mode = st.sidebar.checkbox("Portfolio Mode (assess multiple datasets)", value=True)

# -----------------------------
# Portfolio Mode
# -----------------------------
if portfolio_mode:
    st.title("💼 Business Value of Information (BVI) — Enterprise Portfolio View")

    datasets = ["Claims Data", "Patient Master Data", "Scheduling Data", "Marketing Data"]
    results = []

    for dataset in datasets:
        st.subheader(f"📊 Assessing {dataset}")

        inputs = {}
        for dim in WEIGHTS.keys():
            with st.expander(f"{dim} — standardized question", expanded=False):
                if dim == "Decision Dependency":
                    score = st.slider("What % of executive or mission-critical decisions rely on this dataset?", 0, 100, 80, key=f"{dataset}_{dim}")
                elif dim == "Revenue Impact":
                    score = st.slider("Estimate % of revenue/processes influenced by this dataset", 0, 100, 85, key=f"{dataset}_{dim}")
                elif dim == "Risk & Compliance":
                    score = st.slider("Rate risk exposure if dataset fails (0=none, 100=catastrophic)", 0, 100, 90, key=f"{dataset}_{dim}")
                elif dim == "Utilization":
                    score = st.slider("What % of departments actively use this dataset?", 0, 100, 70, key=f"{dataset}_{dim}")
                else:
                    score = 0
                inputs[dim] = score

                # Evidence upload per dimension
                st.file_uploader(f"Upload evidence for {dim} ({dataset})", 
                                type=["pdf","docx","xlsx","csv","png","jpg"], 
                                key=f"{dataset}_{dim}_evidence")

        bvi_score = compute_bvi(inputs)
        peer = PEER_BENCHMARKS.get(dataset, None)

        results.append({
            "Dataset": dataset,
            "BVI Score": bvi_score,
            "Peer Benchmark": peer,
            "Classification": crit_label(bvi_score)
        })

        st.markdown(f"### {dataset} Score: **{bvi_score}/100** {crit_label(bvi_score)}")
        if peer:
            st.caption(f"Peer Benchmark: {peer} (Industry average)")

        st.divider()

    # -----------------------------
    # Portfolio Results
    # -----------------------------
    df = pd.DataFrame(results)

    st.subheader("🏢 Portfolio Results Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Bar chart
    st.subheader("💶 BVI Scores vs Peer Benchmark")
    fig = px.bar(df, x="Dataset", y="BVI Score", color="Classification", text="BVI Score")
    if "Peer Benchmark" in df.columns:
        fig.add_scatter(x=df["Dataset"], y=df["Peer Benchmark"], mode="lines+markers", name="Peer Benchmark")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # Quadrant view (Condition vs Relevance — IVI vs BVI placeholder)
    st.subheader("🎯 Portfolio Priority Quadrant")
    df["Condition (IVI)"] = [78, 84, 65, 72]  # placeholder IVI scores for demo
    fig2 = px.scatter(df, x="Condition (IVI)", y="BVI Score", size="BVI Score", color="Classification",
                      text="Dataset", labels={"Condition (IVI)":"Data Condition (Trust)", "BVI Score":"Business Relevance"})
    fig2.update_traces(textposition="top center")
    st.plotly_chart(fig2, use_container_width=True)

    # Export
    st.subheader("⬇️ Export Portfolio Results")
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "bvi_portfolio_results.csv", "text/csv")

else:
    st.title("💼 Business Value of Information (BVI) — Single Dataset Mode")
    st.caption("Switch to Portfolio Mode for full enterprise view.")
