# radiology_pain_app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Radiology Workflow Pain Validation", layout="wide")

st.title("Imaging IT Vendor Landscape (As-Is)")

# --- Vendor List (instead of diagram) ---
st.markdown("""
Hospitals typically manage connections to **15–20 different imaging IT vendors**, each
operating as a siloed "cloud" with its own PACS, VNA, viewer, or exchange.  

### 🌩 Core Vendors (widely used in hospitals)
- GE Healthcare
- Philips Healthcare
- Agfa HealthCare
- Sectra
- Merative (Merge, ex-IBM)
- Fujifilm (Synapse)
- Change Healthcare / Optum
- Infinitt Healthcare
- Novarad
- Hyland Healthcare
- Intelerad
- Ambra Health
- Life Image

### 🌩 Extended Vendors (secondary but growing)
- Siemens Healthineers (syngo.via, AI Rad Companion)
- Carestream Health (enterprise imaging, PACS)
- Visage Imaging (enterprise viewer)
- PaxeraHealth (vendor-neutral PACS, modular solutions)
- Mach7 Technologies (VNA + interoperability)

---
### 📌 Key Insight
- Each of these vendors represents a **separate 'cloud' or silo**.  
- Hospitals must integrate all of them individually, which creates:
  - Fragmented data across silos  
  - Duplicate scans and inefficiencies  
  - Slower diagnosis and delayed care  
  - Compliance and interoperability risks  
  - High IT maintenance costs  
""")

# --- Pain Points Table ---
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
