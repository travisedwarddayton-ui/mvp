# app_vendor_grid_single_flow.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

st.set_page_config(page_title="Vendor Grid with Hospital Flow", layout="wide")

st.title("Radiology Vendor Clouds ↔ Hospital Data Flow")

# Vendor list (13)
vendors = [
    "GE Healthcare", "Philips Healthcare", "Agfa HealthCare", "Sectra",
    "Merative (Merge)", "Fujifilm (Synapse)", "Change Healthcare / Optum",
    "Infinitt Healthcare", "Novarad", "Hyland Healthcare", "Intelerad",
    "Ambra Health", "Life Image"
]

# Grid layout
cols = 4
rows = (len(vendors) + cols - 1) // cols
x_spacing, y_spacing = 0.25, 0.18

fig, ax = plt.subplots(figsize=(15, 10))

# Place vendors in grid
positions = []
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = 0.2 + col * x_spacing
    y = 1.0 - row * y_spacing
    positions.append((x, y))

    # Vendor cloud
    cloud = Ellipse((x, y), width=0.22, height=0.10,
                    facecolor="#cfe8ff", edgecolor="blue", linewidth=1.2)
    ax.add_patch(cloud)
    ax.text(x, y, v, ha="center", va="center", fontsize=9, color="navy", weight="bold")

# Hospital box at bottom
hospital_x, hospital_y = 0.5, -0.1
hospital = Rectangle((hospital_x-0.2, hospital_y-0.05), 0.4, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=13, weight="bold", color="black")

# Single bi-directional arrow (grid center → hospital)
arrow = FancyArrowPatch((0.5, 0.25), (0.5, -0.05),
                        arrowstyle="<->", mutation_scale=20,
                        linewidth=2, color="black")
ax.add_patch(arrow)
ax.text(0.52, 0.1, "Data Movement", fontsize=10, rotation=90, va="center")

# Frame
ax.set_xlim(0, 1.1)
ax.set_ylim(-0.2, 1.2)
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### Key Point
- All vendors connect to the hospital, but conceptually it’s **one data flow**.  
- Imaging data moves **to and from** vendor clouds and the hospital.  
- This cleans up the picture: **no spaghetti**, just one relationship.  
""")
