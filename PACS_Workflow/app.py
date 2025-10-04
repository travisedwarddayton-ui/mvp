# app_current_state_refined.py
import io
import random
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle
import matplotlib.lines as mlines
import pandas as pd

st.set_page_config(page_title="Radiology Current State — Multi-Vendor Cloud Silos", layout="wide")

st.title("Current State: Radiology Data Scattered Across Many Vendor Clouds")
st.caption("Each vendor has its own cloud archive; priors are fragmented by vendor and often by modality. "
           "This illustrates why radiologists must know **which** cloud to search.")

# ----- Vendor data (single-sentence description + modality tag) -----
vendors = [
    {
        "vendor": "GE Healthcare",
        "tag": "CT / Cardiac",
        "desc": "Provides enterprise PACS and imaging cloud solutions, pushing CT and Cardiac datasets into its ecosystem."
    },
    {
        "vendor": "Philips Healthcare",
        "tag": "MRI / Neuro",
        "desc": "Offers HealthSuite Imaging cloud and IntelliSpace PACS, pushing MRI and Neuro imaging data."
    },
    {
        "vendor": "Agfa HealthCare",
        "tag": "X-Ray / General",
        "desc": "Runs Enterprise Imaging and RUBEE orchestration, handling X-Ray and General Radiology studies."
    },
    {
        "vendor": "Sectra",
        "tag": "Ortho / MSK",
        "desc": "Delivers cloud PACS and enterprise platforms, managing Orthopedic and Musculoskeletal imaging workflows."
    },
    {
        "vendor": "Merative (Merge)",
        "tag": "Mammo / Oncology",
        "desc": "Provides Merge PACS and VNA, focused on Mammography and Oncology imaging plus structured reports."
    },
    {
        "vendor": "Fujifilm (Synapse)",
        "tag": "Ultrasound",
        "desc": "Offers Synapse PACS Cloud, pushing Ultrasound and General Imaging data."
    },
    {
        "vendor": "Change Healthcare / Optum",
        "tag": "PET / Oncology",
        "desc": "Operates cloud imaging and workflow solutions, handling PET and Nuclear Medicine Oncology datasets."
    },
    {
        "vendor": "Hyland Healthcare",
        "tag": "All / VNA",
        "desc": "Supplies enterprise archive and content management, aggregating multimodality datasets into a central VNA."
    },
    {
        "vendor": "Intelerad",
        "tag": "Mixed",
        "desc": "Provides cloud PACS and enterprise workflow, managing mixed radiology modalities across enterprise sites."
    },
    {
        "vendor": "Ambra Health",
        "tag": "Image Sharing / VNA",
        "desc": "Specializes in image exchange and cloud VNA, enabling sharing of DICOM and non-DICOM studies."
    },
    {
        "vendor": "Life Image",
        "tag": "Interoperability Network",
        "desc": "Runs a medical image exchange network, pushing interoperability data and cross-hospital study transfers."
    },
    {
        "vendor": "Infinitt Healthcare",
        "tag": "General / Regional",
        "desc": "Offers regional PACS, handling general diagnostic imaging and specialized radiology data."
    },
    {
        "vendor": "Novarad",
        "tag": "Community / General",
        "desc": "Provides PACS for community and mid-size hospitals, pushing local radiology imaging datasets."
    },
]

# ----- Controls -----
colA, colB, colC, colD = st.columns([1.3, 1, 1, 1])
with colA:
    show_studies = st.checkbox("Show sample studies inside archives", value=True)
with colB:
    studies_per_vendor = st.slider("Studies per vendor (visual)", min_value=2, max_value=8, value=4, step=1)
with colC:
    show_legend = st.checkbox("Show legend", value=True)
with colD:
    highlight = st.selectbox("Highlight a vendor", ["(none)"] + [v["vendor"] for v in vendors])

# ----- Layout math (grid of clouds) -----
cols = 4
cloud_w, cloud_h = 0.28, 0.15
x_spacing, y_spacing = 0.35, 0.23

positions = []
for i in range(len(vendors)):
    x = (i % cols) * x_spacing + 0.08       # left to right
    y = 1.02 - (i // cols) * y_spacing      # top to bottom
    positions.append((x, y))

# ----- Draw diagram -----
fig, ax = plt.subplots(figsize=(15, 10))

# Draw each vendor cloud with a labeled archive + optional studies
for (x, y), v in zip(positions, vendors):
    # Cloud (blue)
    edge_color = "red" if v["vendor"] == highlight else "blue"
    lw = 2.5 if v["vendor"] == highlight else 1.2
    cloud = Ellipse((x, y), width=cloud_w, height=cloud_h,
                    facecolor="#cfe8ff", edgecolor=edge_color, linewidth=lw, alpha=0.9)
    ax.add_patch(cloud)
    ax.text(x, y + (cloud_h/2) + 0.03, v["vendor"], ha="center", va="bottom",
            fontsize=9, color="navy", weight="bold")

    # Archive (yellow) inside cloud
    arch_w, arch_h = 0.12, 0.055
    arch_x, arch_y = (x - arch_w/2), (y - arch_h/2 + 0.002)
    archive = Rectangle((arch_x, arch_y), arch_w, arch_h, facecolor="#FFD700", edgecolor="black", linewidth=1.2)
    ax.add_patch(archive)
    ax.text(x, y, "Archive", ha="center", va="center", fontsize=8.5, color="black")

    # Modality/role tag under archive
    ax.text(x, y - (cloud_h/2) + 0.01, v["tag"], ha="center", va="top", fontsize=8, color="#8B0000", style="italic")

    # Optional “studies” dots inside archive
    if show_studies:
        random.seed(hash(v["vendor"]) & 0xFFFFFFFF)
        for _ in range(studies_per_vendor):
            # random position within the archive rectangle margins
            px = arch_x + 0.01 + random.random() * (arch_w - 0.02)
            py = arch_y + 0.01 + random.random() * (arch_h - 0.02)
            dot = Circle((px, py), radius=0.0065, facecolor="#F5A623", edgecolor="darkorange", linewidth=0.6)
            ax.add_patch(dot)

# Hospital (green block) at bottom-center
hospital_x, hospital_y = 0.52, -0.05
hospital = Rectangle((hospital_x - 0.22, hospital_y - 0.05), 0.44, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=13, weight="bold", color="black")

# Connect each cloud to the Hospital
for (x, y) in positions:
    line = mlines.Line2D([x, hospital_x], [y - (cloud_h/2), hospital_y + 0.05],
                         color="gray", linestyle="--", linewidth=1.1, alpha=0.9)
    ax.add_line(line)

# Legend (optional)
if show_legend:
    ax.text(0.03, 1.07, "Legend:", fontsize=10, weight="bold", transform=ax.transAxes)
    ax.add_patch(Ellipse((0.11, 1.07), 0.03, 0.02, transform=ax.transAxes,
                         facecolor="#cfe8ff", edgecolor="blue", linewidth=1))
    ax.text(0.14, 1.07, "Vendor Cloud", fontsize=9, transform=ax.transAxes, va="center")
    ax.add_patch(Rectangle((0.32, 1.065), 0.03, 0.02, transform=ax.transAxes,
                           facecolor="#FFD700", edgecolor="black", linewidth=1))
    ax.text(0.36, 1.07, "Archive", fontsize=9, transform=ax.transAxes, va="center")
    circ = Circle((0.51, 1.07), 0.01, transform=ax.transAxes,
                  facecolor="#F5A623", edgecolor="darkorange", linewidth=0.8)
    ax.add_patch(circ)
    ax.text(0.54, 1.07, "Studies (trapped)", fontsize=9, transform=ax.transAxes, va="center")
    ax.plot([0.72, 0.75], [1.07, 1.07], transform=ax.transAxes, color="gray", linestyle="--", linewidth=1.2)
    ax.text(0.76, 1.07, "Connection to Hospital", fontsize=9, transform=ax.transAxes, va="center")

# Frame
ax.set_xlim(-0.05, 1.45)
ax.set_ylim(-0.2, 1.15)
ax.axis("off")

st.pyplot(fig)

# ----- Download diagram button -----
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
st.download_button("Download diagram (PNG)", data=buf.getvalue(), file_name="current_state_vendor_clouds.png", mime="image/png")

st.markdown("### Why this hurts care")
st.markdown(
"""
- Each **vendor cloud** is a separate **archive silo**; patient priors can be anywhere.  
- Radiologists must **guess the vendor** and **modalities** to locate prior studies.  
- This fragmentation causes **delays**, **duplicate scans**, **lost throughput**, and **compliance complexity**.  
"""
)

# ----- Descriptions table below the illustration -----
st.markdown("### Vendor roles and what they push (single statement + modality tag)")
df = pd.DataFrame([
    {"Vendor": v["vendor"], "Modality Tag": v["tag"], "Single-Statement Description": v["desc"]}
    for v in vendors
])
st.dataframe(df, use_container_width=True)
