# app_current_state_refined_centered.py
import io
import random
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle
import matplotlib.lines as mlines
import pandas as pd

st.set_page_config(page_title="Radiology Current State — Multi-Vendor Cloud Silos", layout="wide")

st.title("Current State: Radiology Data Scattered Across Many Vendor Clouds")

st.caption("Each vendor has its own cloud archive; priors are fragmented by vendor and modality. "
           "Radiologists must guess where to look, wasting time and risking duplicate scans.")

# ----- Vendor data -----
vendors = [
    ("GE Healthcare", "CT / Cardiac",
     "Provides enterprise PACS and imaging cloud solutions, pushing CT and Cardiac datasets."),
    ("Philips Healthcare", "MRI / Neuro",
     "Offers HealthSuite Imaging cloud and IntelliSpace PACS, pushing MRI and Neuro imaging data."),
    ("Agfa HealthCare", "X-Ray / General",
     "Runs Enterprise Imaging and RUBEE orchestration, handling X-Ray and General Radiology studies."),
    ("Sectra", "Ortho / MSK",
     "Delivers cloud PACS and enterprise platforms, managing Orthopedic and Musculoskeletal imaging."),
    ("Merative (Merge)", "Mammo / Oncology",
     "Provides Merge PACS and VNA, focused on Mammography and Oncology imaging."),
    ("Fujifilm (Synapse)", "Ultrasound",
     "Offers Synapse PACS Cloud, pushing Ultrasound and General Imaging data."),
    ("Change Healthcare / Optum", "PET / Oncology",
     "Operates cloud imaging and workflow solutions, handling PET and Nuclear Medicine Oncology datasets."),
    ("Hyland Healthcare", "All / VNA",
     "Supplies enterprise archive and content management, aggregating multimodality datasets into a VNA."),
    ("Intelerad", "Mixed",
     "Provides cloud PACS and enterprise workflow, managing mixed radiology modalities."),
    ("Ambra Health", "Image Sharing / VNA",
     "Specializes in image exchange and cloud VNA, enabling sharing of DICOM and non-DICOM studies."),
    ("Life Image", "Interoperability Network",
     "Runs a medical image exchange network, enabling cross-hospital study transfers."),
    ("Infinitt Healthcare", "General / Regional",
     "Offers regional PACS, handling general diagnostic imaging and specialized radiology data."),
    ("Novarad", "Community / General",
     "Provides PACS for community and mid-size hospitals, pushing local radiology imaging datasets."),
]

# Controls
show_studies = st.checkbox("Show sample studies inside archives", value=True)
studies_per_vendor = st.slider("Studies per vendor", min_value=2, max_value=6, value=3, step=1)

# Layout grid: center clouds in columns
cols = 4
cloud_w, cloud_h = 0.25, 0.14
x_spacing, y_spacing = 0.33, 0.22

positions = []
n = len(vendors)
for i in range(n):
    col = i % cols
    row = i // cols
    # center across full width
    x = (col * x_spacing) + 0.2
    y = 1.0 - (row * y_spacing)
    positions.append((x, y))

fig, ax = plt.subplots(figsize=(14, 9))

# Draw vendors
for (x, y), (vendor, tag, desc) in zip(positions, vendors):
    # Blue cloud
    cloud = Ellipse((x, y), width=cloud_w, height=cloud_h,
                    facecolor="#cfe8ff", edgecolor="blue", linewidth=1.2, alpha=0.9)
    ax.add_patch(cloud)
    ax.text(x, y + (cloud_h/2) + 0.025, vendor, ha="center", va="bottom",
            fontsize=9, color="navy", weight="bold")

    # Archive (yellow)
    arch_w, arch_h = 0.1, 0.045
    arch_x, arch_y = x - arch_w/2, y - arch_h/2
    archive = Rectangle((arch_x, arch_y), arch_w, arch_h,
                        facecolor="#FFD700", edgecolor="black", linewidth=1.0)
    ax.add_patch(archive)
    ax.text(x, y, "Archive", ha="center", va="center", fontsize=8, color="black")

    # Modality tag
    ax.text(x, y - (cloud_h/2) - 0.01, tag, ha="center", va="top",
            fontsize=8, color="#8B0000", style="italic")

    # Studies
    if show_studies:
        random.seed(hash(vendor) & 0xFFFFFFFF)
        for _ in range(studies_per_vendor):
            px = arch_x + 0.01 + random.random() * (arch_w - 0.02)
            py = arch_y + 0.01 + random.random() * (arch_h - 0.02)
            dot = Circle((px, py), radius=0.0055, facecolor="#F5A623", edgecolor="darkorange", linewidth=0.5)
            ax.add_patch(dot)

# Hospital at bottom
hospital_x, hospital_y = 0.5, -0.08
hospital = Rectangle((hospital_x - 0.18, hospital_y - 0.05), 0.36, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=12, weight="bold", color="black")

# Connections
for (x, y) in positions:
    line = mlines.Line2D([x, hospital_x], [y - (cloud_h/2), hospital_y + 0.05],
                         color="gray", linestyle="--", linewidth=1.0, alpha=0.8)
    ax.add_line(line)

# Center frame
ax.set_xlim(0, 1.2)
ax.set_ylim(-0.2, 1.1)
ax.axis("off")

st.pyplot(fig)

# Table of vendors
st.markdown("### Vendor roles and what they push")
df = pd.DataFrame([{"Vendor": v, "Modality Tag": t, "Single-Statement": d} for v, t, d in vendors])
st.dataframe(df, use_container_width=True)

st.markdown("""
### Why this hurts care
- Each vendor is a **silo**; priors may exist in any of them.  
- Archives are **fragmented by modality and vendor**.  
- Radiologists must check multiple systems, causing **delays, duplicates, and inefficiency**.  
""")
