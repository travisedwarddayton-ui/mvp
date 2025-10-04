# app_pain_matrix.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

st.set_page_config(page_title="Radiology Workflow Pain Matrix", layout="wide")

st.title("Radiology Vendor Clouds ↔ Hospital (As-Is)")

# Vendor list (grid)
vendors = [
    "GE Healthcare", "Philips Healthcare", "Agfa HealthCare", "Sectra",
    "Merative (Merge)", "Fujifilm (Synapse)", "Change Healthcare / Optum",
    "Infinitt Healthcare", "Novarad", "Hyland Healthcare", "Intelerad",
    "Ambra Health", "Life Image"
]

cols = 4
rows = (len(vendors) + cols - 1) // cols
x_spacing, y_spacing = 0.25, 0.18

fig, ax = plt.subplots(figsize=(15, 10))

# Vendor grid
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = 0.2 + col * x_spacing
    y = 1.0 - row * y_spacing
    cloud = Ellipse((x, y), width=0.22, height=0.10,
                    facecolor="#cfe8ff", edgecolor="blue", linewidth=1.2)
    ax.add_patch(cloud)
    ax.text(x, y, v, ha="center", va="center", fontsize=9, color="navy", weight="bold")

# Hospital
hospital_x, hospital_y = 0.5, -0.1
hospital = Rectangle((hospital_x-0.2, hospital_y-0.05), 0.4, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=13, weight="bold", color="black")

# Bi-directional arrow
arrow = FancyArrowPatch((0.5, 0.25), (0.5, -0.05),
                        arrowstyle="<->", mutation_scale=20,
                        linewidth=2, color="black")
ax.add_patch(arrow)
ax.text(0.52, 0.1, "Data Movement", fontsize=10, rotation=90, va="center")

ax.set_xlim(0, 1.1)
ax.set_ylim(-0.2, 1.2)
ax.axis("off")

st.pyplot(fig)

# ---- Pain Matrix Table ----
st.markdown("## Pain Points in Radiology Workflow (Fact-Checkable)")

data = [
    ["Data fragmented across 13+ vendor silos", "High", "Constantly",
     "Frustration, burnout", "Revenue leakage, lost throughput",
     "No unified patient view", "Constant app toggling", ":contentReference[oaicite:0]{index=0}"],
    ["No universal interoperability layer", "High", "Constantly",
     "Clinician stress", "High IT integration cost",
     "Limited knowledge transfer", "Manual routing between RIS/PACS/EHR", ":contentReference[oaicite:1]{index=1}:contentReference[oaicite:2]{index=2}"],
    ["Radiologists waste time finding priors", "Medium–High", "Constantly",
     "Fatigue, morale loss", "Lost billable reads (minutes per case)",
     "Cognitive overload", "Slower turnaround, missed SLAs", ":contentReference[oaicite:3]{index=3}"],
    ["Duplicate scans ordered", "High", "Medium",
     "Patient anxiety", "Duplicate scan cost, wasted scanner hours",
     "Lost insight from scattered priors", "Redundant workflows", ":contentReference[oaicite:4]{index=4}"],
    ["Compliance gaps (HIPAA/GDPR)", "High", "Constantly",
     "Anxiety of breach liability", "Avg breach ~$10.93M",
     "Policy uncertainty", "No centralized audit", ":contentReference[oaicite:5]{index=5}"],
    ["Inconsistent analytics & AI integration", "Medium", "Constantly",
     "Clinician disappointment", "Missed ROI, failed AI pilots",
     "No enterprise-wide learning", "Manual patchwork", ":contentReference[oaicite:6]{index=6}"],
    ["High IT maintenance burden", "Medium–High", "Medium",
     "IT staff burnout", "~$300K/yr downtime",
     "Institutional knowledge loss", "Vendor upgrades break workflows", ":contentReference[oaicite:7]{index=7}"],
    ["Vendor lock-in", "High", "Medium",
     "Feeling trapped", "High switching costs",
     "Loss of data control", "Inflexible workflows", ":contentReference[oaicite:8]{index=8}"],
    ["Delays in diagnosis & care", "High", "Constantly",
     "Patient stress, worse outcomes", "Longer LOS, higher costs",
     "Incomplete priors = errors", "Every workflow slowed", ":contentReference[oaicite:9]{index=9}"],
]

df = pd.DataFrame(data, columns=[
    "Pain Point", "Severity", "Frequency", "Emotional Pain",
    "Financial Pain", "Knowledge Pain", "Process Pain", "Reference"
])

st.dataframe(df, use_container_width=True)
