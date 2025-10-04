# app_current_state_full.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.lines as mlines

st.set_page_config(page_title="Radiology Data Pain - Current State (All Vendors)", layout="wide")

st.title("Current State: Radiology Data Scattered Across Many Vendor Clouds")

# Full vendor list
vendors = [
    "GE Healthcare",
    "Philips Healthcare",
    "Agfa HealthCare",
    "Sectra",
    "Merative (Merge)",
    "Fujifilm (Synapse)",
    "Change Healthcare / Optum",
    "Hyland Healthcare",
    "Intelerad",
    "Ambra Health",
    "Life Image",
    "Infinitt Healthcare",
    "Novarad"
]

# Arrange clouds in a grid
cols = 4
positions = []
for i, v in enumerate(vendors):
    x = (i % cols) * 0.35
    y = 1 - (i // cols) * 0.25
    positions.append((x, y))

fig, ax = plt.subplots(figsize=(14, 10))

# Draw clouds with archives
for (x, y), name in zip(positions, vendors):
    cloud = Ellipse((x, y), width=0.3, height=0.15, facecolor="#cce5ff", edgecolor="blue", alpha=0.7)
    ax.add_patch(cloud)
    ax.text(x, y+0.1, name, ha="center", va="bottom", fontsize=9, color="blue", weight="bold")

    # Archive inside each cloud
    archive = Rectangle((x-0.06, y-0.03), 0.12, 0.06, facecolor="#FFD700", edgecolor="black")
    ax.add_patch(archive)
    ax.text(x, y, "Archive", ha="center", va="center", fontsize=8, color="black")

# Draw central hospital
hospital_x, hospital_y = 0.5, -0.1
hospital = Rectangle((hospital_x-0.2, hospital_y-0.05), 0.4, 0.1, facecolor="#90EE90", edgecolor="black")
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center", fontsize=12, weight="bold", color="black")

# Connect each cloud to hospital
for (x, y) in positions:
    line = mlines.Line2D([x, hospital_x], [y-0.1, hospital_y+0.05], color="gray", linestyle="--", linewidth=1.0)
    ax.add_line(line)

ax.set_xlim(-0.2, 1.3)
ax.set_ylim(-0.2, 1.1)
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### What This Shows
- Each **vendor cloud** has its own **archive silo**.  
- The **hospital** must connect separately to each vendor archive.  
- Patient studies are scattered across **GE, Philips, Agfa, Sectra, Merative, Fujifilm, Change/Optum, Hyland, Intelerad, Ambra, Life Image, Infinitt, Novarad**.  
- Radiologists must **know the vendor** to locate priors.  
- This causes **delays, repeat scans, lost productivity, and compliance risks**.  
""")
