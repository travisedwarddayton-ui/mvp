import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

# Vendors
vendors = [
    "GE Healthcare", "Philips Healthcare", "Agfa HealthCare", "Sectra",
    "Merative (Merge)", "Fujifilm (Synapse)", "Change Healthcare / Optum",
    "Infinitt Healthcare", "Novarad", "Hyland Healthcare", "Intelerad",
    "Ambra Health", "Life Image"
]

cols = 4
x_spacing, y_spacing = 3.5, 2.2
fig, ax = plt.subplots(figsize=(16, 10))

vendor_positions = []
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = col * x_spacing + 2
    y = 6 - row * y_spacing
    vendor_positions.append((x, y))
    
    cloud = Ellipse((x, y), width=2.5, height=1.0,
                    facecolor="#d9ecff", edgecolor="#004080", linewidth=1.8)
    ax.add_patch(cloud)
    ax.text(x, y, v, ha="center", va="center", fontsize=10, color="#00264d", weight="bold")

# Hospital
hospital_x, hospital_y = (x_spacing * (cols-1))/2 + 2, -1.0
hospital = Rectangle((hospital_x-2.5, hospital_y-0.8), 5, 1.6,
                     facecolor="#90EE90", edgecolor="black", linewidth=2.0)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=14, weight="bold", color="black")

# Arrows
for (x, y) in vendor_positions:
    arrow = FancyArrowPatch((x, y-0.6), (hospital_x, hospital_y+0.8),
                            arrowstyle="->", mutation_scale=14,
                            linewidth=1.5, color="gray", alpha=0.7,
                            connectionstyle="arc3,rad=0.15")
    ax.add_patch(arrow)

# Styling
ax.set_xlim(0, cols * x_spacing + 4)
ax.set_ylim(-2, 7)
ax.axis("off")
ax.set_facecolor("white")
ax.set_title("As-Is: Hospital Manages 13+ Vendor Connections", fontsize=16, weight="bold", pad=20)

plt.show()


# --- Pain Points Table with External Links ---
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

# Render as markdown-enabled table
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
