import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ----------------------------
# Mock Data
# ----------------------------
np.random.seed(42)

claims = pd.DataFrame({
    "Claim ID": range(1, 501),
    "Status": np.random.choice(["Approved", "Denied"], size=500, p=[0.8, 0.2]),
    "Reason": np.random.choice(
        ["Missing Info", "Coding Error", "Duplicate Claim", "Not Covered", "Late Submission"],
        size=500
    ),
    "Amount": np.random.randint(100, 1000, size=500),
    "Submission Date": pd.date_range("2025-01-01", periods=500, freq="D")
})

# Filter denied claims
denied_claims = claims[claims["Status"] == "Denied"]

# ----------------------------
# UI
# ----------------------------
st.set_page_config(page_title="Claims Denial Tracker", page_icon="💰", layout="wide")

st.title("💰 Claims Denial Dashboard")
st.subheader("Track, analyze, and reduce your rejected claims")

# KPI cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Claims", f"{len(claims)}")
with col2:
    st.metric("Denied Claims", f"{len(denied_claims)} ({len(denied_claims)/len(claims)*100:.1f}%)")
with col3:
    st.metric("Revenue Lost (€)", f"{denied_claims['Amount'].sum():,}")

# ----------------------------
# Charts
# ----------------------------

st.markdown("### 📊 Denials by Reason")
reason_chart = (
    alt.Chart(denied_claims)
    .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
    .encode(
        x=alt.X("count()", title="Number of Denials"),
        y=alt.Y("Reason", sort="-x"),
        color=alt.Color("Reason", legend=None)
    )
)
st.altair_chart(reason_chart, use_container_width=True)

st.markdown("### 📈 Denials Over Time")
time_chart = (
    alt.Chart(denied_claims)
    .mark_line(point=True)
    .encode(
        x="Submission Date:T",
        y="sum(Amount):Q",
        color=alt.value("#E45756")
    )
)
st.altair_chart(time_chart, use_container_width=True)

# ----------------------------
# Data Table
# ----------------------------
st.markdown("### 📋 Denied Claims Details")
st.dataframe(denied_claims[["Claim ID", "Reason", "Amount", "Submission Date"]])

# ----------------------------
# CTA
# ----------------------------
st.success("✅ Imagine cutting these denials by 25% in 30 days. That's €{:,.0f} in extra cash flow.".format(denied_claims['Amount'].sum() * 0.25))
