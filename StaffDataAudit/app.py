import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="7-Day Staffing Data Audit & Strategy", layout="wide")

# ---- HEADER ----
st.title("7-Day Staffing Data Audit & Strategy ($2,000 Flat Rate)")
st.subheader("See Exactly Where Your Staffing Firm is Making — or Losing — Money")

st.markdown("""
Running a healthcare staffing agency means balancing contracts, payroll, and compliance — often with razor-thin margins.  
Our flat-rate service delivers **measurable financial clarity in just one week**.
""")

# ---- FILE UPLOAD ----
st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload staffing data (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Uploaded Data Preview")
    st.dataframe(df.head())

    # Example calculations
    if "Bill Rate" in df.columns and "Pay Rate" in df.columns:
        df["Gross Margin"] = df["Bill Rate"] - df["Pay Rate"]

    if "Start Date" in df.columns and "End Date" in df.columns:
        df["Start Date"] = pd.to_datetime(df["Start Date"])
        df["End Date"] = pd.to_datetime(df["End Date"])
        df["Time to Fill (days)"] = (df["End Date"] - df["Start Date"]).dt.days

    # ---- METRICS ----
    st.header("Expected Outcomes Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Gross Margin per Contract", f"${df['Gross Margin'].mean():.2f}")
    with col2:
        if "Time to Fill (days)" in df.columns:
            st.metric("Avg Time-to-Fill", f"{df['Time to Fill (days)'].mean():.1f} days")
    with col3:
        st.metric("Projected Faster Payments", "10–20%")
    with col4:
        st.metric("Admin Hours Saved", "30%+")

    # ---- VISUALS ----
    st.subheader("Margin by Contract")
    st.bar_chart(df.set_index("Contract")["Gross Margin"])

    if "Time to Fill (days)" in df.columns:
        st.subheader("Recruiter Efficiency (Time-to-Fill)")
        st.line_chart(df["Time to Fill (days)"])

else:
    st.info("⬅️ Upload your staffing data CSV to see your audit results.")

# ---- FOOTER ----
st.markdown("---")
st.markdown("""
✅ Margin by Contract Report  
✅ Time-to-Fill Analysis  
✅ Payroll vs. Bill Rate Dashboard  
✅ Collections & Cash Flow Report  
✅ Executive Roadmap  

👉 By the end of 7 days, you’ll know exactly which contracts are worth growing, which clients hurt your margins, and how to protect cash flow — for a flat **$2,000**.
""")
