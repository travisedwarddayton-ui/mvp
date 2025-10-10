import streamlit as st
from streamlit_sortables import sort_items

st.set_page_config(page_title="Software Sorting Trainer", layout="wide")

st.title("💻 Software Sorting Trainer – Drag & Drop Edition")
st.caption("Practice classifying software into **System**, **Utility**, and **Application** categories by dragging cards into the right box.")

st.divider()
st.info("💡 Tip: Think about what the software *does* — manages hardware, maintains performance, or supports everyday nursing tasks.")

# ---------------------------------------------------------
# 1️⃣ Define data
# ---------------------------------------------------------
correct_answers = {
    "Operating System": "System Software",
    "Device Drivers": "System Software",
    "Firmware": "System Software",
    "Antivirus": "Utility Software",
    "File Compression Tool": "Utility Software",
    "Backup Software": "Utility Software",
    "Microsoft Word": "Application Software",
    "Web Browser": "Application Software",
    "EHR App (Electronic Health Record)": "Application Software",
}

# Initial pool of draggable cards
items = list(correct_answers.keys())

# ---------------------------------------------------------
# 2️⃣ Display three target categories
# ---------------------------------------------------------
st.subheader("🧩 Step 1: Sort the cards below")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🧠 System Software")
    st.caption("Controls or manages the computer hardware (e.g., OS, drivers).")
with col2:
    st.markdown("### 🧰 Utility Software")
    st.caption("Supports system maintenance and performance (e.g., antivirus).")
with col3:
    st.markdown("### 📝 Application Software")
    st.caption("Used to perform user tasks (e.g., Word, browsers, EHR).")

# ---------------------------------------------------------
# 3️⃣ Drag-and-drop interactive area
# ---------------------------------------------------------
sorted_dict = sort_items(
    items=items,
    groups=["System Software", "Utility Software", "Application Software"],
    direction="horizontal",
    multi_containers=True,
    key="software_sort"
)

st.divider()

# ---------------------------------------------------------
# 4️⃣ Evaluate results
# ---------------------------------------------------------
if st.button("✅ Check My Answers"):
    total = len(items)
    correct = 0
    st.subheader("🧾 Results")

    for category, placed_items in sorted_dict.items():
        st.markdown(f"**{category}:**")
        for i in placed_items:
            expected = correct_answers[i]
            if expected == category:
                st.success(f"✅ {i}")
                correct += 1
            else:
                st.error(f"❌ {i} → Correct: {expected}")

    st.info(f"**Score:** {correct} / {total}")

    if correct == total:
        st.balloons()
        st.success("Excellent! You’ve mastered the software classification.")
    elif correct >= total * 0.7:
        st.success("Good work! Review the ones you misplaced.")
    else:
        st.warning("Keep practicing — revisit the chapter on software types.")

st.divider()
st.caption("Built for Nursing Informatics students to reinforce understanding of software categories interactively.")
