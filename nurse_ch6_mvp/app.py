
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from io import StringIO
from textwrap import dedent

st.set_page_config(page_title="Data → Wisdom: Interactive Learning Lab", layout="wide")

# ---------- Header ----------
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

# ============== 1) DIKW Continuum ==============
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

# ============== 2) Big Data: The 6 Vs ==============
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

# ============== 3) Data States ==============
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

# ============== 4) Data Playground (Drag & Drop CSV) ==============
st.subheader("4) Data Playground: Upload & Explore (Drag & Drop)")
st.write("Drag & drop a **CSV** to explore descriptive analytics, data quality checks, and run SQL.")

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
    
    # Quick profiling
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
    
    # Simple descriptive analytics
    st.markdown("#### Descriptive Analytics")
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if num_cols:
        sel = st.selectbox("Pick a numeric column", num_cols)
        st.line_chart(df[sel])
        st.write("Summary statistics:", df[sel].describe())
    else:
        st.info("No numeric columns detected.")
    
    # Tiny SQL sandbox (sqlite3)
    st.markdown("#### SQL Sandbox (SQLite)")
    st.caption("Your uploaded table is named **data**. Try: `SELECT COUNT(*) FROM data;`")
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

# ============== 5) DBMS Models & Storage ==============
st.subheader("5) Storing Data: DBMS Models & Storage Options")

with st.expander("Relational vs NoSQL (quick compare)"):
    st.markdown(dedent(\"\"\"
    **Relational (RDBMS)**  
    - Structured tables, SQL, ACID transactions  
    - Strong consistency, mature tooling  
    - Examples: PostgreSQL, MySQL, SQL Server

    **NoSQL**  
    - Key-value, document, columnar, graph  
    - Flexible schemas, high scalability  
    - Examples: MongoDB, Cassandra, Neo4j
    \"\"\"))

cols2 = st.columns(3)
with cols2[0]:
    st.markdown("**Data Warehouse**")
    st.caption("Curated, lightly summarized, append-only; separates analytical from operational workloads.")
with cols2[1]:
    st.markdown("**Data Mart**")
    st.caption("Subject/department-specific subset for focused analytics and faster delivery.")
with cols2[2]:
    st.markdown("**Data Lake**")
    st.caption("Raw, diverse (structured/semi/unstructured); schema-on-read; scalable ingestion.")

# ============== 6) Dashboards (KPI Snapshot) ==============
st.subheader("6) KPI Snapshot Dashboard")
if df is not None:
    # Heuristic KPIs for sample healthcare ER dataset
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("Unique Patients", df["patient_id"].nunique() if "patient_id" in df.columns else len(df))
    with kpi_cols[1]:
        if "wait_minutes" in df.columns:
            st.metric("Median Wait (min)", int(np.nanmedian(df["wait_minutes"])) )
        else:
            st.metric("Median Wait (min)", "—")
    with kpi_cols[2]:
        if "admitted" in df.columns:
            adm_rate = 100*df["admitted"].mean()
            st.metric("Admission Rate", f"{adm_rate:.1f}%")
        else:
            st.metric("Admission Rate", "—")
    with kpi_cols[3]:
        if "triage_level" in df.columns:
            top = df["triage_level"].mode().iloc[0]
            st.metric("Top Triage Level", str(top))
        else:
            st.metric("Top Triage Level", "—")

    # Simple pivot/aggregation
    with st.expander("📊 Group & Aggregate"):
        candidates = [c for c in df.columns if df[c].dtype == "object" or str(df[c].dtype).startswith(("category","bool"))]
        group_col = st.selectbox("Group by (categorical)", candidates or df.columns.tolist())
        metric_col = st.selectbox("Metric column (numeric)", num_cols or df.columns.tolist())
        agg = df.groupby(group_col)[metric_col].mean().reset_index()
        st.bar_chart(agg, x=group_col, y=metric_col)
else:
    st.caption("KPI & charts will appear after loading data.")

# ============== 7) Knowledge Discovery (KDD) Demo ==============
st.subheader("7) Knowledge Discovery (KDD) — Mini Demo")
st.markdown("We’ll simulate a **rule-based classifier** to demonstrate pattern → decision mapping.")
rule_expander = st.expander("Define a simple rule (IF ... THEN ...)")
with rule_expander:
    if df is None:
        st.info("Load data to try rules. The sample dataset includes `wait_minutes`, `triage_level`, and `admitted`.")
    else:
        num_col = st.selectbox("Numeric field for condition", [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])])
        thresh = st.number_input("Threshold (>", value=float(df[num_col].median()) if pd.api.types.is_numeric_dtype(df[num_col]) else 0.0)
        then_label = st.text_input("THEN label", "High Risk")
        if st.button("Apply Rule"):
            pred = (df[num_col] > thresh).astype(int)
            st.write("Predicted positive rate:", f"{pred.mean()*100:.1f}%")
            st.dataframe(pd.DataFrame({num_col: df[num_col], "predicted_label": np.where(pred==1, then_label, "Else")} ).head(30))

# ============== 8) Auto‑graded Quiz ==============
st.subheader("8) Check Your Understanding — Quiz")
questions = [
    {
        "q": "Data in motion is an increasing concern in healthcare because of:",
        "choices": ["Streaming apps", "Monitoring devices", "Mobile devices", "All of the above"],
        "answer": 3,
    },
    {
        "q": "A NoSQL database model is:",
        "choices": [
            "A database where tables are related by keys",
            "An agile system for un/semi-structured data",
            "A database organized purely around entities",
            "A graph of objects and relationships",
        ],
        "answer": 1,
    },
    {
        "q": "Volume, Variety, Velocity, Veracity, Value, Variability describe:",
        "choices": ["Big data", "Data analytics", "Benchmarks", "Dashboards"],
        "answer": 0,
    },
    {
        "q": "The two main components of a DBMS are:",
        "choices": [
            "Data + physical storage structures only",
            "Object identification & storage",
            "Front-end application + Back-end data store",
            "None of the above",
        ],
        "answer": 2,
    },
    {
        "q": "Dashboards are used to:",
        "choices": [
            "See KPIs at a glance",
            "Find anomalies/patterns to predict outcomes",
            "Prescribe actions automatically",
            "All of the above",
        ],
        "answer": 0,
    },
    {
        "q": "Curating data means:",
        "choices": ["Encrypting data", "Ensuring data quality", "Preparing for warehouse", "Moving data between systems"],
        "answer": 1,
    },
    {
        "q": "Which analytics type sets optimal staffing given demand forecasts?",
        "choices": ["Descriptive", "Prescriptive", "Predictive", "All of the above"],
        "answer": 1,
    },
    {
        "q": "Finding anomalies/patterns/correlations to predict outcomes is:",
        "choices": ["Benchmarking", "Patient centric care", "Data mining", "Data analytics"],
        "answer": 2,
    },
]

score = 0
for i, item in enumerate(questions, 1):
    st.markdown(f"**Q{i}. {item['q']}**")
    sel = st.radio("Select one:", item["choices"], key=f"q{i}")
    idx = item["choices"].index(sel) if sel in item["choices"] else -1
    if idx == item["answer"]:
        st.success("✅ Correct")
        score += 1
    else:
        st.warning(f"❌ Not quite. Answer: **{item['choices'][item['answer']]}**")

st.info(f"**Your score:** {score} / {len(questions)}")

# ============== 9) Reflection ==============
st.subheader("9) Reflection")
st.text_area("What aspects of DIKW or data stewardship change how you'll document or analyze care this week?", "")

st.divider()
st.caption("Built for learning: DIKW • Data States • Big Data (6Vs) • DBMS & Storage • SQL • Dashboards • KDD • Quiz")
