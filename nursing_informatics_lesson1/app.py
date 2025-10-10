
import streamlit as st

st.set_page_config(page_title="Software Sorting Trainer – Drag & Drop (with Fallback)", layout="wide")

st.title("💻 Software Sorting Trainer")
st.caption("Sort software into **System**, **Utility**, and **Application**. Uses drag & drop if available, otherwise a click-to-move fallback.")

# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
CORRECT = {
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

CATEGORIES = ["System Software", "Utility Software", "Application Software"]

# ---------------------------------------------------------
# Try to import drag-and-drop component
# ---------------------------------------------------------
HAVE_SORTABLES = False
try:
    from streamlit_sortables import sort_items  # type: ignore
    HAVE_SORTABLES = True
except Exception:
    HAVE_SORTABLES = False

st.info("💡 Tip: Think about whether the software manages hardware, maintains the system, or helps you do daily tasks.")

# ---------------------------------------------------------
# Helper: grading
# ---------------------------------------------------------
def grade(placed: dict[str, list[str]]):
    total = sum(len(v) for v in placed.values())
    correct = 0
    rows = []
    for cat, items in placed.items():
        for item in items:
            expected = CORRECT.get(item)
            if expected == cat:
                rows.append(("✅", item, cat, "Correct"))
                correct += 1
            else:
                rows.append(("❌", item, cat or "—", f"Correct: {expected}"))
    return correct, total, rows

# ---------------------------------------------------------
# Mode A: Real Drag & Drop (requires streamlit-sortables)
# ---------------------------------------------------------
if HAVE_SORTABLES:
    st.subheader("🧩 Drag & Drop Mode (streamlit-sortables detected)")
    items = list(CORRECT.keys())

    st.markdown("#### Step 1: Drag each card into the correct category")
    placed = sort_items(
        items=items,
        groups=CATEGORIES,
        direction="horizontal",
        multi_containers=True,
        key="dragdrop_sort"
    )

    st.divider()
    if st.button("✅ Check My Answers", key="check_drag"):
        correct, total, rows = grade(placed)
        st.subheader("🧾 Results")
        for symbol, item, chosen, note in rows:
            if symbol == "✅":
                st.success(f"{symbol} {item} — {chosen}")
            else:
                st.error(f"{symbol} {item} — {chosen} | {note}")
        st.info(f"**Score:** {correct} / {total}")
        if correct == total:
            st.balloons()
            st.success("Excellent! You’ve mastered software classification.")
        elif correct >= total * 0.7:
            st.success("Good work! Review the ones you misplaced.")
        else:
            st.warning("Keep practicing — review the chapter on software types.")

# ---------------------------------------------------------
# Mode B: Fallback – Click-to-Move (no extra packages)
# ---------------------------------------------------------
else:
    st.subheader("🧩 Fallback Mode (no extra packages required)")
    st.caption("Install `streamlit-sortables` for drag & drop, or use this no-dependency interactive interface.")

    if "pool" not in st.session_state:
        st.session_state.pool = list(CORRECT.keys())
        st.session_state.system = []
        st.session_state.utility = []
        st.session_state.application = []

    left, mid, right = st.columns(3)

    with left:
        st.markdown("### 🎒 Item Pool")
        if st.session_state.pool:
            selected = st.selectbox("Pick an item to place:", ["— Select —"] + st.session_state.pool, key="pick_item")
        else:
            selected = "— Select —"
        st.markdown("### Move to:")
        c1, c2, c3 = st.columns(3)
        if c1.button("🧠 System", use_container_width=True):
            if selected and selected != "— Select —" and selected in st.session_state.pool:
                st.session_state.pool.remove(selected)
                st.session_state.system.append(selected)
        if c2.button("🧰 Utility", use_container_width=True):
            if selected and selected != "— Select —" and selected in st.session_state.pool:
                st.session_state.pool.remove(selected)
                st.session_state.utility.append(selected)
        if c3.button("📝 App", use_container_width=True):
            if selected and selected != "— Select —" and selected in st.session_state.pool:
                st.session_state.pool.remove(selected)
                st.session_state.application.append(selected)

        if st.button("♻️ Reset"):
            st.session_state.pool = list(CORRECT.keys())
            st.session_state.system = []
            st.session_state.utility = []
            st.session_state.application = []

    with mid:
        st.markdown("### 🧠 System Software")
        for i, item in enumerate(st.session_state.system):
            cols = st.columns([4,1])
            cols[0].markdown(f"- **{item}**")
            if cols[1].button("←", key=f"sys_back_{i}"):
                st.session_state.system.remove(item)
                st.session_state.pool.append(item)

    with right:
        st.markdown("### 🧰 Utility Software")
        for i, item in enumerate(st.session_state.utility):
            cols = st.columns([4,1])
            cols[0].markdown(f"- **{item}**")
            if cols[1].button("←", key=f"uti_back_{i}"):
                st.session_state.utility.remove(item)
                st.session_state.pool.append(item)

        st.markdown("### 📝 Application Software")
        for i, item in enumerate(st.session_state.application):
            cols = st.columns([4,1])
            cols[0].markdown(f"- **{item}**")
            if cols[1].button("←", key=f"app_back_{i}"):
                st.session_state.application.remove(item)
                st.session_state.pool.append(item)

    st.divider()
    if st.button("✅ Check My Answers", key="check_fallback"):
        placed = {
            "System Software": st.session_state.system,
            "Utility Software": st.session_state.utility,
            "Application Software": st.session_state.application,
        }
        correct, total, rows = grade(placed)
        st.subheader("🧾 Results")
        for symbol, item, chosen, note in rows:
            if symbol == "✅":
                st.success(f"{symbol} {item} — {chosen}")
            else:
                st.error(f"{symbol} {item} — {chosen} | {note}")
        st.info(f"**Score:** {correct} / {total}")
        if correct == total:
            st.balloons()
            st.success("Excellent! You’ve mastered software classification.")
        elif correct >= total * 0.7:
            st.success("Good work! Review the ones you misplaced.")
        else:
            st.warning("Keep practicing — review the chapter on software types.")
