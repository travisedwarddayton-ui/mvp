# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Dental Practice KPI Command Center", layout="wide")

# -----------------------
# Helpers
# -----------------------
def money(x): 
    return f"${x:,.0f}"

@st.cache_data
def gen_demo(n_months=12, seed=7):
    rng = np.random.default_rng(seed)
    start = (pd.Timestamp.today().normalize() - pd.offsets.MonthEnd(n_months)).normalize() + pd.Timedelta(days=1)
    months = pd.date_range(start, periods=n_months, freq="MS")

    providers = ["Dr. Smith", "Dr. Lee", "Hygiene-A", "Hygiene-B"]
    payers = ["PPO-A", "PPO-B", "Medicaid", "Cash"]
    services = ["Exam", "Cleaning", "Filling", "Crown", "Root Canal", "Whitening"]
    chairs = [f"Chair-{i}" for i in range(1,6)]

    # Appointments/Schedule
    rows=[]
    appt_id=1
    for m in months:
        days = pd.date_range(m, m + pd.offsets.MonthEnd(0), freq="D")
        for d in days:
            open_hrs = 8
            slots = int(open_hrs * 2)  # 30-min slots
            for chair in chairs:
                for s in range(slots):
                    booked = np.random.rand() < 0.68
                    status = "Open"
                    if booked:
                        status = np.random.choice(["Completed","No-Show","Cancelled"], p=[0.88,0.05,0.07])
                    prov = np.random.choice(providers, p=[0.35,0.25,0.2,0.2])
                    rows.append([appt_id, d, chair, prov, status])
                    appt_id+=1
    schedule = pd.DataFrame(rows, columns=["AppointmentID","Date","Chair","Provider","Status"])

    # Patients / Visits / Treatments
    n_visits = int((schedule["Status"]=="Completed").sum()*0.85)
    visit_dates = np.random.choice(schedule[schedule["Status"]=="Completed"]["Date"], size=n_visits)
    pt_ids = [f"PT{100000+i}" for i in range(n_visits)]
    new_patient = np.random.rand(n_visits) < 0.18
    payer_col = np.random.choice(payers, size=n_visits, p=[0.35,0.35,0.2,0.1])
    provider_col = np.random.choice(providers, size=n_visits, p=[0.4,0.3,0.15,0.15])
    service_col = np.random.choice(services, size=n_visits, p=[0.2,0.28,0.22,0.18,0.07,0.05])

    fee_map = {"Exam":120,"Cleaning":160,"Filling":250,"Crown":1200,"Root Canal":900,"Whitening":450}
    fee = np.array([fee_map[s] for s in service_col])
    writeoff_rate = np.where(payer_col=="Cash", 0.02, np.where(payer_col=="Medicaid",0.35,0.18))
    writeoff = fee * writeoff_rate
    production = fee - writeoff

    # Collections with lag
    lag = np.random.choice([15,30,45,60,75,90], size=n_visits, p=[0.25,0.35,0.2,0.1,0.06,0.04])
    paid = production * np.random.normal(0.92, 0.05, size=n_visits).clip(0.6,1.05)
    paid_date = pd.to_datetime(visit_dates) + pd.to_timedelta(lag, unit="D")

    visits = pd.DataFrame({
        "PatientID": pt_ids,
        "VisitDate": pd.to_datetime(visit_dates),
        "Provider": provider_col,
        "Payer": payer_col,
        "Service": service_col,
        "GrossFee": fee,
        "WriteOff": writeoff,
        "NetProduction": production,
        "Collected": paid,
        "CollectedDate": paid_date,
        "IsNewPatient": new_patient
    })

    # Treatment plans / Acceptance
    tx_rows=[]
    for i in range(int(n_visits*0.65)):
        d = visits["VisitDate"].sample(1).iloc[0]
        vprov = visits["Provider"].sample(1).iloc[0]
        pt = np.random.choice(visits["PatientID"],1)[0]
        plan_amt = np.random.choice([500,1200,2400,3500,4800], p=[0.25,0.3,0.25,0.15,0.05])
        accepted = np.random.rand() < 0.55
        tx_rows.append([pt, d, vprov, plan_amt, accepted])
    plans = pd.DataFrame(tx_rows, columns=["PatientID","PlanDate","Provider","PlanAmount","Accepted"])

    # Claims (for denial rate)
    claim_rows=[]
    for i in range(n_visits):
        reason = np.random.choice(
            ["OK","Coding","Eligibility","Documentation","Timely Filing"],
            p=[0.88,0.04,0.03,0.03,0.02]
        )
        denied = reason!="OK"
        claim_rows.append([visits["PatientID"].iloc[i], visits["VisitDate"].iloc[i], visits["Payer"].iloc[i],
                           visits["NetProduction"].iloc[i], denied, reason if denied else ""])
    claims = pd.DataFrame(claim_rows, columns=["PatientID","ServiceDate","Payer","ClaimAmount","Denied","DenialReason"])

    return schedule, visits, plans, claims

def monthify(s):
    return pd.to_datetime(s).dt.to_period("M").dt.to_timestamp()

# -----------------------
# Sidebar Inputs
# -----------------------
st.sidebar.title("Data Sources")
demo = st.sidebar.toggle("Generate demo data", value=True)

if not demo:
    sch_file = st.sidebar.file_uploader("Schedule CSV (AppointmentID,Date,Chair,Provider,Status)", type=["csv"])
    vis_file = st.sidebar.file_uploader("Visits CSV (PatientID,VisitDate,Provider,Payer,Service,GrossFee,WriteOff,NetProduction,Collected,CollectedDate,IsNewPatient)", type=["csv"])
    tx_file  = st.sidebar.file_uploader("TreatmentPlans CSV (PatientID,PlanDate,Provider,PlanAmount,Accepted)", type=["csv"])
    cl_file  = st.sidebar.file_uploader("Claims CSV (PatientID,ServiceDate,Payer,ClaimAmount,Denied,DenialReason)", type=["csv"])

if demo:
    schedule, visits, plans, claims = gen_demo()
else:
    if not all([sch_file, vis_file, tx_file, cl_file]):
        st.warning("Upload all four CSVs or enable demo data.")
        st.stop()
    schedule = pd.read_csv(sch_file, parse_dates=["Date"])
    visits   = pd.read_csv(vis_file, parse_dates=["VisitDate","CollectedDate"])
    plans    = pd.read_csv(tx_file, parse_dates=["PlanDate"])
    claims   = pd.read_csv(cl_file, parse_dates=["ServiceDate"])

# Filters
min_date = min(schedule["Date"].min(), visits["VisitDate"].min())
max_date = max(schedule["Date"].max(), visits["VisitDate"].max())
start, end = st.sidebar.date_input("Date range", (min_date.date(), max_date.date()))
provider_sel = st.sidebar.multiselect("Providers", sorted(schedule["Provider"].unique()), default=list(sorted(schedule["Provider"].unique())))
payer_sel = st.sidebar.multiselect("Payers", sorted(visits["Payer"].unique()), default=list(sorted(visits["Payer"].unique())))

# Apply filters
schedule_f = schedule[(schedule["Date"]>=pd.Timestamp(start)) & (schedule["Date"]<=pd.Timestamp(end)) & (schedule["Provider"].isin(provider_sel))]
visits_f   = visits[(visits["VisitDate"]>=pd.Timestamp(start)) & (visits["VisitDate"]<=pd.Timestamp(end)) & (visits["Provider"].isin(provider_sel)) & (visits["Payer"].isin(payer_sel))]
plans_f    = plans[(plans["PlanDate"]>=pd.Timestamp(start)) & (plans["PlanDate"]<=pd.Timestamp(end)) & (plans["Provider"].isin(provider_sel))]
claims_f   = claims[(claims["ServiceDate"]>=pd.Timestamp(start)) & (claims["ServiceDate"]<=pd.Timestamp(end)) & (claims["Payer"].isin(payer_sel))]

# -----------------------
# KPI CALCULATIONS
# -----------------------
# Production / Collections
gross = visits_f["GrossFee"].sum()
writeoff = visits_f["WriteOff"].sum()
net_production = visits_f["NetProduction"].sum()
collections = visits_f["Collected"].sum()
collection_ratio = collections / net_production if net_production else np.nan

# AR (simplified: production not yet collected within range)
open_ar = (visits_f["NetProduction"] - visits_f["Collected"]).clip(lower=0)
total_ar = open_ar.sum()

# Days in AR approximation
if len(visits_f):
    avg_daily_net = net_production / max((visits_f["VisitDate"].max() - visits_f["VisitDate"].min()).days+1, 1)
    days_in_ar = total_ar / avg_daily_net if avg_daily_net > 0 else np.nan
else:
    days_in_ar = np.nan

# Claims / Denials
denial_rate = claims_f["Denied"].mean() if len(claims_f) else np.nan
top_denials = claims_f[claims_f["Denied"]].groupby("DenialReason").size().sort_values(ascending=False).head(5)

# Patients
new_patients = int(visits_f["IsNewPatient"].sum())
unique_patients = visits_f["PatientID"].nunique()
rev_per_patient = net_production / unique_patients if unique_patients else np.nan
rev_per_visit = net_production / len(visits_f) if len(visits_f) else np.nan

# Treatment Plan Acceptance
if len(plans_f):
    tpa = plans_f["Accepted"].mean()
    avg_plan_amt = plans_f["PlanAmount"].mean()
else:
    tpa, avg_plan_amt = np.nan, np.nan

# Scheduling / Utilization
util = (schedule_f["Status"]=="Completed").sum() / (len(schedule_f)) if len(schedule_f) else np.nan
no_show = (schedule_f["Status"]=="No-Show").mean() if len(schedule_f) else np.nan
cancel = (schedule_f["Status"]=="Cancelled").mean() if len(schedule_f) else np.nan

# Hygiene recall proxy (completed hygiene services over completed)
hyg_mask = visits_f["Service"].str.contains("Cleaning", case=False, na=False)
hyg_recall_rate = (hyg_mask.sum() / max(len(visits_f),1)) if len(visits_f) else np.nan

# Payer mix & write-off %
payer_mix = visits_f.groupby("Payer")["NetProduction"].sum().sort_values(ascending=False)
writeoff_pct = writeoff / gross if gross else np.nan

# Provider productivity
prod_by_provider = visits_f.groupby("Provider")["NetProduction"].sum().sort_values(ascending=False)
visits_by_provider = visits_f.groupby("Provider")["PatientID"].count().sort_values(ascending=False)

# -----------------------
# HEADER
# -----------------------
st.title("Dental Practice KPI Command Center")
st.caption("Covers production, collections, AR, claims/denials, patients, scheduling, payer mix, and provider productivity.")

# -----------------------
# TOP METRICS
# -----------------------
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Gross Production", money(gross))
m2.metric("Write-offs", money(writeoff))
m3.metric("Net Production", money(net_production))
m4.metric("Collections", money(collections))
m5.metric("Collection Ratio", f"{collection_ratio*100:,.1f}%" if pd.notna(collection_ratio) else "—")
m6.metric("Days in AR (est.)", f"{days_in_ar:,.1f}" if pd.notna(days_in_ar) else "—")

m7, m8, m9, m10, m11, m12 = st.columns(6)
m7.metric("Denial Rate", f"{denial_rate*100:,.1f}%" if pd.notna(denial_rate) else "—")
m8.metric("New Patients", f"{new_patients:,}")
m9.metric("Revenue / Patient", money(rev_per_patient) if pd.notna(rev_per_patient) else "—")
m10.metric("Revenue / Visit", money(rev_per_visit) if pd.notna(rev_per_visit) else "—")
m11.metric("Schedule Utilization", f"{util*100:,.1f}%" if pd.notna(util) else "—")
m12.metric("No-Show / Cancel", f"{(no_show or 0)*100:,.1f}% / {(cancel or 0)*100:,.1f}%")

m13, m14, m15 = st.columns(3)
m13.metric("Tx Plan Acceptance", f"{tpa*100:,.1f}%" if pd.notna(tpa) else "—")
m14.metric("Avg Plan Amount", money(avg_plan_amt) if pd.notna(avg_plan_amt) else "—")
m15.metric("Hygiene Recall Rate (proxy)", f"{hyg_recall_rate*100:,.1f}%" if pd.notna(hyg_recall_rate) else "—")

st.markdown("---")

# -----------------------
# TABS
# -----------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Production & Collections", "AR & Cash", "Claims & Denials",
    "Patients & Growth", "Scheduling & Ops", "Payer & Provider"
])

with tab1:
    st.subheader("Monthly Production vs Collections")
    v_m = visits_f.copy()
    v_m["Month"] = monthify(v_m["VisitDate"])
    pc = v_m.groupby("Month")[["GrossFee","WriteOff","NetProduction","Collected"]].sum()
    st.line_chart(pc[["NetProduction","Collected"]])
    st.dataframe(pc.style.format({"GrossFee":money,"WriteOff":money,"NetProduction":money,"Collected":money}))

with tab2:
    st.subheader("AR Overview")
    st.write("AR = Net Production − Collections (simplified for demo).")
    ar_month = v_m.groupby("Month").apply(lambda d: (d["NetProduction"]-d["Collected"]).clip(lower=0).sum())
    ar_df = ar_month.rename("AR").to_frame()
    st.bar_chart(ar_df)
    st.metric("Total AR (current range)", money(total_ar))

with tab3:
    st.subheader("Denial Rate & Top Reasons")
    colA, colB = st.columns(2)
    with colA:
        st.metric("Denial Rate", f"{denial_rate*100:,.1f}%" if pd.notna(denial_rate) else "—")
        if not top_denials.empty:
            st.dataframe(top_denials.rename("Count"))
    with colB:
        if not claims_f.empty:
            c_m = claims_f.copy()
            c_m["Month"] = monthify(c_m["ServiceDate"])
            dr = c_m.groupby("Month")["Denied"].mean().rename("DenialRate")
            st.line_chart(dr)

with tab4:
    st.subheader("Patients & Treatment Plans")
    pcols = st.columns(3)
    pcols[0].metric("Unique Patients", f"{unique_patients:,}")
    pcols[1].metric("New Patients", f"{new_patients:,}")
    pcols[2].metric("Tx Plan Acceptance", f"{tpa*100:,.1f}%" if pd.notna(tpa) else "—")
    st.write("Revenue per patient and visit over time")
    rv = v_m.groupby("Month").agg(NetProduction=("NetProduction","sum"),
                                  Visits=("PatientID","count"),
                                  Patients=("PatientID", "nunique"))
    rv["RevPerVisit"]=rv["NetProduction"]/rv["Visits"]
    rv["RevPerPatient"]=rv["NetProduction"]/rv["Patients"]
    st.line_chart(rv[["RevPerVisit","RevPerPatient"]].fillna(0))

with tab5:
    st.subheader("Scheduling Utilization & Attendance")
    s_m = schedule_f.copy()
    s_m["Month"] = monthify(s_m["Date"])
    util_m = s_m.assign(Booked=(s_m["Status"]!="Open").astype(int),
                        Completed=(s_m["Status"]=="Completed").astype(int),
                        NoShow=(s_m["Status"]=="No-Show").astype(int),
                        Cancelled=(s_m["Status"]=="Cancelled").astype(int)) \
                 .groupby("Month")[["Booked","Completed","NoShow","Cancelled"]].sum()
    st.area_chart(util_m[["Completed","NoShow","Cancelled"]])
    st.dataframe(util_m)

with tab6:
    st.subheader("Payer Mix & Provider Productivity")
    col1, col2 = st.columns(2)
    with col1:
        if not payer_mix.empty:
            pm = payer_mix.rename("NetProduction").to_frame()
            pm["Share"] = pm["NetProduction"]/pm["NetProduction"].sum()
            st.dataframe(pm.style.format({"NetProduction":money,"Share":"{:.1%}"}))
            st.bar_chart(pm["NetProduction"])
        st.metric("Write-off %", f"{writeoff_pct*100:,.1f}%" if pd.notna(writeoff_pct) else "—")
    with col2:
        pp = prod_by_provider.rename("NetProduction").to_frame()
        pp["Visits"] = visits_by_provider
        st.dataframe(pp.style.format({"NetProduction":money}))
        st.bar_chart(pp["NetProduction"])

st.markdown("---")
st.caption("KPIs included: Gross/Net Production, Collections, Collection Ratio, AR & Days-in-AR (est), Denial Rate & reasons, New Patients, Revenue per Patient/Visit, Tx Plan Acceptance, Hygiene Recall proxy, Schedule Utilization, No-Show/Cancel, Payer Mix, Write-offs %, Provider Productivity.")
