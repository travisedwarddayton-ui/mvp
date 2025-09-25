# Managed Analytics for Healthcare Clinics — Streamlit demo
# ---------------------------------------------------------
# How to run:
#   1) pip install -r requirements.txt
#   2) streamlit run app.py
#
# Optional: add Snowflake creds to .streamlit/secrets.toml (see bottom)

import io
import time
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Managed Analytics for Clinics",
    page_icon="🩺",
    layout="wide"
)

# ---------- Helpers
@st.cache_data
def demo_data(seed=7, months=6, clinic_name="Demo Clinic"):
    rng = np.random.default_rng(seed)
    start = (datetime.today().replace(day=1) - pd.DateOffset(months=months-1)).to_pydatetime()
    dates = pd.date_range(start, periods=months, freq="MS")

    # Patient table
    first = ["Alex","Sam","Jordan","Taylor","Chris","Jamie","Robin","Riley","Avery","Casey","Drew"]
    last  = ["Lee","Patel","Nguyen","Gonzalez","Martin","Clark","Diaz","Khan","Kim","Lopez","Brown"]
    n = 1600
    dob = pd.to_datetime(rng.integers(1950,2012,size=n)*10000 + rng.integers(1,13,size=n)*100 + rng.integers(1,28,size=n), format="%Y%m%d")
    patients = pd.DataFrame({
        "patient_id": np.arange(1,n+1),
        "first_name": rng.choice(first, size=n),
        "last_name":  rng.choice(last, size=n),
        "dob":        dob,
        "sex":        rng.choice(["F","M"], size=n),
    })
    # Inject a few dupes
    dupe_ix = rng.choice(patients.index, size=30, replace=False)
    patients = pd.concat([patients, patients.loc[dupe_ix].assign(patient_id=lambda d: d["patient_id"]+100000)], ignore_index=True)

    # Encounters
    enc = []
    for d in dates:
        days = pd.date_range(d, d + pd.offsets.MonthEnd(0), freq="D")
        for day in days:
            daily = rng.poisson(55)
            subset = patients.sample(daily, replace=True, random_state=int(day.strftime("%Y%m%d")))
            reasons = rng.choice(
                ["Primary care","Endocrinology","Cardiology","Dermatology","Ortho","Telehealth"],
                size=daily, p=[.38,.12,.15,.1,.12,.13]
            )
            show = rng.choice([0,1], size=daily, p=[.08,.92])  # no-show flag
            enc.append(pd.DataFrame({
                "encounter_id": [f"E{day:%Y%m%d}-{i}" for i in range(daily)],
                "date": day,
                "patient_id": subset["patient_id"].values,
                "department": reasons,
                "no_show": 1-show
            }))
    encounters = pd.concat(enc, ignore_index=True)

    # Claims
    rate_map = {"Primary care":120,"Endocrinology":190,"Cardiology":240,"Dermatology":160,"Ortho":220,"Telehealth":90}
    claims = encounters.assign(
        cpt=lambda d: d["department"].map({
            "Primary care":"99213","Endocrinology":"95251","Cardiology":"93000","Dermatology":"11102","Ortho":"99204","Telehealth":"99442"
        }),
        allowed_amt=lambda d: d["department"].map(rate_map) * (1 - d["no_show"])
    )
    claims["payer"] = np.where(np.random.rand(len(claims))<.62, "Commercial", "Medicare")
    claims["status"] = np.select(
        [np.random.rand(len(claims))<.06, np.random.rand(len(claims))<.11],
        ["Denied","Pending"],
        default="Paid"
    )
    claims.loc[claims["no_show"]==1, ["status","allowed_amt"]] = ["No-Show",0]

    # Staff schedule (for simple utilization calc)
    staff = pd.DataFrame({
        "staff_id": range(1,21),
        "role": np.where(rng.random(20)<.7, "Clinician","MA"),
        "fte": rng.integers(6,10,size=20)/10
    })
    return clinic_name, patients, encounters, claims, staff

def kpi_block(label, value, delta=None, help_text=None):
    st.metric(label, value, delta=delta, help=help_text)

def month_key(dt):
    return pd.Timestamp(dt).to_period("M").to_timestamp()

def percent(n, d):
    return f"{(0 if d==0 else 100*n/d):.1f}%"

# ---------- Auth (lightweight demo)
with st.sidebar:
    st.markdown("### 🔐 Sign in")
    user = st.text_input("Email", value="admin@clinic.org")
    pw = st.text_input("Password", type="password", value="demo123")
    ok = st.button("Sign in", use_container_width=True)
    st.divider()
    data_src = st.radio("Data Source", ["Sample Demo", "Upload CSVs", "Snowflake (read-only)"])
    st.caption("Switch sources any time—views update automatically.")

if not ok and "authed" not in st.session_state:
    st.info("Use the sidebar to sign in (demo accepts any credentials).")
    st.stop()
st.session_state["authed"] = True

# ---------- Data loading
clinic, patients, encounters, claims, staff = demo_data()
if data_src == "Upload CSVs":
    col1, col2, col3 = st.columns(3)
    with col1: f1 = st.file_uploader("Patients CSV", type=["csv"])
    with col2: f2 = st.file_uploader("Encounters CSV", type=["csv"])
    with col3: f3 = st.file_uploader("Claims CSV", type=["csv"])
    if f1 and f2 and f3:
        patients = pd.read_csv(f1, parse_dates=["dob"])
        encounters = pd.read_csv(f2, parse_dates=["date"])
        claims = pd.read_csv(f3)
        clinic = "Uploaded Clinic"
elif data_src == "Snowflake (read-only)":
    st.warning("Snowflake connector is stubbed for demo. Add credentials in `.streamlit/secrets.toml` and implement `read_from_snowflake()`.")
    # patients, encounters, claims = read_from_snowflake(...)

# ---------- Navbar
tabs = st.tabs(["🏠 Overview","💵 Revenue & Claims","📋 Compliance","🧹 Data Quality","⚙️ Admin"])

# ---------- Overview
with tabs[0]:
    st.markdown("## 🩺 Managed Analytics — Clinic Overview")
    st.caption("Operational KPIs across patient flow, revenue, and staff utilization.")
    m_enc = encounters.assign(month=encounters["date"].apply(month_key))
    m_claims = claims.assign(month=claims["date"].apply(month_key) if "date" in claims.columns else m_enc["month"])
    by_m = m_enc.groupby("month").agg(visits=("encounter_id","count"), no_shows=("no_show","sum")).reset_index()
    rev_m = m_claims[m_claims["status"].isin(["Paid","Pending"])].groupby("month")["allowed_amt"].sum().reset_index()

    # KPIs (last month vs prev)
    if len(by_m) >= 2:
        last, prev = by_m.iloc[-1], by_m.iloc[-2]
        last_rev = float(rev_m.iloc[-1]["allowed_amt"])
        prev_rev = float(rev_m.iloc[-2]["allowed_amt"])
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi_block("Visits (mo)", int(last["visits"]), delta=int(last["visits"]-prev["visits"]))
        with c2: kpi_block("No-Show Rate", percent(int(last["no_shows"]), int(last["visits"])),
                           delta=f"{((last['no_shows']/last['visits'])-(prev['no_shows']/prev['visits']))*100:+.1f} pts")
        with c3: kpi_block("Revenue (mo)", f"${last_rev:,.0f}", delta=f"${(last_rev-prev_rev):,.0f}")
        with c4:
            util = staff["fte"].sum()
            visits_per_fte = last["visits"] / (util if util else 1)
            kpi_block("Visits / FTE (mo)", f"{visits_per_fte:.1f}", help_text="Rough productivity indicator")

    # Charts
    left, right = st.columns((2,1))
    with left:
        st.subheader("Visits & No-Shows")
        chart = alt.Chart(by_m).mark_line(point=True).encode(
            x=alt.X("month:T", title="Month"),
            y=alt.Y("visits:Q", title="Visits"),
            tooltip=["month","visits","no_shows"]
        )
        ns = alt.Chart(by_m).mark_bar(opacity=0.35).encode(x="month:T", y=alt.Y("no_shows:Q", title="No-Shows"), tooltip=["no_shows"])
        st.altair_chart((chart + ns).resolve_scale(y="independent"), use_container_width=True)
    with right:
        st.subheader("Monthly Revenue")
        st.altair_chart(
            alt.Chart(rev_m).mark_area(line=True).encode(
                x="month:T", y=alt.Y("allowed_amt:Q", title="USD"), tooltip=["month","allowed_amt"]
            ),
            use_container_width=True
        )

    st.divider()
    st.subheader("Department Mix (last 90 days)")
    last90 = encounters[encounters["date"]>=datetime.now()-timedelta(days=90)]
    mix = last90["department"].value_counts(normalize=True).rename_axis("department").reset_index(name="share")
    st.altair_chart(
        alt.Chart(mix).mark_bar().encode(x="department:N", y=alt.Y("share:Q", axis=alt.Axis(format="%")), tooltip=["department","share"]),
        use_container_width=True
    )

# ---------- Revenue & Claims
with tabs[1]:
    st.markdown("## 💵 Revenue & Claims")
    flt_col1, flt_col2, flt_col3 = st.columns(3)
    with flt_col1:
        st.selectbox("Payer", ["All","Commercial","Medicare"], key="payer_sel")
    with flt_col2:
        st.selectbox("Status", ["All","Paid","Pending","Denied","No-Show"], key="status_sel")
    with flt_col3:
        st.multiselect("Department", sorted(claims["department"].dropna().unique()), key="dept_sel")

    df = claims.copy()
    if st.session_state.payer_sel != "All":
        df = df[df["payer"]==st.session_state.payer_sel]
    if st.session_state.status_sel != "All":
        df = df[df["status"]==st.session_state.status_sel]
    if st.session_state.dept_sel:
        df = df[df["department"].isin(st.session_state.dept_sel)]

    colA, colB, colC, colD = st.columns(4)
    colA.metric("Gross Allowed (period)", f"${df['allowed_amt'].sum():,.0f}")
    colB.metric("Avg Ticket", f"${df['allowed_amt'].replace(0,np.nan).mean():,.0f}")
    colC.metric("Denial Rate", percent((df["status"]=="Denied").sum(), len(df)))
    colD.metric("No-Show Rate", percent((df["status"]=="No-Show").sum(), len(df)))

    st.dataframe(df.sort_values("allowed_amt", ascending=False).head(500), use_container_width=True, height=380)
    st.download_button("⬇️ Export filtered claims (CSV)", df.to_csv(index=False).encode(), "claims_filtered.csv", mime="text/csv")

# ---------- Compliance
with tabs[2]:
    st.markdown("## 📋 Compliance (HIPAA / GDPR posture)")
    st.caption("Automated checks + documentation stubs your compliance officer can export.")
    # Simple rules demo
    findings = []
    # 1) Access control
    findings.append({"Area":"Access Control","Check":"Session timeout < 30 min","Status":"Pass","Notes":"Default 20 min."})
    # 2) Data minimization
    phi_cols = {"patients":["first_name","last_name","dob","sex"], "claims":["payer","status"], "encounters":["department","date"]}
    findings.append({"Area":"Data Minimization","Check":"Only required PHI stored","Status":"Pass","Notes":f"Scoped columns: {phi_cols}"})
    # 3) Encryption (stub)
    findings.append({"Area":"Encryption at Rest","Check":"Storage encryption enabled","Status":"Pass","Notes":"KMS-managed keys (demo)."})
    # 4) Audit logs
    findings.append({"Area":"Auditability","Check":"Read/write logs captured","Status":"Warn","Notes":"Enable external SIEM export in Admin."})
    # 5) DPA / BAA
    findings.append({"Area":"Agreements","Check":"DPA/BAA on file","Status":"Warn","Notes":"Upload signed BAA under Admin > Documents."})

    comp_df = pd.DataFrame(findings)
    st.dataframe(comp_df, use_container_width=True)
    st.download_button("⬇️ Export compliance report (CSV)", comp_df.to_csv(index=False).encode(), "compliance_report.csv", mime="text/csv")

    st.divider()
    st.subheader("Data Retention Policy (demo)")
    st.code("""
- Encounter data: 7 years
- Billing/claims: 7 years
- Access logs: 2 years
- Backup retention: 30 days rolling
""", language="markdown")

# ---------- Data Quality
with tabs[3]:
    st.markdown("## 🧹 Data Quality & De-duplication")
    # Duplicate detection: same first, last, dob (naive)
    key_cols = ["first_name","last_name","dob"]
    pts = patients.copy()
    pts["dupe_key"] = pts[key_cols].astype(str).agg("|".join, axis=1)
    dupes = pts[pts.duplicated("dupe_key", keep=False)].sort_values("dupe_key")
    dq = pd.DataFrame({
        "Rule":["Duplicate patients (first,last,dob)","Missing DOB","Unknown sex"],
        "Count":[len(dupes), pts["dob"].isna().sum(), (pts["sex"].isna() | ~pts["sex"].isin(["F","M"])).sum()]
    })
    c1,c2 = st.columns((1,2))
    with c1: st.dataframe(dq, use_container_width=True, height=170)
    with c2:
        if not dupes.empty:
            st.warning(f"Potential duplicates detected: {len(dupes)}")
            st.dataframe(dupes[["patient_id","first_name","last_name","dob","sex"]].head(200), use_container_width=True, height=320)
            st.download_button("⬇️ Export potential duplicates", dupes.to_csv(index=False).encode(), "potential_duplicates.csv", mime="text/csv")
        else:
            st.success("No obvious duplicates found with current rule.")

    st.divider()
    st.subheader("No-Show Drivers (last 90 days)")
    last90 = encounters[encounters["date"]>=datetime.now()-timedelta(days=90)]
    drv = last90.groupby("department").agg(
        visits=("encounter_id","count"),
        no_shows=("no_show","sum")
    ).reset_index()
    drv["no_show_rate"] = drv["no_shows"]/drv["visits"]
    st.altair_chart(
        alt.Chart(drv).mark_bar().encode(
            x="department:N",
            y=alt.Y("no_show_rate:Q", axis=alt.Axis(format="%"), title="No-Show Rate"),
            tooltip=["department","visits","no_shows","no_show_rate"]
        ),
        use_container_width=True
    )

# ---------- Admin
with tabs[4]:
    st.markdown("## ⚙️ Admin & Integrations")
    st.write("**Integrations** (stubs): Snowflake, Epic/HL7, FHIR, SFTP, S3, Google Cloud Storage.")
    st.checkbox("Enable SIEM export (audit logs)", value=False, key="siem")
    st.checkbox("Auto-archive PHI fields in exports", value=True, key="archive_phi")
    st.text_input("SFTP Endpoint", value="sftp://etl.example.org/inbound/")
    st.text_input("Notification email", value="security@clinic.org")
    st.file_uploader("Upload BAA / DPA (PDF)", type=["pdf"])
    st.button("Save settings", type="primary")

    st.divider()
    st.subheader("ETL Scheduler (demo)")
    freq = st.selectbox("Frequency", ["Hourly","Daily","Weekly"], index=1)
    t = st.time_input("Run time", value=datetime.now().time().replace(second=0, microsecond=0))
    if st.button("Schedule job"):
        st.success(f"ETL scheduled: {freq} at {t.strftime('%H:%M')} (demo).")

    st.caption("This demo app showcases the productized service. In production, these controls map to your managed platform backend.")

# ---------- Footer
st.divider()
st.caption("© Managed Analytics for Healthcare Clinics — Demo UI. All sample data is synthetic.")
