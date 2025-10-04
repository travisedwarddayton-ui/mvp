# app_state_transition.py
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle
import matplotlib.lines as mlines

st.set_page_config(page_title="Radiology Cloud Fragmentation: Current vs Future", layout="wide")

st.title("Radiology Cloud Fragmentation")
st.caption("Showing how vendor silos create workflow pain, and how an interoperability layer simplifies access.")

# Vendor categories
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

tab1, tab2 = st.tabs(["📉 Current State", "🚀 Future State"])

# ------------------ CURRENT STATE ------------------
with tab1:
    st.subheader("Current State: Fragmented Vendor Clouds")
    fig, ax = plt.subplots(figsize=(15, 9))

    # Arrange categories in columns
    x_positions = [0.2, 0.5, 0.8]
    category_titles = list(vendors.keys())

    for col, (cat, vendor_list) in enumerate(vendors.items()):
        for row, (vendor, tag) in enumerate(vendor_list):
            x = x_positions[col]
            y = 1 - (row * 0.12)

            # Blue cloud
            cloud = Ellipse((x, y), width=0.25, height=0.1, facecolor="#cfe8ff", edgecolor="blue", linewidth=1)
            ax.add_patch(cloud)
            ax.text(x, y + 0.07, vendor, ha="center", va="bottom", fontsize=9, color="navy", weight="bold")
            
            # Archive (yellow box)
            archive = Rectangle((x-0.05, y-0.02), 0.1, 0.04, facecolor="#FFD700", edgecolor="black", linewidth=1)
            ax.add_patch(archive)
            ax.text(x, y, "Archive", ha="center", va="center", fontsize=7, color="black")
            
            # Tag
            ax.text(x, y - 0.07, tag, ha="center", va="top", fontsize=7, color="#8B0000", style="italic")

            # Line to hospital
            ax.add_line(mlines.Line2D([x, 0.5], [y-0.05, -0.05], color="gray", linestyle="--", linewidth=1))

        # Category label
        ax.text(x, 1.05, cat, ha="center", va="bottom", fontsize=11, weight="bold", color="black")

    # Hospital at bottom
    hospital = Rectangle((0.35, -0.1), 0.3, 0.08, facecolor="#90EE90", edgecolor="black", linewidth=1.5)
    ax.add_patch(hospital)
    ax.text(0.5, -0.06, "Hospital", ha="center", va="center", fontsize=12, weight="bold")

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.2, 1.2)
    ax.axis("off")
    st.pyplot(fig)

    st.markdown("""
    ### Problems in the Current State
    - Hospital must connect separately to **13+ different vendor clouds**.  
    - Patient priors are scattered by **vendor and modality**.  
    - Radiologists waste time guessing where images live.  
    - Leads to **delays, duplicate scans, inefficiency, and compliance risk**.  
    """)

# ------------------ FUTURE STATE ------------------
with tab2:
    st.subheader("Future State: Unified Interoperability Layer")
    fig, ax = plt.subplots(figsize=(15, 9))

    # Vendor clouds (same layout but connect to Interop layer instead of hospital)
    x_positions = [0.2, 0.5, 0.8]
    category_titles = list(vendors.keys())

    for col, (cat, vendor_list) in enumerate(vendors.items()):
        for row, (vendor, tag) in enumerate(vendor_list):
            x = x_positions[col]
            y = 1 - (row * 0.12)

            # Blue cloud
            cloud = Ellipse((x, y), width=0.25, height=0.1, facecolor="#cfe8ff", edgecolor="blue", linewidth=1)
            ax.add_patch(cloud)
            ax.text(x, y + 0.07, vendor, ha="center", va="bottom", fontsize=9, color="navy", weight="bold")

            # Archive
            archive = Rectangle((x-0.05, y-0.02), 0.1, 0.04, facecolor="#FFD700", edgecolor="black", linewidth=1)
            ax.add_patch(archive)
            ax.text(x, y, "Archive", ha="center", va="center", fontsize=7, color="black")

            # Tag
            ax.text(x, y - 0.07, tag, ha="center", va="top", fontsize=7, color="#8B0000", style="italic")

            # Line to Interop Layer
            ax.add_line(mlines.Line2D([x, 0.5], [y-0.05, 0.15], color="gray", linestyle="--", linewidth=1))

        # Category title
        ax.text(x, 1.05, cat, ha="center", va="bottom", fontsize=11, weight="bold", color="black")

    # Interoperability Layer
    interop = Rectangle((0.25, 0.1), 0.5, 0.08, facecolor="#FFA07A", edgecolor="black", linewidth=1.5)
    ax.add_patch(interop)
    ax.text(0.5, 0.14, "Neutral Interoperability Layer", ha="center", va="center", fontsize=11, weight="bold")

    # Hospital at bottom
    hospital = Rectangle((0.35, -0.1), 0.3, 0.08, facecolor="#90EE90", edgecolor="black", linewidth=1.5)
    ax.add_patch(hospital)
    ax.text(0.5, -0.06, "Hospital", ha="center", va="center", fontsize=12, weight="bold")

    # Single connection from Interop → Hospital
    ax.add_line(mlines.Line2D([0.5, 0.5], [0.1, -0.02], color="black", linewidth=2))

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.2, 1.2)
    ax.axis("off")
    st.pyplot(fig)

    st.markdown("""
    ### Benefits of the Future State
    - All vendor silos connect to a **single interoperability layer**.  
    - Radiologists query **one worklist** for all modalities and vendors.  
    - Priors are auto-fetched without knowing where they live.  
    - Hospital IT simplifies integrations from **13+ feeds → 1 feed**.  
    - Unlocks **AI, analytics, compliance, and ROI** with unified access.  
    """)
