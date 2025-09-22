import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="OB-GYN Clinic Dashboard", layout="wide")

st.title("👩‍⚕️ OB-GYN Clinic Analytics Dashboard")

# Generate sample demo data
dates = pd.date_range(start="2025-01-01", periods=12, freq='M')
appointments = np.random.randint(80, 150, size=len(dates))
cancellations = np.random.randint(5, 20, size=len(dates))
procedures = np.random.randint(30, 70, size=len(dates))
revenue = appointments * np.random.randint(50, 120, size=len(dates))

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Appointments (YTD)", f"{appointments.sum()}")
col2.metric("Cancellations (YTD)", f"{cancellations.sum()}")
col3.metric("Procedures (YTD)", f"{procedures.sum()}")
col4.metric("Revenue (YTD)", f"${revenue.sum():,}")

st.markdown("---")

# Trends
st.subheader("📅 Monthly Trends")

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(dates, appointments, marker='o', label='Appointments')
ax.plot(dates, cancellations, marker='x', label='Cancellations')
ax.set_title("Appointments vs Cancellations")
ax.legend()
ax.set_xlabel("Month")
ax.set_ylabel("Count")
fig.autofmt_xdate()
st.pyplot(fig)

fig2, ax2 = plt.subplots(figsize=(10,4))
ax2.bar(dates, revenue, color='purple')
ax2.set_title("Monthly Revenue")
ax2.set_xlabel("Month")
ax2.set_ylabel("Revenue ($)")
fig2.autofmt_xdate()
st.pyplot(fig2)

# Procedure breakdown
st.subheader("🔎 Procedure Breakdown")
procedure_types = ["Prenatal Care", "Ultrasound", "Delivery", "GYN Surgery"]
procedure_counts = np.random.randint(20, 80, size=len(procedure_types))

fig3, ax3 = plt.subplots()
ax3.pie(procedure_counts, labels=procedure_types, autopct='%1.1f%%', startangle=90)
ax3.set_title("Procedures by Type")
st.pyplot(fig3)

st.markdown("---")

st.info("This dashboard is deployment-ready. To share with clients, push this file (app.py) to a GitHub repo and connect it to Streamlit Cloud. You'll instantly get a public URL.")

st.caption("Demo dashboard – data is simulated.")
