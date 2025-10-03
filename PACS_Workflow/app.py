# Imaging Operations Control Tower – Streamlit MVP
# Author: ChatGPT (Radiology Software Engineer mode)

import datetime as dt
import random
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# 0) Page Config & Session State
# ------------------------------------------------------------
st.set_page_config(
    page_title="Imaging Operations Control Tower",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "seed" not in st.session_state:
    st.session_state.seed = 42
random.seed(st.session_state.seed)
np.random.seed(st.session_state.seed)

# ------------------------------------------------------------
# Synthetic Data Generation (Inventory + Exam History)
# ------------------------------------------------------------
SITES = ["Main Campus", "North Clinic", "East Outpatient", "West Oncology"]
MODALITIES = ["CT", "MRI", "XR", "US", "PET", "MG"]
VENDORS = ["Siemens", "GE", "Philips", "Canon", "Hologic"]
MODELS = {
    "CT": ["Somatom Force", "Revolution CT", "Ingenuity CT", "Aquilion One"],
    "MRI": ["MAGNETOM Aera", "SIGNA Artist", "Ingenia 1.5T", "Vantage Orian"],
    "XR": ["Ysio Max", "Discovery XR", "DigitalDiagnost", "Radrex"],
    "US": ["ACUSON Sequoia", "LOGIQ E10", "EPIQ 7", "Aplio i800"],
    "PET": ["Biograph mCT", "Discovery MI", "Vereos PET/CT", "Celesteion"],
    "MG": ["Mammomat Revelation", "Senographe Pristina", "Selenia Dimensions", "Amulet Innovality"],
}

def generate_machine_inventory(n: int = 24) -> pd.DataFrame:
    rows = []
    for i in range(n):
        modality = random.choice(MODALITIES)
        vendor = random.choice(VENDORS)
        model = random.choice(MODELS[modality])
        site = random.choice(SITES)
        room = f"{modality}-{random.randint(1,6)}"
        install_date = dt.date.today() - dt.timedelta(days=random.randint(365, 3650))
        uptime_pct = round(np.clip(np.random.normal(98.2, 1.1), 90, 100), 2)
        status = random.choices(["Ready", "In Use", "Down", "Maintenance"], weights=[60, 25, 5, 10])[0]
        next_maint = dt.date.today() + dt.timedelta(days=random.randint(7, 120))
        cost_scan = round(np.random.uniform(20, 150), 2)
        price_scan = round(cost_scan * np.random.uniform(1.5, 4.0), 2)
        rows.append({
            "machine_id": f"M{i:03d}",
            "modality": modality,
            "vendor": vendor,
            "model": model,
            "site": site,
            "room": room,
            "status": status,
            "uptime_pct": uptime_pct,
            "install_date": install_date,
            "next_maintenance": next_maint,
            "cost_per_scan": cost_scan,
            "revenue_per_scan": price_scan,
        })
    return pd.DataFrame(rows)


def generate_exam_history(inv_df: pd.DataFrame, days: int = 120) -> pd.DataFrame:
    records = []
    start = dt.date.today() - dt.timedelta(days=days)
    for _, m in inv_df.iterrows():
        base = {"CT": 35, "MRI": 22, "XR": 65, "US": 52, "PET": 8, "MG": 18}[m.modality]
        for d in range(days):
            exam_date = start + dt.timedelta(days=d)
            weekday = exam_date.weekday()
            wk_factor = 0.5 if weekday >= 5 else 1.0
            volume = max(0, int(np.random.poisson(base * wk_factor)))
            for i in range(volume):
                exam_types = {
                    "CT": ["Thorax", "Abdomen", "Head", "Angio"],
                    "MRI": ["Brain", "Spine", "Knee", "Abdomen"],
                    "XR": ["Chest", "Hand", "Pelvis", "Spine"],
                    "US": ["Abdominal", "OB", "Vascular", "Thyroid"],
                    "PET": ["Oncology", "Neuro", "Cardiac"],
                    "MG": ["Screening", "Diagnostic"]
                }[m.modality]
                exam = random.choice(exam_types)
                scan_min = np.clip(np.random.normal({"CT": 8, "MRI": 25, "XR": 4, "US": 20, "PET": 30, "MG": 12}[m.modality], 2.5), 2, 90)
                prep_min = np.clip(np.random.normal({"CT": 7, "MRI": 15, "XR": 3, "US": 10, "PET": 20, "MG": 6}[m.modality], 2.0), 1, 60)
                wait_min = np.clip(np.random.normal(10, 6), 0, 60)
                dose_mgy = np.nan
                if m.modality in ["CT", "XR", "MG", "PET"]:
                    base_dose = {"CT": 6.5, "XR": 0.2, "MG": 1.8, "PET": 5.0}[m.modality]
                    dose_mgy = np.clip(np.random.normal(base_dose, base_dose * 0.15), 0.05, base_dose * 3)
                rejected = np.random.rand() < {"CT": 0.02, "MRI": 0.03, "XR": 0.05, "US": 0.03, "PET": 0.02, "MG": 0.03}[m.modality]
                revenue = m.revenue_per_scan
                cost = m.cost_per_scan
                records.append({
                    "exam_id": f"E{m.machine_id}-{exam_date.strftime('%Y%m%d')}-{i:03d}",
                    "date": pd.to_datetime(exam_date),
                    "site": m.site,
                    "machine_id": m.machine_id,
                    "modality": m.modality,
                    "vendor": m.vendor,
                    "model": m.model,
                    "exam_type": exam,
                    "scan_min": round(float(scan_min), 2),
                    "prep_min": round(float(prep_min), 2),
                    "wait_min": round(float(wait_min), 2),
                    "dose_mgy": round(float(dose_mgy), 3) if not np.isnan(dose_mgy) else np.nan,
                    "rejected": int(rejected),
                    "revenue": revenue,
                    "cost": cost,
                })
    return pd.DataFrame.from_records(records)

@st.cache_data(show_spinner=False)
def load_data():
    inventory = generate_machine_inventory(28)
    exams = generate_exam_history(inventory, days=150)
    return inventory, exams

inv_df, exams_df = load_data()

# ------------------------------------------------------------
# Sidebar Controls
# ------------------------------------------------------------
role = st.sidebar.selectbox("Role", ["Radiology Director", "CIO/CTO", "CFO", "Biomedical Engineering", "Modality Lead", "Data Analyst"])
site_filter = st.sidebar.multiselect("Sites", options=SITES, default=SITES)
modality_filter = st.sidebar.multiselect("Modalities", options=MODALITIES, default=MODALITIES)

# FIX: ensure start_date and end_date are datetime.date
start_date, end_date = st.sidebar.date_input(
    "Date range",
    value=(dt.date.today() - dt.timedelta(days=60), dt.date.today()),
)
if isinstance(start_date, list) or isinstance(start_date, tuple):
    start_date, end_date = start_date[0], start_date[1]

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

st.sidebar.markdown("---")
show_only_alerts = st.sidebar.checkbox("Show only machines with issues/alerts", value=False)

mask = (
    exams_df["site"].isin(site_filter)
    & exams_df["modality"].isin(modality_filter)
    & (exams_df["date"] >= start_date)
    & (exams_df["date"] <= end_date)
)
ex = exams_df.loc[mask].copy()
inv = inv_df[inv_df["site"].isin(site_filter) & inv_df["modality"].isin(modality_filter)].copy()

st.title("Imaging Operations Control Tower – Fixed")

st.write("✅ Fixed date filter TypeError by normalizing to pandas datetime.")
