# app_current_state_simple.py
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Current State: Vendor Cloud Silos", layout="wide")

st.title("Current State of Radiology Imaging Data")
st.caption("Each vendor cloud is its own silo with archives and data spread across them.")

vendors = [
    "GE Healthcare Cloud",
    "Philips HealthSuite",
    "Agfa Enterprise Imaging",
    "Sectra PACS Cloud",
    "Merative (Merge) Cloud",
    "Ambra Health Cloud",
    "Life Image Exchange"
]

# Fake study counts
study_counts = [5, 4, 3, 6, 2, 4, 3]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(vendors, study_counts, color="#4A90E2", alpha=0.8)
ax.set_xlabel("Number of Studies (example)")
ax.set_title("Studies Scattered Across Vendor Clouds")

st.pyplot(fig)

st.markdown("""
### Key Problem
- Each vendor has **its own cloud archive**.  
- Patient studies are **scattered across multiple silos**.  
- Radiologists must **know the vendor** to locate priors.  
- Leads to **delays, duplicate scans, inefficiency**.
""")
