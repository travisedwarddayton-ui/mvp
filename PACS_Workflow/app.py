# app_current_state_diagram_v2.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.lines as mlines

st.set_page_config(page_title="Radiology Data Pain - Current State", layout="wide")

st.title("Current State: Radiology Data Scattered Across Vendor Clouds")

# Vendors
vendors = [
    "GE Cloud",
    "Philips Cloud",
    "Agfa Cloud",
    "Sectra Cloud",
    "Merative Cloud",
    "Ambra Cloud",
    "Life Image Cloud"
]

# Cloud positions
positions = [
    (0.2, 0.8), (0.6, 0.8), (1.0, 0.8),
    (0.2, 0.5), (0.6, 0.5), (1.0, 0.5),
    (0.6, 0.2)
]

fig, ax = plt.subplots(figsize=(12, 8))

# Draw clouds and archives
for (x, y), name in zip(positions, vendors):
    # Cloud
    cloud = Ellipse((x, y), width=0.35, height=0.2, facecolor="#cce5ff", edgecolor="blue", alpha=0.7)
    ax.add_patch(cloud)
    ax.text(x, y+0.13, name, ha="center", va="bottom", fontsize=10, color="blue", weight="bold")

    # Yellow archive box inside each cloud
    archive = Rectangle((x-0.07, y-0.04), 0.14, 0.08, facecolor="#FFD700", edgecolor="black")
    ax.add_patch(archive)
    ax.text(x, y, "Archive", ha="center", va="center", fontsize=9, color="black")

# Draw hospital at bottom
hospital_x, hospital_y = 0.6, -0.05
hospital = Rectangle((hospital_x-0.15, hospital_y-0.05), 0.3, 0.1, facecolor="#90EE90", edgecolor="black")
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center", fontsize=12, weight="bold", color="black")

# Connect each cloud to the hospital
for (x, y) in positions:
    line = mlines.Line2D([x, hospital_x], [y-0.1, hospital_y+0.05], color="gray", linestyle="--", linewidth=1.5)
    ax.add_line(line)

ax.set_xlim(-0.1, 1.3)
ax.set_ylim(-0.2, 1.1)
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### Pain Illustrated
- Each **vendor cloud** has its **own archive** (yellow box).  
- To access patient studies, the hospital must connect separately to **each vendor cloud**.  
- Radiologists have to **know which archive** holds the prior images.  
- This creates **complexity, wasted time, and clinical risk**.
""")
