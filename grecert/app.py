import streamlit as st
import pdfplumber
import re
import json
from datetime import datetime

# --- Streamlit Page Config ---
st.set_page_config(page_title="Grecert ITV Parser", layout="wide")

st.title("🚌 Grecert – ITV Report Parser")
st.caption("Upload a DGT ITV report PDF. The parser will extract all required CAE fields for verification.")

pdf_file = st.file_uploader("📄 Upload ITV PDF", type=["pdf"])

# --------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------
def normalize_date(date_str):
    """Normalize dates to ISO format."""
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except Exception:
        return date_str

def safe_search(pattern, text, group=1, flags=0):
    match = re.search(pattern, text, flags)
    return match.group(group).strip() if match else None

# --------------------------------------------------------------
# Main Logic
# --------------------------------------------------------------
if pdf_file:
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # ----------------------------------------------------------
    # VEHICLE INFORMATION
    # ----------------------------------------------------------
    matricula = safe_search(r"Matr[ií]cula:\s*([A-Z0-9]+)", text)
    bastidor = safe_search(r"Bastidor:\s*([A-Z0-9]+)", text)
    marca_raw = safe_search(r"Marca:\s*([A-Z0-9\-’' ]{2,20})", text)
    marca = marca_raw.replace(" F", "").strip() if marca_raw else None
    modelo_raw = safe_search(r"Modelo:\s*([A-Z'’ ]+CITY LLE)", text)
    modelo = modelo_raw.replace("  ", " ").replace(" S ", "'S ").strip() if modelo_raw else None
    renting = safe_search(r"Renting:\s*(Sí|No)", text)
    titular = safe_search(r"Filiación:\s*(.+)", text)
    domicilio = safe_search(r"Domicilio vehículo:\s*(.+)", text)
    aseguradora = safe_search(r"Aseguradora:\s*([A-Z,\. ]+)", text)
    aseguradora = re.sub(r"\s{2,}", " ", aseguradora) if aseguradora else None

    # ----------------------------------------------------------
    # ITV HISTORY TABLE (MULTILINE REGEX)
    # ----------------------------------------------------------
    itv_pattern = (
        r"(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+"
        r"(FAVORABLE|DESFAVORABLE)\s+([\d\.\-]+)\s*(.*?)(?=\n\d{2}/\d{2}/\d{4}|\Z)"
    )
    itv_entries = []
    for m in re.finditer(itv_pattern, text, re.DOTALL):
        defectos = " ".join(m.group(6).split()).strip()
        itv_entries.append({
            "fecha_itv": normalize_date(m.group(1)),
            "fecha_caducidad": normalize_date(m.group(2)),
            "estacion": m.group(3),
            "resultado": m.group(4),
            "km": m.group(5).replace(".", "").replace("-", "").strip(),
            "defectos": defectos if defectos else "---"
        })

    # ----------------------------------------------------------
    # ODOMETER HISTORY
    # ----------------------------------------------------------
    odo_matches = re.findall(r"(\d{2}/\d{2}/\d{4})\s+([\d\.]+)\s+Estación ITV", text)
    odometer = [
        {"fecha": normalize_date(d), "km": int(k.replace(".", ""))}
        for d, k in odo_matches
    ]

    # ----------------------------------------------------------
    # TECHNICAL DATA
    # ----------------------------------------------------------
    cil = safe_search(r"Cilindrada:\s*([\d\.]+)", text)
    kw = safe_search(r"Potencia neta \(kW\):\s*([\d\.]+)", text)
    cvf = safe_search(r"Potencia fiscal.*?:\s*([\d\.]+)", text)
    comb = safe_search(r"Combustible:\s*([A-Z]+)", text)
    euro = safe_search(r"Nivel de emisiones:\s*(EURO [A-Z0-9]+)", text)
    plazas_sentado = safe_search(r"Plazas:\s*(\d+)", text)
    plazas_pie = safe_search(r"Plazas pie:\s*(\d+)", text)
    masa_max = safe_search(r"Masa máxima:\s*(\d+)", text)
    masa_en_carga = safe_search(r"Masa Máxima en Carga:\s*(\d+)", text)

    # ----------------------------------------------------------
    # REPORT METADATA
    # ----------------------------------------------------------
    fecha_informe = safe_search(r"Fecha Informe:\s*([\d/]+)", text)
    csv_code = safe_search(r"(RETELE-[A-Z0-9]+)", text)
    solicitante_raw = safe_search(r"Solicitante:\s*([A-ZÑÁÉÍÓÚ0-9 ,.]+)", text)
    solicitante = solicitante_raw.rstrip(" T") if solicitante_raw else None
    canal = safe_search(r"Canal:\s*([A-Z]+)", text)

    # ----------------------------------------------------------
    # BAJA DETECTION
    # ----------------------------------------------------------
    baja_match = re.search(
        r"de baja del\s*(\d{2}/\d{2}/\d{4})\s*hasta el\s*(\d{2}/\d{2}/\d{4})",
        text,
        re.IGNORECASE,
    )
    baja_info = (
        {"inicio": normalize_date(baja_match.group(1)), "fin": normalize_date(baja_match.group(2))}
        if baja_match else None
    )

    # ----------------------------------------------------------
    # COMPILE OUTPUT JSON
    # ----------------------------------------------------------
    data = {
        "vehicle": {
            "matricula": matricula,
            "bastidor": bastidor,
            "marca": marca,
            "modelo": modelo,
            "renting": renting,
            "titular": titular,
            "domicilio": domicilio,
            "aseguradora": aseguradora,
        },
        "itv_history": itv_entries,
        "odometer_history": odometer,
        "technical": {
            "cilindrada": cil,
            "potencia_kw": kw,
            "potencia_fiscal": cvf,
            "combustible": comb,
            "plazas_sentado": plazas_sentado,
            "plazas_pie": plazas_pie,
            "masa_maxima": masa_max,
            "masa_en_carga": masa_en_carga,
            "nivel_emisiones": euro,
        },
        "report": {
            "fecha_informe": normalize_date(fecha_informe) if fecha_informe else None,
            "csv_code": csv_code,
            "solicitante": solicitante,
            "canal": canal,
        },
        "baja": baja_info,
    }

    # ----------------------------------------------------------
    # VALIDATION SUMMARY
    # ----------------------------------------------------------
    mandatory_fields = {
        "matricula": data["vehicle"]["matricula"],
        "bastidor": data["vehicle"]["bastidor"],
        "marca": data["vehicle"]["marca"],
        "modelo": data["vehicle"]["modelo"],
        "nivel_emisiones": data["technical"]["nivel_emisiones"],
        "csv_code": data["report"]["csv_code"]
    }
    missing = [k for k, v in mandatory_fields.items() if not v]

    # ----------------------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------------------
    st.subheader("✅ Extracted Data Preview")
    st.json(data, expanded=True)

    if missing:
        st.warning(f"⚠️ Missing required fields: {', '.join(missing)}")
    else:
        st.success("✅ All mandatory fields captured successfully!")

    # ----------------------------------------------------------
    # DOWNLOAD OR EXPORT
    # ----------------------------------------------------------
    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    st.download_button(
        label="💾 Download JSON",
        data=json_str,
        file_name=f"{matricula or 'vehicle'}_itv.json",
        mime="application/json"
    )
