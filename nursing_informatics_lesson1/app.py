import streamlit as st
import random

st.set_page_config(page_title="Software Sorting Trainer", layout="centered")

st.title("💻 Software Sorting Trainer")
st.subheader("Drag and drop each software item into the correct category.")
st.caption("Practice classifying software into System, Utility, and Application categories.")

# ----------------------------
# Data
# ----------------------------
categories = {
    "System Software": ["Operating System", "Device Drivers", "Firmware"],
    "Utility Software": ["Antivirus", "File Compression Tool", "Backup Software"],
    "Application Software": ["Microsoft Word", "Web Browser", "EHR App (Electronic Health Record)"],
}

# Flatten all items
all_items = sum(categories.values(), [])
random.shuffle(all_items)

# ----------------------------
# UI
# ----------------------------
st.divider()
st.write("### Step 1: Sort These Items")
st.info("💡 Tip: Think about what the software *does* — manages hardware, maintains performance, or supports daily work.")

col1, col2, col3 = st.columns(3)
col1.markdown("**System Software**")
col2.markdown("**Utility Software**")
col3.markdown("**Application Software**")

# Session state for tracking choices
if "answers" not in st.session_state:
    st.session_state.answers = {item: None for item in all_items}

for item in all_items:
    st.markdown(f"🧩 **{item}**")
    st.session_state.answers[item] = st.radio(
        "Choose category:",
        ["System Software", "Utility Software", "Application Software", "Not sure yet"],
        index=3,
        key=item,
        label_visibility="collapsed"
    )

st.divider()

# ----------------------------
# Check Answers
# ----------------------------
if st.button("Check My Answers"):
    correct = 0
    total = len(all_items)
    st.write("### 🧾 Results")

    for category, items in categories.items():
        for i in items:
            user_choice = st.session_state.answers[i]
            if user_choice == category:
                st.success(f"✅ {i}: Correct ({category})")
                correct += 1
            else:
                st.error(f"❌ {i}: {user_choice or 'No answer'} → Correct answer: {category}")

    st.info(f"**Score:** {correct} / {total}")

    if correct == total:
        st.balloons()
        st.success("Excellent! You’ve mastered the software classification.")
    elif correct >= total * 0.7:
        st.success("Good work! Review the incorrect ones to improve.")
    else:
        st.warning("Keep practicing — revisit the chapter on software types.")

st.divider()
st.caption("Built for Nursing Informatics practice – helps visualize where each tool fits in the computing environment.")
