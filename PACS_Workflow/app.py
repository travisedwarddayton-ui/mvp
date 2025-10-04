# app_current_state_modalities_corrected.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.lines as mlines

st.set_page_config(page_title="Radiology Data Pain - Current State (Corrected Labels)", layout="wide")

st.title("Current State: Radiology Data Scattered Across Vendor Clouds and Modalities")

# Vendors with corrected modality/role labels
vendors_modalities = [
    ("GE Healthcare", "CT / Cardiac"),
    ("Philips Healthcare", "MRI / Neuro"),
    ("Agfa HealthCare", "X-Ray / General"),
    ("Sectra", "Orthopedic / MSK"),
    ("Merative (Merge)", "Mammography / Oncology"),
    ("Fujifilm (Synapse)", "Ultrasound"),
    ("Change Healthcare / Optum", "PET / Oncology"),
    ("Hyland Healthcare", "Enterprise Archive"),
    ("Intelerad", "Cloud PACS / Mixed"),
    ("Ambra Health", "Image Sharing / VNA"),
    ("Life Image", "Interoperability Network"),
    ("Infinitt Healthcare", "Regional PACS"),
    ("Novarad", "Community / Small Clinics"),
]

# Grid layout
cols = 4
positions = []
for i, (vendor, modality) in enumerate(vendors_modalities):
    x = (i % cols) * 0.35
    y = 1 - (i // cols) * 0.25
    positions.append((x, y))

fig, ax = plt.subplots(figsize=(15, 10))

# Draw clouds with archives and modality/role labels
for (x, y), (vendor, modality) in zip(positions, vendors_modalities):
    # Cloud
    cloud = Ellipse((x, y), width=0.3, height=0.15, facecolor="#cce5ff", edgecolor="blue", alpha=0.7)
    ax.add_patch(cloud)
    ax.text(x, y+0.1, vendor, ha="center", va="bottom", fontsize=9, color="blue", weight="bold")

    # Archive inside cloud
    archive = Rectangle((x-0.06, y-0.025), 0.12, 0.05, facecolor="#FFD700", edgecolor="black")
    ax.add_patch(archive)
    ax.text(x, y, "Archive", ha="center", va="center", fontsize=8, color="black")

    # Modality / role under archive
    ax.text(x, y-0.07, modality, ha="center", va="top", fontsize=8, color="darkred", style="italic")

# Draw hospital at bottom
hospital_x, hospital_y = 0.5, -0.1
hospital = Rectangle((hospital_x-0.2, hospital_y-0.05), 0.4, 0.1, facecolor="#90EE90", edgecolor="black")
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center", fontsize=12, weight="bold", color="black")

# Connect clouds to hospital
for (x, y) in positions:
    line = mlines.Line2D([x, hospital_x], [y-0.1, hospital_y+0.05], color="gray", linestyle="--", linewidth=1.0)
    ax.add_line(line)

ax.set_xlim(-0.2, 1.3)
ax.set_ylim(-0.2, 1.1)
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### Data Pain Amplified
- Each **vendor cloud** has its own **archive silo**.  
- Some are **modality-specific** (CT, MRI, Mammo, PET, Ultrasound).  
- Others are **workflow/network players** like Ambra (*Image Sharing / VNA*) and Life Image (*Interoperability Network*).  
- The hospital must connect to **all of them separately** to find priors.  
- This causes delays, duplicate scans, wasted cost, and compliance headaches.  
""")
