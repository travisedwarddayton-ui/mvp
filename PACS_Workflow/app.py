# app_current_state_spread_v3.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle
import matplotlib.lines as mlines

st.set_page_config(page_title="Radiology Current State — Spread Layout v3", layout="wide")

st.title("Current State: Radiology Data Fragmented Across Vendor Clouds")
st.caption("Vendors are grouped by category, but each connects separately to the hospital, causing integration chaos.")

vendors = {
    "PACS / Modality Clouds": [
        ("GE Healthcare", "CT / Cardiac"),
        ("Philips Healthcare", "MRI / Neuro"),
        ("Agfa HealthCare", "X-Ray / General"),
        ("Sectra", "Ortho / MSK"),
        ("Merative (Merge)", "Mammo / Oncology"),
        ("Fujifilm (Synapse)", "Ultrasound"),
        ("Change Healthcare / Optum", "PET / Oncology"),
        ("Infinitt Healthcare", "General / Regional"),
        ("Novarad", "Community / General"),
    ],
    "Workflow / Archive Providers": [
        ("Hyland Healthcare", "All / VNA"),
        ("Intelerad", "Mixed"),
    ],
    "Exchange / Interoperability Networks": [
        ("Ambra Health", "Image Sharing / VNA"),
        ("Life Image", "Interoperability Network"),
    ],
}

fig, ax = plt.subplots(figsize=(15, 16))  # taller canvas

x_positions = [0.2, 0.55, 0.9]
y_start = 1.0
y_spacing = 0.20  # more spacing

for col, (cat, vendor_list) in enumerate(vendors.items()):
    for row, (vendor, tag) in enumerate(vendor_list):
        x = x_positions[col]
        y = y_start - (row * y_spacing)

        # Blue cloud
        cloud = Ellipse((x, y), width=0.26, height=0.12,
                        facecolor="#cfe8ff", edgecolor="blue", linewidth=1.2)
        ax.add_patch(cloud)
        ax.text(x, y + 0.085, vendor, ha="center", va="bottom", fontsize=10, color="navy", weight="bold")

        # Archive
        archive = Rectangle((x-0.05, y-0.025), 0.1, 0.05,
                            facecolor="#FFD700", edgecolor="black", linewidth=1)
        ax.add_patch(archive)
        ax.text(x, y, "Archive", ha="center", va="center", fontsize=8, color="black")

        # Modality tag
        ax.text(x, y - 0.08, tag, ha="center", va="top", fontsize=8, color="#8B0000", style="italic")

        # Connect to hospital
        ax.add_line(mlines.Line2D([x, 0.55], [y-0.06, -0.15], color="gray", linestyle="--", linewidth=1))

    # Category header
    ax.text(x, 1.12, cat, ha="center", va="bottom", fontsize=12, weight="bold")

# Hospital (lowered further down)
hospital = Rectangle((0.4, -0.20), 0.3, 0.1,
                     facecolor="#90EE90", edgecolor="black", linewidth=1.5)
ax.add_patch(hospital)
ax.text(0.55, -0.15, "Hospital", ha="center", va="center", fontsize=13, weight="bold")

ax.set_xlim(0, 1.1)
ax.set_ylim(-0.3, 1.15)  # more bottom space
ax.axis("off")

st.pyplot(fig)

st.markdown("""
### Pain Points
- Hospital must manage **13+ vendor connections**.  
- Priors are scattered across **modality- and vendor-specific silos**.  
- Radiologists waste time, IT integrations remain brittle, and compliance is harder.  
""")
