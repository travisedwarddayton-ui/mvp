import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Grecert – CAE Expediente Pre-Validation Dashboard", layout="wide")

st.title("🏗️ Grecert – CAE Expediente Pre-Validation Portal")
st.caption("Automated dossier verification prior to final CAE submission (RES010 / RES020)")

# Sidebar – Filters and Controls
st.sidebar.header("🔍 Filters & Controls")
selected_lot = st.sidebar.selectbox("Select Lot", ["ACT01_RABANAL_ALONSO_ANGELES", "ACT02_PEREZ_MARTIN_JOSE"], index=0)
status_filter = st.sidebar.multiselect("Filter by Status", ["PASS", "FLAG", "MISSING"], default=["FLAG"])
confidence_range = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, (0.0, 1.0), 0.05)

# Load Dossier Results (placeholder)
@st.cache_data
def load_results():
    sample_data = [
        {
            "dossier_id": "ACT01_RABANAL_ALONSO_ANGELES",
            "status": "FLAG",
            "confidence": 0.83,
            "apellidos_nombre": "RABANAL ALONSO, ANGELES",
            "installer": "Empresa Instaladora S.L.",
            "comunidad_autonoma": "Castilla y León",
            "issues": [
                {"code": "CSV_SURF_OUT_OF_TOL", "severity": "MAJOR", "message": "Superficie mismatch ±10% exceeded"},
                {"code": "ADDRESS_FUZZY_LOW", "severity": "MINOR", "message": "Address variation below threshold"}
            ],
            "ficha_type": "RES020",
            "superficie": 95.0,
            "ahorro": 31.8,
            "fecha_inicio": "2025-05-02",
            "fecha_fin": "2025-05-10",
            "cee_date": "2025-05-14"
        },
        {
            "dossier_id": "ACT02_PEREZ_MARTIN_JOSE",
            "status": "PASS",
            "confidence": 0.96,
            "apellidos_nombre": "PEREZ MARTIN, JOSE",
            "installer": "Soluciones Verdes S.L.",
            "comunidad_autonoma": "Madrid",
            "issues": [],
            "ficha_type": "RES010",
            "superficie": 80.0,
            "ahorro": 29.5,
            "fecha_inicio": "2025-04-11",
            "fecha_fin": "2025-04-19",
            "cee_date": "2025-04-25"
        }
    ]
    return pd.DataFrame(sample_data)

df = load_results()

# Apply filters
filtered = df[df["status"].isin(status_filter)]
filtered = filtered[(filtered["confidence"] >= confidence_range[0]) & (filtered["confidence"] <= confidence_range[1])]

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Dossiers", len(df))
col2.metric("Flagged", len(df[df.status == "FLAG"]))
col3.metric("Passed", len(df[df.status == "PASS"]))
col4.metric("Avg Confidence", f"{df.confidence.mean():.2f}")

st.markdown("---")

# Dossier Table
st.subheader(f"📁 Lot: {selected_lot}")
st.dataframe(
    filtered[["dossier_id", "status", "confidence", "apellidos_nombre", "installer", "comunidad_autonoma", "ficha_type", "superficie", "ahorro"]],
    use_container_width=True,
    hide_index=True
)

# Dossier Detail View
st.markdown("---")
st.subheader("🔎 Dossier Detail Review")
selected_dossier = st.selectbox("Select Dossier for Detail Review", filtered["dossier_id"].unique())

record = df[df.dossier_id == selected_dossier].iloc[0].to_dict()

colA, colB = st.columns(2)
with colA:
    st.markdown(f"**Applicant:** {record['apellidos_nombre']}")
    st.markdown(f"**Installer:** {record['installer']}")
    st.markdown(f"**Comunidad Autónoma:** {record['comunidad_autonoma']}")
    st.markdown(f"**Ficha Type:** {record['ficha_type']}")
with colB:
    st.markdown(f"**Surface (m²):** {record['superficie']}")
    st.markdown(f"**Savings (%):** {record['ahorro']}")
    st.markdown(f"**Dates:** {record['fecha_inicio']} → {record['fecha_fin']} (CEE {record['cee_date']})")
    st.progress(record['confidence'])

st.markdown("### ❗ Issues Found")
if len(record["issues"]):
    for issue in record["issues"]:
        st.error(f"[{issue['severity']}] {issue['code']} — {issue['message']}")
else:
    st.success("No issues detected. All validations passed.")

# Export Options
st.markdown("---")
st.subheader("📦 Final Package Generation")
colx, coly = st.columns(2)
with colx:
    if st.button("Generate Final Package", type="primary"):
        st.success(f"Package for {selected_lot} generated successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")
with coly:
    st.download_button(
        label="Download Dossier Report",
        data=json.dumps(record, indent=2),
        file_name=f"{selected_dossier}_report.json",
        mime="application/json"
    )

st.caption("© 2025 Grecert Data Validation Suite – Pre-submission QA Automation")
