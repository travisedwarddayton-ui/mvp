# radiology_pain_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

st.set_page_config(page_title="Radiology Workflow Pain Validation", layout="wide")

st.title("Radiology Vendor Clouds ↔ Hospital (As-Is)")

# --- Vendor Diagram ---
vendors = [
    "GE Healthcare", "Philips Healthcare", "Agfa HealthCare", "Sectra",
    "Merative (Merge)", "Fujifilm (Synapse)", "Change Healthcare / Optum",
    "Infinitt Healthcare", "Novarad", "Hyland Healthcare", "Intelerad",
    "Ambra Health", "Life Image"
]

cols = 4
x_spacing, y_spacing = 0.25, 0.18

fig, ax = plt.subplots(figsize=(15, 10))

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
# Add arrows from each vendor to hospital
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = 0.2 + col * x_spacing
    y = 1.0 - row * y_spacing
    arrow = FancyArrowPatch((x, y-0.05), (hospital_x, hospital_y+0.05),
                            arrowstyle="-|>", mutation_scale=10,
                            linewidth=1, color="gray", alpha=0.6)
    ax.add_patch(arrow)


# --- Pain Points Table ---
st.markdown("## Pain Points in Radiology Workflow")

pain_data = [
    ["Data fragmented across 13+ vendor silos", "High", "Constantly",
     "Frustration, burnout", "Revenue leakage, lost throughput",
     "No unified patient view", "Constant app toggling", "Radiology Workflow Requirements (2025)"],
    ["No universal interoperability layer", "High", "Constantly",
     "Clinician stress", "High IT integration cost",
     "Limited knowledge transfer", "Manual routing RIS/PACS/EHR", "Imaging Workflow Enhancement (2025)"],
    ["Radiologists waste time finding priors", "Medium–High", "Constantly",
     "Fatigue, morale loss", "Lost billable reads", 
     "Cognitive overload", "Slower turnaround", "Radiology Workflow Requirements (2025)"],
    ["Duplicate scans ordered", "High", "Medium",
     "Patient anxiety", "Duplicate scan cost", 
     "Lost insight from scattered priors", "Redundant workflows", "Imaging Workflow Enhancement (2025)"],
    ["Compliance gaps (HIPAA/GDPR)", "High", "Constantly",
     "Breach anxiety", "Avg breach ~$10.93M",
     "Policy uncertainty", "No centralized audit", "Imaging Workflow Enhancement (2025)"],
    ["Inconsistent analytics & AI integration", "Medium", "Constantly",
     "Clinician disappointment", "Missed ROI, failed AI pilots",
     "No enterprise-wide learning", "Manual patchwork", "Imaging Workflow Enhancement (2025)"],
    ["High IT maintenance burden", "Medium–High", "Medium",
     "IT staff burnout", "~$300K/yr downtime",
     "Knowledge loss", "Vendor upgrades break workflows", "Imaging Workflow Enhancement (2025)"],
    ["Vendor lock-in", "High", "Medium",
     "Feeling trapped", "High switching costs",
     "Loss of data control", "Inflexible workflows", "Imaging Workflow Enhancement (2025)"],
    ["Delays in diagnosis & care", "High", "Constantly",
     "Patient stress, worse outcomes", "Longer LOS, higher costs",
     "Incomplete priors = errors", "Every workflow slowed", "Radiology Workflow Requirements (2025)"]
]

df = pd.DataFrame(pain_data, columns=[
    "Pain Point", "Severity", "Frequency", "Emotional Pain",
    "Financial Pain", "Knowledge Pain", "Process Pain", "Reference"
])

st.dataframe(df, use_container_width=True)

# --- Validation Section ---
st.markdown("## Validation of Pain Points (Engagement Data)")

validation_data = [
    ["Consolidated view of modalities (Image Post)", "18.75%", 
     "Strong validation of Data Fragmentation + Finding Priors"],
    ["Clinical data in multiple places (Video Post)", "5.17%", 
     "Weak resonance — too generic"],
    ["Data Quality Framework (Video Post)", "6.67%", 
     "Moderate validation of Knowledge/Process Pain"],
    ["Oncology compliance obligations (Document Post)", "16.67%", 
     "Strong validation of Compliance Pain"]
]

validation_df = pd.DataFrame(validation_data, columns=[
    "Post Tested", "CTR", "Validation Insight"
])

st.dataframe(validation_df, use_container_width=True)

st.markdown("""
### Insights
- **Top validated pains**: Imaging data fragmentation (18.75%) and Compliance obligations (16.67%).  
- **Medium validation**: Data quality frameworks (6.67%).  
- **Weak framing**: General "data silos" (5.17%).  

### Why This Is Viable
- Specific clinical pain (modalities, priors) resonates much stronger than broad "data silo" talk.  
- Compliance burden (esp. oncology) also shows strong engagement.  
- Validates business opportunity: hospitals want **workflow simplification + compliance protection**.  
""")
