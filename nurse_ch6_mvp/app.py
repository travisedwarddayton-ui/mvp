import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from textwrap import dedent

st.set_page_config(page_title="Data → Wisdom: Interactive Learning Lab", layout="wide")

st.title("📘 Data & Data Processing — Interactive Learning Lab")
st.caption("Inspired by Chapter 6: *Data and Data Processing* — DIKW, DBMS, Big Data, Warehouses, Stewardship, Analytics, and Expert Systems.")

with st.sidebar:
    st.header("Learning Path")
    st.markdown("- DIKW Continuum")
    st.markdown("- Generate & Curate Data")
    st.markdown("- Store & Retrieve (DBMS, SQL)")
    st.markdown("- Analyze & Decide (Dashboards, KDD)")
    st.markdown("- Quiz & Reflection")
    st.divider()
    st.info("💡 Tip: Drag & drop a CSV in the **Data Playground** to explore analytics and run SQL.")

st.subheader("1) DIKW Continuum: From Data ➜ Information ➜ Knowledge ➜ Wisdom")

cols = st.columns(4)
with cols[0]:
    st.markdown("### **Data**")
    st.write("- Raw facts, no context\n- e.g., `98, 116, 58, 68, 18`")
with cols[1]:
    st.markdown("### **Information**")
    st.write("- Data + labels/context\n- e.g., `Temp=98.0, BP=116/68, Pulse=58, Resp=18`")
with cols[2]:
    st.markdown("### **Knowledge**")
    st.write("- Patterns & interpretation\n- Compare to norms, patient context")
with cols[3]:
    st.markdown("### **Wisdom**")
    st.write("- Judicious action\n- Apply knowledge ethically for care")

st.progress(25, text="Progresses as quality & context increase; interactions grow with complexity.")

with st.expander("🧭 Try it: Label the raw data to create information"):
    sample_vals = st.text_input("Raw data (comma-separated):", "98, 116, 58, 68, 18")
    labels = st.multiselect("Pick labels to assign (in order)", ["Temperature", "Systolic BP", "Pulse", "Diastolic BP", "Respiration"], default=["Temperature", "Systolic BP", "Pulse", "Diastolic BP", "Respiration"])
    if st.button("Create Information"):
        try:
            nums = [x.strip() for x in sample_vals.split(",")]
            pairs = list(zip(labels, nums))
            st.success("Information: " + "; ".join([f"{k}={v}" for k,v in pairs]))
        except Exception as e:
            st.error(f"Could not parse: {e}")

st.subheader("2) Big Data in Healthcare: The 6 Vs")
v_cols = st.columns(3)
v_defs = {
    "Volume": "How much data is produced (e.g., 2.5 quintillion bytes/day).",
    "Variety": "Many types: notes, labs, imaging, social posts, IoT streams.",
    "Velocity": "Speed/streaming: sensors & real-time feeds.",
    "Veracity": "Quality/accuracy: noise, bias, missingness.",
    "Value": "Clinical relevance: outcomes, reduced cost, patient benefit.",
    "Variability": "Seasonality & change in data patterns (e.g., flu waves).",
}
for i, (k, v) in enumerate(v_defs.items()):
    with v_cols[i//2]:
        st.markdown(f"**{k}** — {v}")

st.subheader("3) Data States & Security")
cc1, cc2, cc3 = st.columns(3)
with cc1:
    st.markdown("**Data at Rest**")
    st.caption("Stored on disks/archives; protect with encryption & access controls.")
with cc2:
    st.markdown("**Data in Use**")
    st.caption("Being processed/read; most vulnerable; enforce least-privilege + secure compute.")
with cc3:
    st.markdown("**Data in Motion**")
    st.caption("Moving across networks/devices; use transport encryption & integrity checks.")

st.subheader("4) Data Playground: Upload & Explore (Drag & Drop)")
uploaded = st.file_uploader("Drop a CSV here", type=["csv"])
sample_choice = st.checkbox("Use sample dataset (ER_admissions.csv)")

def load_df():
    if uploaded is not None:
        return pd.read_csv(uploaded)
    elif sample_choice:
        return pd.read_csv('ER_admissions.csv')
    else:
        return None

df = load_df()
if df is not None:
    st.success(f"Loaded rows: {len(df):,} • Columns: {len(df.columns)}")
    st.dataframe(df.head(20), use_container_width=True)

    st.markdown("#### Quick Profiling")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Rows", len(df))
    with c2:
        st.metric("Columns", len(df.columns))
    with c3:
        st.metric("Missing Cells", int(df.isna().sum().sum()))

    with st.expander("🔍 Data Quality (Curating) — Missingness & Types"):
        st.write(df.dtypes.to_frame("dtype"))
        st.write("Missing by column:", df.isna().sum())

    st.markdown("#### Descriptive Analytics")
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if num_cols:
        sel = st.selectbox("Pick a numeric column", num_cols)
        st.line_chart(df[sel])
        st.write("Summary statistics:", df[sel].describe())
    else:
        st.info("No numeric columns detected.")

    st.markdown("#### SQL Sandbox (SQLite)")
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")
    query = st.text_area("SQL query", "SELECT COUNT(*) AS n_rows FROM data;")
    if st.button("Run SQL"):
        try:
            res = pd.read_sql_query(query, conn)
            st.dataframe(res, use_container_width=True)
        except Exception as e:
            st.error(f"SQL error: {e}")
    conn.close()
else:
    st.info("👉 Upload a CSV or check **Use sample dataset** to continue.")

st.subheader("5) Storing Data: DBMS Models & Storage Options")
with st.expander("Relational vs NoSQL (quick compare)"):
    st.markdown(dedent("""
**Relational (RDBMS)**  
- Structured tables, SQL, ACID transactions  
- Strong consistency, mature tooling  
- Examples: PostgreSQL, MySQL, SQL Server

**NoSQL**  
- Key-value, document, columnar, graph  
- Flexible schemas, high scalability  
- Examples: MongoDB, Cassandra, Neo4j
"""))

st.caption("Built for learning: DIKW • Data States • Big Data (6Vs) • DBMS & Storage • SQL • Dashboards • KDD • Quiz")
