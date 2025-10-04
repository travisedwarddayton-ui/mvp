# app_current_state_diagram.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle

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

# Layout positions for the clouds
positions = [
    (0.2, 0.8), (0.6, 0.8), (1.0, 0.8),
    (0.2, 0.4), (0.6, 0.4), (1.0, 0.4),
    (0.6, 0.1)
]

fig, ax = plt.subplots(figsize=(12, 8))

# Draw each vendor cloud
for (x, y), name in zip(positions, vendors):
    cloud = Ellipse((x, y), width=0.35, height=0.2, facecolor="#cce5ff", edgecolor="blue", alpha=0.7)
    ax.add_patch(cloud)
    ax.text(x, y+0.12, name, ha="center", va="bottom", fontsize=10, color="blue")
    
    # Scatter some patient studies inside each cloud
    for i in range(4):
        cx = x + (0.1 * (i%2 - 0.5))
        cy = y + (0.05 * (i//2 - 0.5))
        circ = Circle((cx, cy), 0.02, facecolor="#f5a623", edgecolor="darkorange")
        ax.add_patch(circ)

ax.set_xlim(-0.1, 1.3)
ax.set_ylim(0, 1.1)
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### Data Pain Points
- Each **vendor cloud** is its own silo.  
- Patient studies (orange dots) are **locked inside** individual vendors.  
- Radiologists must **know which cloud** to search for priors.  
- This causes **delays, repeat scans, lost productivity, and compliance risk**.
""")
