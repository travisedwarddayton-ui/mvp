# app_vendor_grid_with_painpoints_clean.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

st.set_page_config(page_title="Radiology Vendor Grid with Pain Points", layout="wide")

st.title("Radiology Vendor Clouds ↔ Hospital (As-Is)")

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

# Plot vendor clouds
for i, v in enumerate(vendors):
    col = i % cols
    row = i // cols
    x = 0.2 + col * x_spacing
    y = 1.0 - row * y_spacing

    cloud = Ellipse((x, y), width=0.22, height=0.10,
                    facecolor="#cfe8ff", edgecolor="blue", linewidth=1.2)
    ax.add_patch(cloud)
    ax.text(x, y, v, ha="center", va="center", fontsize=9, color="navy", weight="bold")

# Hospital
hospital_x, hospital_y = 0.5, -0.1
hospital = Rectangle((hospital_x-0.2, hospital_y-0.05), 0.4, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(hospital_x, hospital_y, "Hospital", ha="center", va="center",
        fontsize=13, weight="bold", color="black")

# Bi-directional arrow
arrow = FancyArrowPatch((0.5, 0.25), (0.5, -0.05),
                        arrowstyle="<->", mutation_scale=20,
                        linewidth=2, color="black")
ax.add_patch(arrow)
ax.text(0.52, 0.1, "Data Movement", fontsize=10, rotation=90, va="center")

# Adjust canvas
ax.set_xlim(0, 1.1)
ax.set_ylim(-0.2, 1.2)
ax.axis("off")

st.pyplot(fig)

# ---- Pain points BELOW diagram (outside figure) ----
st.markdown("## Pain Points in Current State")
st.markdown("""
- Data fragmented across 13+ vendor silos  
- No universal interoperability layer  
- Radiologists waste time finding priors  
- Duplicate scans increase cost & risk  
- HIPAA/GDPR compliance harder to enforce  
- Inconsistent analytics & AI integration  
- High IT maintenance & upgrade burden  
- Vendor lock-in makes switching costly  
- Delays in diagnosis and patient care  
""")
