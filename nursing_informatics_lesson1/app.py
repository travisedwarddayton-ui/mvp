import streamlit as st
import statistics
import re
import time
import graphviz
import matplotlib.pyplot as plt

st.set_page_config(page_title="DIKW Visual Interactive", layout="wide")

st.title("🧭 DIKW Pyramid Interactive – Visual Edition")
st.caption("Watch how raw data transforms into information, knowledge, and wisdom.")

# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------
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
    if mean_val >= 140:
        rule = "Potential hypertension concern (mean systolic ≥ 140)."
    elif mean_val >= 130:
        rule = "Elevated blood pressure (mean systolic ≥ 130)."
    else:
        rule = "Within normal range; continue routine monitoring."
    return {"rule": rule}

def knowledge_to_wisdom(info, knowledge):
    if not info or not knowledge:
        return []
    actions = []
    if "hypertension" in knowledge["rule"].lower():
        actions = [
            "Recheck BP in 15 minutes; confirm proper cuff use.",
            "Notify medical officer and review antihypertensive orders.",
            "Educate on salt reduction and medication adherence.",
        ]
    elif "elevated" in knowledge["rule"].lower():
        actions = [
            "Reinforce lifestyle advice; schedule follow-up reading.",
            "Confirm with manual cuff if possible."
        ]
    else:
        actions = ["Continue routine monitoring as per protocol."]
    return actions

# ------------------------------------------------------------
# Step 1: Animated DIKW Pyramid
# ------------------------------------------------------------
st.header("1️⃣ The DIKW Pyramid")

st.caption("Click **Reveal Layers** to visualize how each level builds upon the previous one.")

if st.button("Reveal Layers 🧩"):
    layers = [
        ("Data", "#219ebc"),
        ("Information", "#8ecae6"),
        ("Knowledge", "#ffb703"),
        ("Wisdom", "#fb8500")
    ]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.axis("off")
    for i, (label, color) in enumerate(layers):
        ax.fill_between(
            [i-1.5, i+1.5],
            [i, i],
            [i+1, i+1],
            color=color,
            alpha=0.8
        )
        ax.text(i, i+0.5, label, ha="center", va="center", fontsize=14, color="black", fontweight="bold")
        st.pyplot(fig)
        time.sleep(1)

    st.success("✅ The DIKW Pyramid builds from raw facts (Data) to wise action (Wisdom).")

st.divider()

# ------------------------------------------------------------
# Step 2: Data Flow Visualization
# ------------------------------------------------------------
st.header("2️⃣ Visualize the DIKW Flow with Real Data")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Enter Systolic BP Readings")
    st.caption("Example: 120, 128, 136, 142, 150")
    raw = st.text_area("Readings", height=120)
    bp_vals = parse_numbers(raw)
    if bp_vals:
        st.write(f"Detected {len(bp_vals)} readings: {bp_vals}")
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(range(1, len(bp_vals)+1), bp_vals, marker="o", color="#219ebc")
        ax.set_xlabel("Reading #")
        ax.set_ylabel("Systolic BP")
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)
    else:
        st.info("Enter numeric BP readings above to see transformation.")

with col2:
    if bp_vals:
        st.subheader("Transformation Flow")

        info = vitals_to_info(bp_vals)
        know = info_to_knowledge(info)
        wiz = knowledge_to_wisdom(info, know)

        dot = graphviz.Digraph()
        dot.attr(rankdir="TB", splines="polyline", nodesep="0.6", ranksep="0.6")

        dot.node("data", f"📈 Data\\nRaw BP: {len(bp_vals)} readings", style="filled", color="#219ebc", shape="box")
        dot.node("info", f"📊 Information\\nMean={round(info['mean'],1)}, Trend={info['trend']}", style="filled", color="#8ecae6", shape="box")
        dot.node("know", f"🧠 Knowledge\\n{know['rule']}", style="filled", color="#ffb703", shape="box")
        dot.node("wis", f"💡 Wisdom\\n{len(wiz)} Recommended Actions", style="filled", color="#fb8500", shape="box")

        dot.edge("data", "info")
        dot.edge("info", "know")
        dot.edge("know", "wis")

        st.graphviz_chart(dot)

        with st.expander("View Actions (Wisdom)"):
            for a in wiz:
                st.markdown(f"- {a}")

st.divider()

st.caption("Educational simulation only — not medical advice. Demonstrates the DIKW hierarchy in Nursing Informatics.")
