import streamlit as st
import textwrap
from datetime import datetime
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Nursing Informatics: History & Hands-On", layout="wide")

# ----------------------------
# Helpers
# ----------------------------

def bullet(items):
    for i in items:
        st.markdown(f"- {i}")

def section_header(title, sub=None, icon="🧠"):
    st.markdown(f"## {icon} {title}")
    if sub:
        st.caption(sub)

def quiz_mc(question, options, correct_idx, key):
    st.markdown(f"**{question}**")
    choice = st.radio("Choose one:", options, key=key, label_visibility="collapsed")
    if st.button("Check", key=f"check_{key}") and choice:
        if options.index(choice) == correct_idx:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Not quite. Correct answer: **{options[correct_idx]}**")

def tag_pills(tags):
    st.markdown(
        " ".join([f"<span style='padding:6px 10px;border-radius:999px;background:#f1f5f9;margin-right:6px;font-size:0.85rem'>{t}</span>"
                  for t in tags]),
        unsafe_allow_html=True
    )

def make_timeline_plot(events):
    years = [e[0] for e in events]
    labels = [e[1] for e in events]
    fig, ax = plt.subplots(figsize=(10, 2.8))
    ax.hlines(1, min(years)-1, max(years)+1)
    ax.set_ylim(0.8, 1.2)
    ax.set_yticks([])
    ax.set_xticks(sorted(years))
    ax.set_xlabel("Year")
    for x, label in events:
        ax.plot(x, 1, "o")
        ax.text(x, 1.06, str(x), ha="center", va="bottom", fontsize=9)
        ax.text(x, 0.94, label, ha="center", va="top", rotation=90, fontsize=8)
    fig.tight_layout()
    return fig

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("Revision Hub")
st.sidebar.markdown("**Nursing Informatics – History & Practice**")
st.sidebar.info("Tip: Use this app like a *revision class*: skim visuals, then do exercises. Export your personal notes at the end.")

mode = st.sidebar.radio("Jump to:", [
    "Overview",
    "Timeline Explorer",
    "Key Terms (Flashcards)",
    "Hardware & Software Basics",
    "Open Source vs Proprietary",
    "Data → Information → Knowledge → Wisdom (DIKW)",
    "EHRs, Usability & Patient Portals",
    "Wearables & mHealth",
    "Nursing Big Data Workgroups",
    "Hands-On Exercises",
    "Build My Handout (Export)"
])

# ----------------------------
# Overview (Refined Section)
# ----------------------------
if mode == "Overview":
    section_header("Nursing Informatics: Why It Matters", "From early computers to mobile health and AI", "📘")

    st.write("""
    Nursing Informatics (NI) is not just about computers — it’s about **improving how nurses think, document, and care**
    using information and technology. Every nurse today, whether in a rural clinic or teaching hospital, interacts with data daily.

    Learning NI helps you:
    - **Make better decisions**: Turn raw observations into insights that guide patient care.
    - **Save time and reduce errors**: Learn how good data entry, standardized terms, and usability design make care safer.
    - **Improve communication**: Use digital tools to connect with other healthcare workers, labs, and patients faster.
    - **Stay relevant**: Modern hospitals expect nurses to work with EHRs, mobile apps, and AI-assisted devices.
    - **Advance your career**: Informatics is now a recognized nursing specialty with global demand for data-savvy nurses.
    - **Strengthen local healthcare**: Nigerian nurses using open-source and low-cost digital tools can bridge resource gaps and lead innovation.
    """)

    col1, col2 = st.columns([1,1])
    with col1:
        section_header("Learning Objectives", icon="🎯")
        bullet([
            "Recall major time periods and milestones in NI.",
            "Differentiate system software, utilities, and applications.",
            "Explain DIKW and where nursing tasks fit in the data pipeline.",
            "Recognize EHR usability principles and patient portal roles.",
            "Identify use-cases for wearables, mHealth, and open-source tools.",
            "Understand how informatics supports safer, smarter nursing."
        ])
    with col2:
        section_header("Why It Matters in Nigeria", icon="🌍")
        bullet([
            "Healthcare facilities are moving toward digital record keeping.",
            "Mobile-based mHealth tools are already used in community care.",
            "Low-cost open-source systems (like OpenMRS) need nurse leadership.",
            "AI and data skills are becoming essential for nursing research and management.",
            "Nurses with informatics knowledge can improve both patient safety and documentation quality."
        ])
    tag_pills(["HIT", "EHR", "mHealth", "Open Source", "DIKW", "Usability", "Career Growth", "Patient Safety"])

# ----------------------------
# Timeline
# ----------------------------
if mode == "Timeline Explorer":
    section_header("Historical Milestones", "Key events that shaped NI", "🕰️")
    timeline = [
        (1960, "Hospitals start computerization (admin, ICU monitors)"),
        (1970, "Early teaching systems (PLATO), standardization efforts"),
        (1981, "First NI working groups & conferences"),
        (1985, "ANA Council on Computer Applications in Nursing"),
        (1990, "HIPAA era; databases & client-server"),
        (1992, "NI recognized as a nursing specialty (ANA)"),
        (1997, "NIDSEC criteria for nursing systems"),
        (2004, "ONC established; push for interoperable EHRs"),
        (2009, "HITECH Act; 'Meaningful Use' incentives"),
        (2017, "MIPS value-based payment impacts workflows"),
    ]
    fig = make_timeline_plot(timeline)
    st.pyplot(fig)
    st.caption("Explore how regulation and technology pushed nursing data standards and EHR adoption.")

# ----------------------------
# Key Terms (Flashcards)
# ----------------------------
if mode == "Key Terms (Flashcards)":
    section_header("Tap to Reveal – Flashcards", icon="🪪")
    terms = {
        "HIT (Health Information Technology)": "Tech that captures, processes, and generates healthcare information across care settings.",
        "EHR (Electronic Health Record)": "Longitudinal, digital patient record integrated across providers; supports decision making.",
        "Usability": "Effectiveness, efficiency, and satisfaction with which specified users achieve goals in a context.",
        "Patient Portal": "Secure online access point for patients to view results, meds, visits, and communicate with providers.",
        "DIKW": "Data → Information → Knowledge → Wisdom: pipeline from raw facts to judgment/action.",
        "Interoperability": "Systems exchanging and using information accurately, consistently, and meaningfully.",
        "Standardized Nursing Terminologies": "Coded vocabularies (e.g., CCC, NANDA, NIC, SNOMED mappings) enabling comparable data."
    }
    for k, v in terms.items():
        with st.expander(k):
            st.write(v)

# (The rest of the app remains unchanged below)
