import streamlit as st
import pandas as pd
import json
from datetime import datetime


st.set_page_config(page_title="Grecert – CAE Expediente Pre‑Validation Dashboard", layout="wide")


st.title("🏗️ Grecert – CAE Expediente Pre‑Validation Portal")
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
