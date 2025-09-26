import streamlit as st
import pandas as pd
from datetime import datetime

# --- Initialize state ---
if "procedures" not in st.session_state:
    st.session_state.procedures = []
if "medications" not in st.session_state:
    st.session_state.medications = []
if "recovery_logs" not in st.session_state:
    st.session_state.recovery_logs = []

st.set_page_config(page_title="My Health Journey", layout="wide")

# --- Header ---
st.title("🌍 My Health Journey (Health Tourism)")
st.markdown("Keep track of your medical journey abroad and easily share it with your doctor.")

# --- Navigation ---
menu = st.sidebar.radio(
    "Navigation",
    ["Add Procedure", "Medications", "Recovery Tracker", "Timeline", "Doctor Summary"]
)

# --- Add Procedure ---
if menu == "Add Procedure":
    st.header("➕ Add a Procedure")
    with st.form("add_proc_form", clear_on_submit=True):
        proc_name = st.text_input("Procedure name")
        proc_date = st.date_input("Procedure date", datetime.today())
        location = st.text_input("Hospital / Clinic")
        doctor = st.text_input("Doctor name")
        notes = st.text_area("Notes (optional)")
        file = st.file_uploader("Upload report/photo (optional)", type=["pdf","jpg","png","jpeg"])
        submitted = st.form_submit_button("Save Procedure")

        if submitted:
            st.session_state.procedures.append({
                "Date": proc_date.strftime("%Y-%m-%d"),
                "Procedure": proc_name,
                "Location": location,
                "Doctor": doctor,
                "Notes": notes,
                "Document": file.name if file else None
            })
            st.success("✅ Procedure saved!")

# --- Medications ---
elif menu == "Medications":
    st.header("💊 Medication Tracker")
    with st.form("add_med_form", clear_on_submit=True):
        med_name = st.text_input("Medication name")
        dose = st.text_input("Dosage (e.g., 500mg, 2x/day)")
        start = st.date_input("Start date", datetime.today())
        end = st.date_input("End date", datetime.today())
        submitted = st.form_submit_button("Save Medication")

        if submitted:
            st.session_state.medications.append({
                "Medication": med_name,
                "Dosage": dose,
                "Start": start.strftime("%Y-%m-%d"),
                "End": end.strftime("%Y-%m-%d"),
            })
            st.success("💊 Medication added!")

    if st.session_state.medications:
        st.subheader("My Medications")
        st.dataframe(pd.DataFrame(st.session_state.medications))

# --- Recovery Tracker ---
elif menu == "Recovery Tracker":
    st.header("📝 Recovery Tracker")
    with st.form("add_rec_form", clear_on_submit=True):
        log_date = st.date_input("Log date", datetime.today())
        pain_level = st.slider("Pain level", 0, 10, 5)
        notes = st.text_area("Recovery notes")
        submitted = st.form_submit_button("Save Log")

        if submitted:
            st.session_state.recovery_logs.append({
                "Date": log_date.strftime("%Y-%m-%d"),
                "Pain Level": pain_level,
                "Notes": notes,
            })
            st.success("📌 Recovery log saved!")

    if st.session_state.recovery_logs:
        st.subheader("My Recovery Logs")
        df = pd.DataFrame(st.session_state.recovery_logs)
        st.line_chart(df.set_index("Date")["Pain Level"])
        st.dataframe(df)

# --- Timeline ---
elif menu == "Timeline":
    st.header("📅 Timeline View")
    if st.session_state.procedures or st.session_state.recovery_logs:
        timeline = []

        for proc in st.session_state.procedures:
            timeline.append({"Date": proc["Date"], "Type": "Procedure", "Detail": proc["Procedure"]})

        for log in st.session_state.recovery_logs:
            timeline.append({"Date": log["Date"], "Type": "Recovery Log", "Detail": f"Pain: {log['Pain Level']}"})

        df = pd.DataFrame(timeline).sort_values("Date")
        st.table(df)
    else:
        st.info("No entries yet.")

# --- Doctor Summary ---
elif menu == "Doctor Summary":
    st.header("👨‍⚕️ Doctor Summary")
    st.markdown("Show this page to your doctor for a quick overview.")

    if st.session_state.procedures:
        st.subheader("Procedures")
        st.table(pd.DataFrame(st.session_state.procedures)[["Date","Procedure","Location","Doctor"]])

    if st.session_state.medications:
        st.subheader("Medications")
        st.table(pd.DataFrame(st.session_state.medications))

    if st.session_state.recovery_logs:
        st.subheader("Recovery Logs (Pain levels)")
        st.line_chart(pd.DataFrame(st.session_state.recovery_logs).set_index("Date")["Pain Level"])

    # Export option
    combined = {
        "Procedures": st.session_state.procedures,
        "Medications": st.session_state.medications,
        "RecoveryLogs": st.session_state.recovery_logs,
    }
    csv_data = pd.DataFrame(combined["Procedures"]).to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Procedures CSV", csv_data, "procedures.csv", "text/csv")
