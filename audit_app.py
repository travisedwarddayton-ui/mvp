
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from io import StringIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

APP_TITLE = "Compliance Filing & Narrative QA (Mendoza Law)"
DATA_PATH = "data/cases.csv"
AUDIT_LOG_PATH = "data/audit_log.csv"
EVIDENCE_PATH = "data/evidence.csv"

REQUIRED_FIELDS = ["case_id","client_name","relief_type","country","assigned_to","filing_deadline","status"]

RED_FLAG_PHRASES = [
    "i don't remember",
    "not sure",
    "maybe",
    "i guess",
    "someone told me",
    "i think it was",
    "approximately",
    "about that time",
]

def load_cases():
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=["filing_deadline","last_updated"])
    except Exception:
        df = pd.DataFrame(columns=REQUIRED_FIELDS + ["last_updated","notes"])
    return df

def save_cases(df: pd.DataFrame):
    df.to_csv(DATA_PATH, index=False)

def load_evidence():
    try:
        df = pd.read_csv(EVIDENCE_PATH)
    except Exception:
        df = pd.DataFrame(columns=["case_id","evidence_id","title","text"])
    return df

def save_evidence(df: pd.DataFrame):
    df.to_csv(EVIDENCE_PATH, index=False)

def log_action(user: str, action: str, details: str):
    ts = datetime.utcnow().isoformat()
    record = pd.DataFrame([{"timestamp_utc": ts, "user": user, "action": action, "details": details}])
    try:
        log_df = pd.read_csv(AUDIT_LOG_PATH)
        log_df = pd.concat([log_df, record], ignore_index=True)
    except Exception:
        log_df = record
    log_df.to_csv(AUDIT_LOG_PATH, index=False)

def badge(text, color="blue"):
    st.markdown(f"<span style='background:{color};padding:2px 6px;border-radius:6px;color:white;font-size:12px'>{text}</span>", unsafe_allow_html=True)

def days_until(d):
    return (pd.to_datetime(d).date() - date.today()).days

def narrative_consistency_score(narrative: str, evidence_texts: list[str]):
    if not narrative or not evidence_texts:
        return None, []
    docs = [narrative] + evidence_texts
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(docs)
    sims = cosine_similarity(X[0:1], X[1:]).flatten()
    top_idx = np.argsort(sims)[::-1]
    ranked = [(int(i), float(sims[i])) for i in top_idx]
    avg = float(np.mean(sims)) if len(sims) else 0.0
    return avg, ranked

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Track filings, spot risks, and QA narratives for asylum / humanitarian relief cases.")

# --- Sidebar ---
st.sidebar.header("Quick Actions")
user = st.sidebar.text_input("Your name (for audit log)", value="Maria Pino")
if st.sidebar.button("Export current data (CSV)"):
    cases_df = load_cases()
    st.sidebar.download_button("Download cases.csv", cases_df.to_csv(index=False), "cases_export.csv", "text/csv")

st.sidebar.markdown("---")
view = st.sidebar.radio("Go to", ["Dashboard","Cases","Narrative QA","Evidence","Audit Log","Settings"])

# --- Data load ---
cases = load_cases()
evidence = load_evidence()

# --- Dashboard ---
if view == "Dashboard":
    st.subheader("At a glance")
    total_cases = len(cases)
    overdue = cases[cases["filing_deadline"] < pd.Timestamp(date.today())] if not cases.empty else pd.DataFrame()
    due_7 = cases[(cases["filing_deadline"] >= pd.Timestamp(date.today())) & (cases["filing_deadline"] <= pd.Timestamp(date.today()+timedelta(days=7)))] if not cases.empty else pd.DataFrame()
    completed = cases[cases["status"].str.lower().eq("filed")] if not cases.empty else pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active cases", total_cases)
    c2.metric("Overdue", len(overdue))
    c3.metric("Due next 7 days", len(due_7))
    c4.metric("Filed", len(completed))

    st.markdown("### Upcoming deadlines")
    if due_7.empty and overdue.empty:
        st.info("No upcoming or overdue deadlines.")
    else:
        if not overdue.empty:
            st.error("Overdue")
            st.dataframe(overdue.sort_values("filing_deadline")[["case_id","client_name","relief_type","filing_deadline","assigned_to","status"]])
        if not due_7.empty:
            st.warning("Due in next 7 days")
            st.dataframe(due_7.sort_values("filing_deadline")[["case_id","client_name","relief_type","filing_deadline","assigned_to","status"]])

# --- Cases ---
elif view == "Cases":
    st.subheader("Case list")
    if cases.empty:
        st.info("No cases yet. Add one below.")
    else:
        with st.expander("Filter", expanded=True):
            colf1, colf2, colf3 = st.columns(3)
            status_filter = colf1.multiselect("Status", sorted(cases["status"].dropna().unique().tolist()))
            assignee_filter = colf2.multiselect("Assigned to", sorted(cases["assigned_to"].dropna().unique().tolist()))
            relief_filter = colf3.multiselect("Relief type", sorted(cases["relief_type"].dropna().unique().tolist()))
            temp = cases.copy()
            if status_filter:
                temp = temp[temp["status"].isin(status_filter)]
            if assignee_filter:
                temp = temp[temp["assigned_to"].isin(assignee_filter)]
            if relief_filter:
                temp = temp[temp["relief_type"].isin(relief_filter)]
        st.dataframe(temp.sort_values("filing_deadline"))

    st.markdown("### Add / Update case")
    with st.form("new_case"):
        col1, col2, col3 = st.columns(3)
        case_id = col1.text_input("Case ID*")
        client_name = col1.text_input("Client name*")
        relief_type = col1.selectbox("Relief type*", ["Asylum","VAWA","U visa","T visa","Other"])
        country = col1.text_input("Country of origin*")

        assigned_to = col2.text_input("Assigned to*")
        filing_deadline = col2.date_input("Filing deadline*", value=date.today()+timedelta(days=21))
        status = col2.selectbox("Status*", ["Drafting","Evidence gathering","Attorney review","Ready to file","Filed","On hold"])

        notes = col3.text_area("Notes")
        submit = st.form_submit_button("Save case")
        if submit:
            # Validate
            missing = [f for f in ["case_id","client_name","relief_type","country","assigned_to","filing_deadline","status"] if not locals()[f]]
            if missing:
                st.error(f"Missing fields: {', '.join(missing)}")
            else:
                row = {
                    "case_id": case_id.strip(),
                    "client_name": client_name.strip(),
                    "relief_type": relief_type,
                    "country": country.strip(),
                    "assigned_to": assigned_to.strip(),
                    "filing_deadline": pd.to_datetime(filing_deadline),
                    "status": status,
                    "last_updated": pd.Timestamp(datetime.utcnow()),
                    "notes": notes,
                }
                # Upsert
                idx = cases.index[cases["case_id"]==row["case_id"]].to_list()
                if idx:
                    cases.loc[idx[0]] = row
                    st.success("Case updated.")
                    log_action(user, "update_case", f"{row['case_id']}")
                else:
                    cases = pd.concat([cases, pd.DataFrame([row])], ignore_index=True)
                    st.success("Case added.")
                    log_action(user, "add_case", f"{row['case_id']}")
                save_cases(cases)

    st.markdown("### Data quality checks")
    if not cases.empty:
        bad_rows = []
        for i, rec in cases.iterrows():
            missing_fields = [f for f in REQUIRED_FIELDS if pd.isna(rec.get(f,'')) or str(rec.get(f,'')).strip()=='' ]
            if missing_fields:
                bad_rows.append((rec["case_id"], ", ".join(missing_fields)))
        if bad_rows:
            st.warning("Cases with missing required fields:")
            st.table(pd.DataFrame(bad_rows, columns=["case_id","missing_fields"]))
        else:
            st.success("All cases have required fields.")

# --- Narrative QA ---
elif view == "Narrative QA":
    st.subheader("Narrative quality & consistency")
    case_choice = None
    if not cases.empty:
        case_choice = st.selectbox("Select case (optional)", ["(none)"] + cases["case_id"].tolist())
        if case_choice != "(none)":
            case_n = cases[cases["case_id"]==case_choice].iloc[0]
            st.caption(f"Client: {case_n['client_name']} • Relief: {case_n['relief_type']} • Deadline: {case_n['filing_deadline'].date()}")

    narrative = st.text_area("Paste client declaration / narrative", height=200)
    st.caption("Tip: keep PII minimal in this demo.")
    st.markdown("#### Evidence snippets")
    ev_for_case = evidence[evidence["case_id"].eq(case_choice)] if case_choice not in (None,"(none)") else evidence
    st.dataframe(ev_for_case[["evidence_id","title","text"]])

    if st.button("Analyze narrative"):
        # Red flag phrases
        found_flags = []
        lower_n = narrative.lower()
        for p in RED_FLAG_PHRASES:
            if p in lower_n:
                found_flags.append(p)
        if found_flags:
            st.error(f"Red‑flag phrases detected: {', '.join(sorted(set(found_flags)))}")
        else:
            st.success("No red‑flag phrases detected.")

        # Consistency vs evidence
        ev_texts = ev_for_case["text"].astype(str).tolist()
        score, ranked = narrative_consistency_score(narrative, ev_texts)
        if score is not None:
            st.metric("Narrative–Evidence Consistency (TF‑IDF cosine, avg)", f"{score:.2f}")
            st.caption("Top matching evidence:")
            rows = []
            for idx, sim in ranked[:5]:
                if idx < len(ev_texts):
                    ev_row = ev_for_case.iloc[idx]
                    rows.append({"evidence_id": ev_row["evidence_id"], "title": ev_row["title"], "similarity": round(sim, 3)})
            if rows:
                st.table(pd.DataFrame(rows))

        log_action(user, "narrative_analysis", f"case={case_choice}")

    st.markdown("#### Add evidence snippet")
    with st.form("add_ev"):
        ev_case = st.text_input("Case ID (optional, link to a case)", value="" if case_choice in (None,"(none)") else case_choice)
        ev_title = st.text_input("Title")
        ev_text = st.text_area("Text", height=120)
        ev_id = st.text_input("Evidence ID", value=f"EV{int(datetime.utcnow().timestamp())}")
        ev_submit = st.form_submit_button("Save evidence")
        if ev_submit:
            ev_df = load_evidence()
            ev_df = pd.concat([ev_df, pd.DataFrame([{"case_id": ev_case, "evidence_id": ev_id, "title": ev_title, "text": ev_text}])], ignore_index=True)
            save_evidence(ev_df)
            log_action(user, "add_evidence", f"{ev_id}")
            st.success("Evidence saved. Reload table above to see it.")

# --- Evidence page (raw) ---
elif view == "Evidence":
    st.subheader("Evidence Library")
    st.dataframe(evidence)
    st.download_button("Download evidence.csv", evidence.to_csv(index=False), "evidence_export.csv", "text/csv")

# --- Audit log ---
elif view == "Audit Log":
    st.subheader("Audit log")
    try:
        log_df = pd.read_csv(AUDIT_LOG_PATH)
        st.dataframe(log_df.tail(500))
        st.download_button("Download audit_log.csv", log_df.to_csv(index=False), "audit_log.csv", "text/csv")
    except Exception:
        st.info("No audit log yet.")

# --- Settings ---
elif view == "Settings":
    st.subheader("Settings & Help")
    st.markdown("""
    **What this demo does**
    - Tracks cases and filing deadlines
    - Highlights overdue/soon due cases
    - Runs quick data quality checks for required fields
    - Stores evidence snippets and compares them to narratives using TF‑IDF cosine similarity
    - Flags weak phrases often discouraged in legal declarations
    - Writes an audit trail of key actions (add/update/analyze)
    
    **Data location**
    - `data/cases.csv` — cases
    - `data/evidence.csv` — evidence snippets
    - `data/audit_log.csv` — audit trail
    
    **Export**
    - Use sidebar to export cases, or pages to download CSVs
    """)
    st.code("streamlit run app.py", language="bash")
