import streamlit as st
import pandas as pd
import numpy as np

# --- Sample Data (simulated DICOM metadata) ---
data = {
    "PatientID": ["123", "123", "456", "789"],
    "Modality": ["CT", "CT", "MR", "XR"],
    "StudyDate": ["2023-01-05", "2023-01-05", "2024-02-10", "2025-03-01"],
    "BodyPartExamined": ["CHEST", "CHEST", "BRAIN", "KNEE"],
    "Vendor": ["GE", "Philips", "Siemens", "GE"]
}
df = pd.DataFrame(data)

# --- Streamlit UI ---
st.set_page_config(page_title="Radiology Workflow Accelerator", layout="wide")

st.title("🩻 Radiology Workflow Accelerator")
st.write("Vendor-neutral layer to normalize, route, and prepare imaging data for analytics.")

# Section 1: Data Preview
st.header("1. Incoming Studies (Raw PACS Data)")
st.dataframe(df)

# Section 2: Normalization
st.header("2. Metadata Normalization")
df["BodyPartExamined"] = df["BodyPartExamined"].str.upper()
df["StudyDate"] = pd.to_datetime(df["StudyDate"])
df["NormalizedModality"] = df["Modality"].replace({"XR": "X-RAY", "MR": "MRI"})
st.dataframe(df)

# Section 3: Routing Rules
st.header("3. Routing to Storage Tiers")
storage_map = {
    "CT": "Short-term Cloud (30 days)",
    "MRI": "Long-term Archive",
    "X-RAY": "Compliance Vault"
}
df["StorageTarget"] = df["NormalizedModality"].map(storage_map).fillna("General Archive")
st.dataframe(df[["PatientID", "NormalizedModality", "StorageTarget"]])

# Section 4: Analytics Conversion
st.header("4. Analytics Pipeline (DICOM → Research Format)")
conversion_choice = st.selectbox("Select Output Format", ["NIfTI", "Parquet", "HL7-FHIR JSON"])
st.success(f"Studies will be converted to **{conversion_choice}** for downstream analytics.")

# Section 5: Workflow Map
st.header("5. Workflow Visualization")
st.graphviz_chart("""
digraph {
    PACS [shape=box, style=filled, color=lightblue, label="PACS/Vendor Clouds"]
    Normalization [shape=ellipse, style=filled, color=lightgreen, label="Metadata Normalization"]
    Routing [shape=box, style=filled, color=lightyellow, label="Routing Rules"]
    Analytics [shape=ellipse, style=filled, color=lightpink, label="Analytics Formats"]
    Archive [shape=box, style=filled, color=lightgray, label="Compliance Archive"]

    PACS -> Normalization -> Routing
    Routing -> Analytics
    Routing -> Archive
}
""")

st.info("✅ This demo shows how studies move from **multi-vendor PACS** → **normalized metadata** → **proper storage/analytics pipelines**.")
