
import streamlit as st
import textwrap
from datetime import datetime
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Nursing Informatics: History & Hands‑On", layout="wide")

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
    if st.button("Check", key=f"check_{key}"):
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
    # events: list of (year, label)
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
        ax.text(x, 1.06, str(x), ha="center", va="bottom", rotation=0, fontsize=9)
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
    "Hands‑On Exercises",
    "Build My Handout (Export)"
])

# ----------------------------
# Overview
# ----------------------------
if mode == "Overview":
    section_header("Nursing Informatics: Why it matters", "From early computers to today’s mHealth and EHRs", "📘")
    st.write("""
    Nursing Informatics (NI) connects **nursing**, **information science**, and **computer technology** to improve patient care,
    education, research, and administration. Over ~60+ years, NI moved from mainframes to **mobile, cloud, and AI‑assisted** tools.
    """)
    col1, col2 = st.columns([1,1])
    with col1:
        section_header("Learning Objectives", icon="🎯")
        bullet([
            "Recall the major time periods and milestones in NI.",
            "Differentiate system software, utilities, and applications.",
            "Explain DIKW and where nursing tasks fit in the pipeline.",
            "Recognize EHR usability principles and patient portal roles.",
            "Identify use‑cases for wearables and mHealth in nursing.",
            "Understand open source vs proprietary choices in practice."
        ])
    with col2:
        section_header("Designed for Nigerian Learners", icon="🌍")
        bullet([
            "Mobile‑first: works on phones; short visual sections.",
            "Uses **revision** terminology and self‑study habits.",
            "Low‑data mode: text + simple charts; offline notes export.",
            "Hands‑on tasks for ward workflows & community health."
        ])
    tag_pills(["HIT", "EHR", "mHealth", "Open Source", "DIKW", "Usability", "SDOH", "Wearables"])

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
        (1990, "HIPAA era; databases & client‑server"),
        (1992, "NI recognized as a nursing specialty (ANA)"),
        (1997, "NIDSEC criteria for nursing systems"),
        (2004, "ONC established; push for interoperable EHRs"),
        (2009, "HITECH Act; 'Meaningful Use' incentives"),
        (2017, "MIPS value‑based payment impacts workflows"),
    ]
    fig = make_timeline_plot(timeline)
    st.pyplot(fig)
    st.caption("Explore how regulation and technology pushed nursing data standards and EHR adoption.")

# ----------------------------
# Key Terms
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

# ----------------------------
# Hardware & Software Basics
# ----------------------------
if mode == "Hardware & Software Basics":
    section_header("Hardware & Software Basics", "What runs behind the scenes of nursing apps", "💻")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hardware in Practice")
        bullet([
            "Point‑of‑care devices: vitals, glucose monitors.",
            "Mobile: tablets and smartphones for ward rounds.",
            "ICU equipment: monitors, infusion pumps, ventilators.",
            "Connectivity: hospital Wi‑Fi, cellular mHealth in the field."
        ])
    with col2:
        st.subheader("Software Types")
        bullet([
            "**System software**: operating systems (Windows/Linux).",
            "**Utility programs**: backup, antivirus, disk tools.",
            "**Applications**: EHR modules, e‑prescribing, LMS."
        ])
    st.divider()
    quiz_mc(
        "Which category does an antivirus tool fit into?",
        ["System software", "Utility program", "Application software"],
        correct_idx=1,
        key="q_util"
    )

# ----------------------------
# Open Source vs Proprietary
# ----------------------------
if mode == "Open Source vs Proprietary":
    section_header("Open Source (FLOSS) vs Proprietary", "Choosing wisely in low‑resource settings", "🧩")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("FLOSS – Pros")
        bullet([
            "No license fees; adaptable to local needs.",
            "Community support; transparency; faster localization.",
            "Good for education and pilot projects."
        ])
        st.subheader("FLOSS – Cons")
        bullet([
            "Requires in‑house skills for maintenance.",
            "Support may be community‑based, not guaranteed.",
        ])
    with col2:
        st.subheader("Proprietary – Pros")
        bullet([
            "Vendor support/SLA; integrated modules.",
            "Certified compliance features more common."
        ])
        st.subheader("Proprietary – Cons")
        bullet([
            "Licensing costs; vendor lock‑in; slower localization."
        ])
    quiz_mc(
        "A nursing school wants to customize an LMS with minimal cost. Which path is most flexible?",
        ["Proprietary with SLA", "FLOSS with local IT support", "Buy a generic course pack"],
        correct_idx=1,
        key="q_floss"
    )

# ----------------------------
# DIKW
# ----------------------------
if mode == "Data → Information → Knowledge → Wisdom (DIKW)":
    section_header("DIKW: From facts to action", "Place nursing tasks on the pipeline", "🧭")
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("**Pipeline**")
        st.write("""
        - **Data**: raw facts (e.g., BP 150/95 at 08:00).
        - **Information**: data with context (BP trend rising over 24h).
        - **Knowledge**: rules/patterns (hypertension risk protocols).
        - **Wisdom**: sound action/judgment (notify MO; adjust meds; educate patient).
        """)
        act = st.selectbox("Where would you place this task? – *'Compile BP readings from ward register'*",
                           ["Data", "Information", "Knowledge", "Wisdom"])
        if st.button("Check placement", key="check_dikw"):
            st.info("Expected: **Information** if you add trend/context; **Data** if you only copy raw values.")
    with col2:
        st.markdown("**Mini‑Case**")
        st.write("""
        Community clinic reports many missed follow‑ups for DM patients. You have SMS reminders, glucometer data,
        and nurse notes from home visits. What **new information** can you generate, and what action (wisdom) follows?
        """)
        st.text_area("Your plan (2–4 lines):", height=120, key="plan_dikw")

# ----------------------------
# EHRs & Usability
# ----------------------------
if mode == "EHRs, Usability & Patient Portals":
    section_header("EHRs, Usability & Patient Portals", "Design that helps nurses, not hinders", "🧩")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Usability Principles (selected)")
        bullet([
            "Match workflow: fewer clicks at point of care.",
            "Consistency & clarity: standard layouts and terms.",
            "Error prevention and helpful feedback messages.",
            "Involve end‑users (nurses!) in design & evaluation."
        ])
        quiz_mc(
            "Which change is MOST likely to reduce medication errors?",
            ["Bigger font sizes in notes", "Barcode medication administration (BCMA)", "Dark mode UI"],
            correct_idx=1,
            key="q_ehr_bcma"
        )
    with col2:
        st.subheader("Patient Portals")
        bullet([
            "Secure access to results, visits, meds; two‑way messaging.",
            "E‑visits for non‑urgent concerns reduce travel burdens.",
            "Patient‑controlled vs provider‑tethered access distinctions."
        ])
        st.info("Nigeria tip: portals + WhatsApp reminders improve attendance where transport/data costs are high.")

# ----------------------------
# Wearables & mHealth
# ----------------------------
if mode == "Wearables & mHealth":
    section_header("Wearables & mHealth", "From sensors to community nursing", "⌚")
    st.write("""
    Wearables track HR, SpO2, sleep, temperature, glucose, and activity. In resource‑constrained settings,
    **simple phone‑paired devices** and **SMS** can still deliver impact (e.g., hypertension follow‑up).
    """)
    bullet([
        "Screening days: spot BP/HR with phone‑linked cuffs.",
        "Post‑discharge: SMS prompts + quick symptom diaries.",
        "Diabetes: low‑cost glucometers with manual entry if no sync."
    ])
    quiz_mc(
        "A rural clinic wants to pilot mHealth with minimal cost. Which is MOST feasible to start?",
        ["Full CGM integration into EHR", "SMS reminders + manual BP logs", "AR glasses for all nurses"],
        correct_idx=1,
        key="q_mhealth"
    )

# ----------------------------
# Big Data Workgroups
# ----------------------------
if mode == "Nursing Big Data Workgroups":
    section_header("Nursing Big Data – What matters", "From care coordination to SDOH", "🧱")
    st.write("Example workstreams you can translate to local projects:")
    bullet([
        "Care Coordination: share minimum comparable data across facilities.",
        "Clinical Data Analytics: track nurse‑sensitive outcomes (falls, pressure injuries).",
        "Transforming Documentation: reduce burden; capture once, reuse many times.",
        "Social Determinants of Health (SDOH): integrate housing, transport, income context for care plans."
    ])
    st.success("Exercise idea: Define 5 nurse‑sensitive indicators for your ward and a weekly data capture plan.")

# ----------------------------
# Hands‑On Exercises
# ----------------------------
if mode == "Hands‑On Exercises":
    section_header("Hands‑On: Try it now", "Short practice aligned to Nigerian revision style", "🧪")
    with st.form("ex1"):
        st.markdown("**Exercise 1: Classify Software**")
        a = st.selectbox("Bedside vitals viewer", ["System", "Utility", "Application"], key="e1a")
        b = st.selectbox("Disk backup tool", ["System", "Utility", "Application"], key="e1b")
        c = st.selectbox("Operating system", ["System", "Utility", "Application"], key="e1c")
        submitted = st.form_submit_button("Check Answers")
        if submitted:
            score = 0
            score += 1 if a == "Application" else 0
            score += 1 if b == "Utility" else 0
            score += 1 if c == "System" else 0
            st.write(f"Score: **{score}/3**")
            if score == 3:
                st.success("Great job!")
            else:
                st.info("Review the Hardware & Software section.")
    st.divider()
    with st.form("ex2"):
        st.markdown("**Exercise 2: Map Tasks to DIKW**")
        t1 = st.selectbox("Compile weekly BP sheet", ["Data", "Information", "Knowledge", "Wisdom"], key="t1")
        t2 = st.selectbox("Create HTN education plan", ["Data", "Information", "Knowledge", "Wisdom"], key="t2")
        t3 = st.selectbox("Detect rising BP trend", ["Data", "Information", "Knowledge", "Wisdom"], key="t3")
        submitted2 = st.form_submit_button("Check Answers  ")
        if submitted2:
            keymap = {"t1": "Information", "t2": "Wisdom", "t3": "Knowledge"}
            score = (1 if t1==keymap["t1"] else 0) + (1 if t2==keymap["t2"] else 0) + (1 if t3==keymap["t3"] else 0)
            st.write(f"Score: **{score}/3**")
            st.caption("Hints: Trend/context → Information; Action/plan → Wisdom; Pattern/rule → Knowledge.")
    st.divider()
    st.markdown("**Exercise 3: Improve Usability**")
    st.write("List 2 changes in your current documentation screen that would save time or reduce errors.")
    st.text_area("Your ideas:", height=120)

# ----------------------------
# Build My Handout
# ----------------------------
if mode == "Build My Handout (Export)":
    section_header("Create Your Revision Handout", "Turn your notes into a downloadable file", "📝")
    default = """
    # Nursing Informatics – Quick Revision Notes
    Topics to cover:
    - Timeline highlights (5 bullets)
    - Definitions (HIT, EHR, DIKW)
    - 3 usability principles I will apply next week
    - mHealth idea for my ward/community
    """
    notes = st.text_area("Edit your notes (markdown or plain text):", value=default.strip(), height=240)
    buf = io.BytesIO(notes.encode("utf-8"))
    st.download_button("Download Handout (.txt)", data=buf, file_name="nursing_informatics_revision.txt", mime="text/plain")
    st.success("Tip: Share with your study group on WhatsApp or print for offline revision.")
