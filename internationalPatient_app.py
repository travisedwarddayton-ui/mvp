import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime as dt

st.set_page_config(page_title="Rare Disease RWD Dashboard", page_icon="🧬", layout="wide")

# --------------------------
# Mock synthetic registry data
# --------------------------
np.random.seed(42)
n = 300
data = pd.DataFrame({
    "patient_id": range(1, n+1),
    "disease": np.random.choice(
        ["Cystic Fibrosis", "SMA", "Epidermolysis Bullosa", "Haemophilia", "Pulmonary Fibrosis"],
        size=n, p=[0.25,0.2,0.15,0.2,0.2]
    ),
    "country": np.random.choice(["Ireland","Spain","France","Germany","UK"], size=n),
    "genotype": np.random.choice(["Genotype A","Genotype B","Genotype C","Unknown"], size=n, p=[0.3,0.3,0.2,0.2]),
    "dob": pd.to_datetime(np.random.randint(1960,2020,n), format='%Y'),
    "consent": np.random.choice([True, False], size=n, p=[0.9,0.1]),
    "last_visit": pd.to_datetime(np.random.randint(2018,2024,n), format='%Y')
})

# Compliance completeness
data["has_dob"] = ~data["dob"].isna()
data["has_consent"] = data["consent"]
data["shareable"] = data["has_dob"] & data["has_consent"]

# --------------------------
# Sidebar filters
# --------------------------
st.sidebar.title("Filters")
sel_disease = st.sidebar.multiselect("Disease", sorted(data["disease"].unique()), default=None)
sel_country = st.sidebar.multiselect("Country", sorted(data["country"].unique()), default=None)

df = data.copy()
if sel_disease:
    df = df[df["disease"].isin(sel_disease)]
if sel_country:
    df = df[df["country"].isin(sel_country)]

# --------------------------
# Overview KPIs
# --------------------------
st.title("🧬 Rare Disease Real-World Data Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Patients", len(df))
col2.metric("Shareable Data", f"{df['shareable'].mean()*100:.1f}%")
col3.metric("With Consent", f"{df['consent'].mean()*100:.1f}%")
col4.metric("Countries", df["country"].nunique())

# --------------------------
# Charts
# --------------------------
st.subheader("Patients by Disease")
disease_chart = (
    alt.Chart(df).mark_bar().encode(
        x=alt.X("disease:N", title="Disease"),
        y=alt.Y("count():Q", title="Patients"),
        color="disease:N",
        tooltip=["disease", "count()"]
    )
)
st.altair_chart(disease_chart, use_container_width=True)

st.subheader("Patients by Country")
country_chart = (
    alt.Chart(df).mark_bar().encode(
        x=alt.X("country:N", title="Country"),
        y=alt.Y("count():Q", title="Patients"),
        color="country:N",
        tooltip=["country", "count()"]
    )
)
st.altair_chart(country_chart, use_container_width=True)

st.subheader("Genotype Distribution (with Consent)")
geno_chart = (
    alt.Chart(df[df["consent"]==True]).mark_arc().encode(
        theta="count():Q",
        color="genotype:N",
        tooltip=["genotype", "count()"]
    )
)
st.altair_chart(geno_chart, use_container_width=True)

# --------------------------
# Compliance Check
# --------------------------
st.subheader("Compliance & Data Readiness")
compliance = pd.DataFrame({
    "Check": ["Patients with Consent","Patients with DOB","Shareable Records"],
    "Percent": [
        df["consent"].mean()*100,
        df["has_dob"].mean()*100,
        df["shareable"].mean()*100
    ]
})
st.table(compliance)

# --------------------------
# Data Download
# --------------------------
st.download_button(
    "⬇️ Download Current Subset (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    "rare_disease_subset.csv",
    "text/csv"
)
