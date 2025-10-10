
import streamlit as st
import statistics
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="DIKW Pyramid Interactive", layout="wide")
st.title("🧭 DIKW Pyramid Interactive")
st.caption("Drag cards (or use the fallback) to order **Data → Information → Knowledge → Wisdom**, then transform raw vitals into a care plan.")

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
TARGET_ORDER = ["Data", "Information", "Knowledge", "Wisdom"]

def normalize(v: str) -> str:
    return v.strip().title()

def check_order(order_list):
    clean = [normalize(x) for x in order_list]
    return clean == TARGET_ORDER

def parse_numbers(text):
    nums = re.findall(r"-?\d+(?:\.\d+)?", text or "")
    return [float(n) for n in nums]

def vitals_to_info(bp_list):
    if not bp_list:
        return {}
    mean_val = statistics.mean(bp_list)
    trend = "flat"
    if len(bp_list) >= 2:
        if bp_list[-1] > bp_list[0] + 5:
            trend = "rising"
        elif bp_list[-1] < bp_list[0] - 5:
            trend = "falling"
    return {"count": len(bp_list), "mean": mean_val, "min": min(bp_list), "max": max(bp_list), "trend": trend}

def info_to_knowledge(info):
    if not info:
        return {}
    mean_val = info["mean"]
    # Very simple teaching rule (not clinical guidance): mean >= 140 -> potential HTN concern
    rule = None
    if mean_val >= 140:
        rule = "Potential hypertension concern (mean systolic ≥ 140)."
    elif mean_val >= 130:
        rule = "Elevated blood pressure (mean systolic ≥ 130)."
    else:
        rule = "Within normal/elevated range; continue routine monitoring."
    return {"rule": rule}

def knowledge_to_wisdom(info, knowledge):
    if not info or not knowledge:
        return []
    actions = []
    if "hypertension" in knowledge["rule"].lower():
        actions = [
            "Recheck BP in 15 minutes; ensure proper cuff size/position.",
            "Notify medical officer and review antihypertensive orders.",
            "Assess symptoms (headache, vision changes, chest pain).",
            "Provide brief education: salt reduction, medication adherence.",
        ]
    elif "elevated" in knowledge["rule"].lower():
        actions = [
            "Reinforce lifestyle advice; schedule follow-up reading.",
            "Check technique; confirm with manual cuff if available."
        ]
    else:
        actions = ["Continue routine monitoring as per protocol."]
    return actions

# ---------------------------------------------------------
# Drag-and-drop availability
# ---------------------------------------------------------
HAVE_SORTABLES = False
try:
    from streamlit_sortables import sort_items  # type: ignore
    HAVE_SORTABLES = True
except Exception:
    HAVE_SORTABLES = False

# ---------------------------------------------------------
# Section 1: Order the DIKW Cards
# ---------------------------------------------------------
st.header("1) Order the DIKW Cards")

cards = ["Wisdom", "Knowledge", "Information", "Data"]  # intentionally shuffled

if HAVE_SORTABLES:
    st.success("Drag-and-drop enabled (streamlit-sortables detected). Arrange the cards left → right.")
    placed = sort_items(
        items=cards,
        groups=["DIKW Order"],
        direction="horizontal",
        multi_containers=False,
        key="dikw_sort"
    )
    # sort_items returns a dict of group -> list
    current_order = placed.get("DIKW Order", [])
else:
    st.info("Fallback mode (no extra packages). Use the selectors to set the order from 1 to 4.")
    cols = st.columns(4)
    positions = {}
    for i, label in enumerate(cards):
        with cols[i]:
            positions[label] = st.selectbox(
                f"{label} position",
                ["1","2","3","4"],
                key=f"pos_{label}"
            )
    # Build the order by position value
    try:
        current_order = [lbl for lbl, pos in sorted(positions.items(), key=lambda x: int(x[1]))]
    except Exception:
        current_order = []

if st.button("✅ Check Order"):
    if not current_order or len(current_order) != 4:
        st.warning("Please arrange all four cards.")
    else:
        if check_order(current_order):
            st.balloons()
            st.success(f"Correct! {current_order}")
        else:
            st.error(f"Not quite: {current_order} → Correct order is {TARGET_ORDER}.")

st.divider()

# ---------------------------------------------------------
# Section 2: From Raw Vitals to a Care Plan
# ---------------------------------------------------------
st.header("2) Transform Raw Vitals into a Care Plan (DIKW in action)")

colL, colR = st.columns([1,1])

with colL:
    st.subheader("Enter Systolic BP Readings")
    st.caption("Paste numbers separated by commas or spaces (e.g., 128, 135, 142, 150).")
    raw = st.text_area("Readings:", height=120, placeholder="128 135 142 150 148 152")
    bp_vals = parse_numbers(raw)
    if bp_vals:
        st.write(f"Detected {len(bp_vals)} readings.")
    else:
        st.write("No readings yet.")

    if bp_vals:
        # Plot
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(range(1, len(bp_vals)+1), bp_vals, marker="o")
        ax.set_xlabel("Reading #")
        ax.set_ylabel("Systolic BP")
        ax.set_title("Raw Data → Visualized Trend (Information)")
        ax.grid(True, linestyle="--", linewidth=0.5)
        st.pyplot(fig)

with colR:
    st.subheader("DIKW Breakdown")
    if bp_vals:
        st.markdown("**Data**")
        st.write(f"Raw values: {bp_vals}")

        info = vitals_to_info(bp_vals)
        st.markdown("**Information**")
        st.write({
            "count": info["count"],
            "mean": round(info["mean"], 1),
            "min": info["min"],
            "max": info["max"],
            "trend": info["trend"]
        })

        know = info_to_knowledge(info)
        st.markdown("**Knowledge**")
        st.write(know["rule"])

        wiz = knowledge_to_wisdom(info, know)
        st.markdown("**Wisdom (Action Plan)**")
        for a in wiz:
            st.markdown(f"- {a}")
    else:
        st.info("Enter readings on the left to see the DIKW transformation.")

st.divider()
st.caption("Educational demo only — not medical advice. DIKW model adapted for nursing informatics practice.")
