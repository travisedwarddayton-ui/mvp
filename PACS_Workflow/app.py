# radiology_pain_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

st.set_page_config(page_title="Radiology Workflow Pain Validation", layout="wide")

st.title("Imaging IT Vendor Landscape (As-Is)")

# --- Vendor List (18 clouds, deduplicated) ---
vendors = [
    "GE Healthcare",
    "Philips Healthcare",
    "Agfa HealthCare",
    "Sectra",
    "Merative (Merge)",
    "Fujifilm (Synapse)",
    "Change Healthcare / Optum",
    "Infinitt Healthcare",
    "Novarad",
    "Hyland Healthcare",
    "Intelerad",
    "Ambra Health",
    "Life Image",
    "Siemens Healthineers (syngo.via, AI Rad Companion)",
    "Carestream Health (enterprise imaging, PACS)",
    "Visage Imaging (enterprise viewer)",
    "PaxeraHealth (vendor-neutral PACS, modular solutions)",
    "Mach7 Technologies (VNA + interoperability)"
]

# --- Layout parameters ---
cols = 4
x_spacing, y_spacing = 4.0, 2.3
fig, ax = plt.subplots(figsize=(18, 12))

vendor_positions = []
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = col * x_spacing + 2
    y = 8 - row * y_spacing
    vendor_positions.append((x, y))

    cloud = Ellipse((x, y), width=3.0, height=1.2,
                    facecolor="#ffcc99", edgecolor="#cc6600", linewidth=1.8)
    ax.add_patch(cloud)
    ax.text(x, y, v, ha="center", va="center", fontsize=9,
            color="black", weight="bold", wrap=True)

# --- Hospital Box ---
hospital_x, hospital_y = (x_spacing * (cols-1))/2 + 2, -1.5
hospital = Rectangle((hospital_x-3, hospital_y-1), 6, 2,
                     facecolor="#90EE90", edgecolor="black", linewidth=2.0)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=16, weight="bold", color="black")

# --- Arrows from vendors to hospital ---
for (x, y) in vendor_positions:
    arrow = FancyArrowPatch((x, y-0.6), (hospital_x, hospital_y+1),
                            arrowstyle="->", mutation_scale=14,
                            linewidth=1.5, color="gray", alpha=0.7,
                            connectionstyle="arc3,rad=0.15")
    ax.add_patch(arrow)

# --- Styling ---
ax.set_xlim(0, cols * x_spacing + 4)
ax.set_ylim(-3, 9)
ax.axis("off")
ax.set_facecolor("white")
ax.set_title("As-Is: Hospital Manages 18+ Imaging Vendor Connections",
             fontsize=18, weight="bold", pad=20)

st.pyplot(fig)

# --- Pain Points Table (with external links) ---
st.markdown("## Pain Points in Radiology Workflow")

pain_data = [
    ["Data fragmented across 13+ vendor silos", "High", "Constantly",
     "Frustration, burnout", "Revenue leakage, lost throughput",
     "No unified patient view", "Constant app toggling",
     "[Source](https://www.intelerad.com/en/2024/07/02/reducing-bottlenecks-in-radiology-workflows/)"],

    ["No universal interoperability layer", "High", "Constantly",
     "Clinician stress", "High IT integration cost",
     "Limited knowledge transfer", "Manual routing RIS/PACS/EHR",
     "[Source](https://www.marketsandmarkets.com/Market-Reports/enterprise-imaging-it-market-259462660.html)"],

    ["Radiologists waste time finding priors", "Medium–High", "Constantly",
     "Fatigue, morale loss", "Lost billable reads", 
     "Cognitive overload", "Slower turnaround",
     "[Source](https://axisimagingnews.com/radiology-products/radiology-software/pacs/pacs-per-use)"],

    ["Duplicate scans ordered", "High", "Medium",
     "Patient anxiety", "Duplicate scan cost", 
     "Lost insight from scattered priors", "Redundant workflows",
     "[Source](https://radiologybusiness.com/topics/artificial-intelligence/radiology-artificial-intelligence-roi-calculator-demonstrates-substantial-benefits-5-year-mark)"],

    ["Compliance gaps (HIPAA/GDPR)", "High", "Constantly",
     "Breach anxiety", "Avg breach ~$10.93M",
     "Policy uncertainty", "No centralized audit",
     "[Source](https://www.ibm.com/reports/data-breach)"],

    ["Inconsistent analytics & AI integration", "Medium", "Constantly",
     "Clinician disappointment", "Missed ROI, failed AI pilots",
     "No enterprise-wide learning", "Manual patchwork",
     "[Source](https://radiologybusiness.com/topics/artificial-intelligence/radiology-artificial-intelligence-roi-calculator-demonstrates-substantial-benefits-5-year-mark)"],

    ["High IT maintenance burden", "Medium–High", "Medium",
     "IT staff burnout", "~$300K/yr downtime",
     "Knowledge loss", "Vendor upgrades break workflows",
     "[Source](https://www.glassbeam.com/how-disruption-costs-impact-imaging-departments/)"],

    ["Vendor lock-in", "High", "Medium",
     "Feeling trapped", "High switching costs",
     "Loss of data control", "Inflexible workflows",
     "[Source](https://dondennison.com/2016/05/09/vna-and-enterprise-viewer-projects-roi/)"],

    ["Delays in diagnosis & care", "High", "Constantly",
     "Patient stress, worse outcomes", "Longer LOS, higher costs",
     "Incomplete priors = errors", "Every workflow slowed",
     "[Source](https://axisimagingnews.com/radiology-products/radiology-software/pacs/pacs-per-use)"]
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
