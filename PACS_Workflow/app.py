# app_vendor_grid_single_arrow.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrow

st.set_page_config(page_title="Radiology Vendor Grid with Hospital Flow", layout="wide")

st.title("Vendor Cloud Landscape with Hospital Data Flow")

# Vendor list (13 vendors)
vendors = [
    "GE Healthcare", "Philips Healthcare", "Agfa HealthCare", "Sectra",
    "Merative (Merge)", "Fujifilm (Synapse)", "Change Healthcare / Optum",
    "Infinitt Healthcare", "Novarad", "Hyland Healthcare", "Intelerad",
    "Ambra Health", "Life Image"
]

# Grid layout parameters
cols = 4
rows = (len(vendors) + cols - 1) // cols  # round up
x_spacing, y_spacing = 0.25, 0.18

fig, ax = plt.subplots(figsize=(15, 10))

# Plot vendors in even grid
positions = []
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = 0.2 + col * x_spacing
    y = 1.0 - row * y_spacing
    positions.append((x, y))

    # Vendor cloud
    cloud = Ellipse((x, y), width=0.20, height=0.10,
                    facecolor="#cfe8ff", edgecolor="blue", linewidth=1.2)
    ax.add_patch(cloud)
    ax.text(x, y, v, ha="center", va="center", fontsize=9, color="navy", weight="bold")

# Hospital at bottom center
hospital_x, hospital_y = 0.5, -0.05
hospital = Rectangle((hospital_x-0.2, hospital_y-0.05), 0.4, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center", fontsize=12, weight="bold")

# Bi-directional arrow from vendor grid (center) to hospital
arrow = FancyArrow(0.5, 0.2, 0, -0.20, width=0.01, head_width=0.05,
                   head_length=0.03, length_includes_head=True, color="black")
ax.add_patch(arrow)
arrow2 = FancyArrow(0.5, -0.05, 0, 0.20, width=0.01, head_width=0.05,
                    head_length=0.03, length_includes_head=True, color="black")
ax.add_patch(arrow2)
ax.text(0.52, 0.1, "Data Movement", fontsize=10, color="black", rotation=90)

ax.set_xlim(0, 1.1)
ax.set_ylim(-0.2, 1.2)
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### Key Point
- Hospital interacts with **all vendor clouds**.  
- Instead of dozens of point-to-point feeds, think of this as **one consolidated data flow**.  
- The bi-directional arrow shows that imaging data moves **to and from the hospital** across vendors.  
""")
