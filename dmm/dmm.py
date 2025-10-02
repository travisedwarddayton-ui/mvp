
import json
import math
from datetime import datetime
from io import StringIO, BytesIO

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Data Management Maturity Intake",
    page_icon="📊",
    layout="wide",
)

# -------------------------------
# Load Config
# -------------------------------
@st.cache_data
def load_dimensions():
    with open("dmm_dimensions.json", "r") as f:
        return json.load(f)

cfg = load_dimensions()

DIMENSIONS = cfg["dimensions"]
LEVEL_LABELS = cfg["level_labels"]  # 1..5
PEER_BENCHMARK = cfg.get("peer_benchmark", {})  # optional benchmark overlay 1..5 per dimension
OVERALL_WEIGHTS = {d["key"]: d.get("weight", 1.0) for d in DIMENSIONS}

# -------------------------------
# Helper Functions
# -------------------------------
def maturity_to_text(level: float) -> str:
    # map to label (round to nearest int 1..5)
    k = int(round(level))
    k = max(1, min(5, k))
    return LEVEL_LABELS[str(k)]

def compute_scores(responses: dict):
    """Compute per sub-dimension, per dimension, and overall maturity scores (1..5)."""
    sub_scores = {}
    dim_scores = {}
    for dim in DIMENSIONS:
        dkey = dim["key"]
        sub_list = dim["sub_dimensions"]
        d_scores = []
        for sub in sub_list:
            skey = f"{dkey}:{sub['key']}"
            val = responses.get(skey, None)
            if val is None:
                continue
            d_scores.append(val)
            sub_scores[skey] = val
        dim_scores[dkey] = sum(d_scores)/len(d_scores) if d_scores else 0.0

    # overall weighted average, plus weakest link note
    total_w = 0.0
    total = 0.0
    for dkey, dscore in dim_scores.items():
        w = OVERALL_WEIGHTS.get(dkey, 1.0)
        total += dscore * w
        total_w += w
    overall = (total / total_w) if total_w else 0.0
    weakest = min(dim_scores.items(), key=lambda kv: kv[1]) if dim_scores else (None, 0.0)

    return sub_scores, dim_scores, overall, weakest

def next_step_recommendations(dim_scores):
    """Generate targeted next steps for any dimension < 3.5."""
    recs = []
    for dim in DIMENSIONS:
        dkey = dim["key"]
        score = dim_scores.get(dkey, 0.0)
        if score < 3.5:
            recs.append({
                "dimension": dim["name"],
                "score": score,
                "recommendations": dim.get("next_steps", [])
            })
    return recs

def build_radar(dim_scores):
    cats = [d["name"] for d in DIMENSIONS]
    vals = [dim_scores.get(d["key"], 0.0) for d in DIMENSIONS]
    # Close the radar
    cats += [cats[0]]
    vals += [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals, theta=cats, fill="toself", name="Your score"))
    # Optional peer overlay
    if PEER_BENCHMARK:
        bvals = [PEER_BENCHMARK.get(d["key"], None) for d in DIMENSIONS]
        if all(v is not None for v in bvals):
            bvals += [bvals[0]]
            fig.add_trace(go.Scatterpolar(r=bvals, theta=cats, fill="none", name="Peer benchmark"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5], tickvals=[1,2,3,4,5])), showlegend=True, height=520)
    return fig

def build_heatmap(responses):
    # Build a matrix of sub-dimensions (rows) vs score, grouped by dimension
    rows = []
    y_labels = []
    x_labels = ["Score (1-5)"]
    for dim in DIMENSIONS:
        for sub in dim["sub_dimensions"]:
            skey = f"{dim['key']}:{sub['key']}"
            score = responses.get(skey, 0.0)
            rows.append([score])
            y_labels.append(f"{dim['name']} — {sub['name']}")
    z = rows
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x_labels,
        y=y_labels,
        zmin=1, zmax=5,
        colorbar=dict(title="Maturity")
    ))
    fig.update_layout(height=640, yaxis=dict(autorange="reversed"))
    return fig

def overall_badge(overall):
    label = maturity_to_text(overall)
    if overall >= 4.5:
        color = "✅"
    elif overall >= 3.5:
        color = "🟢"
    elif overall >= 2.5:
        color = "🟡"
    else:
        color = "🟠"
    return f"{color} **Overall Level {overall:.1f} — {label}**"

def to_results_dataframe(responses, dim_scores, overall):
    rows = []
    for dim in DIMENSIONS:
        dkey = dim["key"]
        # dimension row
        rows.append({
            "type": "dimension",
            "key": dkey,
            "name": dim["name"],
            "score": dim_scores.get(dkey, 0.0),
            "descriptor": maturity_to_text(dim_scores.get(dkey, 0.0))
        })
        for sub in dim["sub_dimensions"]:
            skey = f"{dkey}:{sub['key']}"
            rows.append({
                "type": "sub-dimension",
                "key": skey,
                "name": f"{dim['name']} — {sub['name']}",
                "score": responses.get(skey, 0.0),
                "descriptor": sub["levels"].get(str(int(round(responses.get(skey, 0.0) or 1)))),  # nearest descriptor
            })
    rows.append({
        "type": "overall",
        "key": "overall",
        "name": "Overall",
        "score": overall,
        "descriptor": maturity_to_text(overall)
    })
    return rows

# -------------------------------
# Sidebar (Meta & Actions)
# -------------------------------
st.sidebar.title("📋 Assessment Controls")

with st.sidebar.popover("ℹ️ How scoring works"):
    st.markdown("""
- Each **sub-dimension** is scored **1–5** using anchored descriptors.
- A **dimension score** is the average of its sub-dimensions.
- The **overall score** is a weighted average across dimensions.
- Graphs update **in real time** as you answer.
""")

client_name = st.sidebar.text_input("Client / Org name", value="Acme Health")
assessor = st.sidebar.text_input("Assessor", value="Travis Dayton")
date_str = st.sidebar.text_input("Assessment date", value=datetime.now().strftime("%Y-%m-%d"))
peer_toggle = st.sidebar.checkbox("Show peer benchmark overlay", value=True)

st.sidebar.divider()

# Results export
export_requested = st.sidebar.checkbox("Prepare results for export", value=False)

# -------------------------------
# Main Layout
# -------------------------------
st.title("📊 Data Management Maturity — Interactive Intake")
st.caption("Answer each area with the statement that best describes your current practice. Charts update live.")

responses = {}

# -------------------------------
# Intake Form (Interactive)
# -------------------------------
for dim in DIMENSIONS:
    st.subheader(f"{dim['icon']} {dim['name']}")
    cols = st.columns([2, 1], vertical_alignment="top")
    with cols[0]:
        st.markdown(dim["description"])
    with cols[1]:
        st.markdown(f"**Weight:** {dim.get('weight',1.0)}")

    with st.expander("Answer the sub-dimensions", expanded=True):
        for sub in dim["sub_dimensions"]:
            skey = f"{dim['key']}:{sub['key']}"
            st.markdown(f"**{sub['name']}**")
            # Anchored radio with 5 descriptors
            options = [1,2,3,4,5]
            labels = [f"{i}. {sub['levels'][str(i)]}" for i in options]
            # Show radio with index labels
            idx = st.radio(
                label=f"Choose the statement that best matches",
                options=list(range(5)),
                format_func=lambda i: labels[i],
                key=skey
            )
            responses[skey] = options[idx]
            st.markdown("---")

    # Optional evidence upload
    with st.expander("📎 (Optional) Upload evidence (policies, screenshots, logs)"):
        st.file_uploader(
            "Drop files here (not uploaded to server unless you implement storage)",
            type=["pdf","docx","pptx","xlsx","csv","png","jpg"],
            accept_multiple_files=True,
            key=f"upload-{dim['key']}"
        )

    st.divider()

# -------------------------------
# Compute Scores
# -------------------------------
sub_scores, dim_scores, overall, weakest = compute_scores(responses)

# -------------------------------
# KPI Header
# -------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(overall_badge(overall))
with col2:
    if weakest[0] is not None:
        wdim_key, wscore = weakest
        wname = next((d["name"] for d in DIMENSIONS if d["key"]==wdim_key), wdim_key)
        st.markdown(f"🔎 **Weakest area:** {wname} — {wscore:.1f}")
with col3:
    # Progress to next whole level
    next_level = math.floor(overall) + 1 if overall < 5 else 5
    to_next = max(0.0, next_level - overall)
    prog = (overall - math.floor(overall)) if overall < 5 else 1.0
    st.markdown(f"🎯 **Progress to Level {next_level}:**")
    st.progress(min(max(prog,0.0),1.0), text=f"{(prog*100):.0f}% toward Level {next_level}")

st.markdown("---")

# -------------------------------
# Charts
# -------------------------------
left, right = st.columns([1,1])

with left:
    st.markdown("### 🧭 Radar (by dimension)")
    if not peer_toggle:
        # Remove overlay if user turned it off
        backup = cfg.get("peer_benchmark", {}).copy()
        cfg["peer_benchmark"] = {}
        fig = build_radar(dim_scores)
        cfg["peer_benchmark"] = backup
    else:
        fig = build_radar(dim_scores)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### 🔥 Heatmap (by sub-dimension)")
    h = build_heatmap(responses)
    st.plotly_chart(h, use_container_width=True)

# -------------------------------
# Recommendations
# -------------------------------
st.markdown("### 🧩 Targeted Recommendations")
recs = next_step_recommendations(dim_scores)
if recs:
    for r in recs:
        with st.expander(f"Improve **{r['dimension']}** (current {r['score']:.1f})"):
            for i, step in enumerate(r["recommendations"], start=1):
                st.markdown(f"- {step}")
else:
    st.success("Nice! All dimensions are ≥ 3.5. Consider optimization/automation roadmaps.")

# -------------------------------
# Export
# -------------------------------
if export_requested:
    st.markdown("### ⤵️ Export Results")
    rows = to_results_dataframe(responses, dim_scores, overall)
    out_df = px.data.tips()  # placeholder to keep namespace warm
    # Build CSV
    import pandas as pd
    df = pd.DataFrame(rows)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV (scores + descriptors)",
        data=csv_bytes,
        file_name=f"{client_name.replace(' ','_')}_DMM_{date_str}.csv",
        mime="text/csv"
    )

    # Export JSON
    export_payload = {
        "client": client_name,
        "assessor": assessor,
        "date": date_str,
        "dimension_scores": dim_scores,
        "overall": overall,
        "level_text": maturity_to_text(overall),
        "responses": responses,
    }
    json_bytes = json.dumps(export_payload, indent=2).encode("utf-8")
    st.download_button(
        "Download JSON (detailed results)",
        data=json_bytes,
        file_name=f"{client_name.replace(' ','_')}_DMM_{date_str}.json",
        mime="application/json"
    )

st.markdown("---")
st.caption("© 2025 Realtime Data Solutions — Data Management Maturity Intake")
