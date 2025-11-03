import streamlit as st
import pdfplumber, re, json
from datetime import datetime

st.set_page_config(page_title="Grecert ITV Report Parser", layout="wide")

st.title("🚌 Grecert – ITV Report Parser")
st.write("Upload a DGT ITV report PDF to extract all required fields for CAE validation.")

pdf_file = st.file_uploader("Upload ITV PDF", type=["pdf"])

if pdf_file:
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # --- VEHICLE IDENTIFICATION ---
    matricula = re.search(r"Matr[ií]cula:\s*([A-Z0-9]+)", text)
    marca = re.search(r"Marca:\s*([A-Z0-9\-’' ]+)", text)
    modelo = re.search(r"Modelo:\s*([A-Z0-9’' ]+)", text)
    bastidor = re.search(r"Bastidor:\s*([A-Z0-9]+)", text)
    renting = re.search(r"Renting:\s*(Sí|No)", text)
    titular = re.search(r"Filiación:\s*(.+)", text)
    domicilio = re.search(r"Domicilio vehículo:\s*(.+)", text)

    # --- INSURANCE ---
    aseguradora = re.search(r"Aseguradora:\s*([A-Z,\. ]+)", text)

    # --- ITV TABLE PARSE ---
    pattern = r"(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([A-Z]+)\s+([\d\.]+)\s*(.*)"
    itv_entries = []
    for m in re.finditer(pattern, text):
        itv_entries.append({
            "fecha_itv": m.group(1),
            "fecha_caducidad": m.group(2),
            "estacion": m.group(3),
            "resultado": m.group(4),
            "km": m.group(5).replace(".", ""),
            "defectos": m.group(6).strip()
        })

    # --- ODOMETER HISTORY ---
    odometer_block = re.findall(r"(\d{2}/\d{2}/\d{4})\s+([\d\.]+)\s+Estación ITV", text)
    odometer = [{"fecha": d, "km": int(k.replace(".", ""))} for d, k in odometer_block]

    # --- TECHNICAL DATA ---
    cil = re.search(r"Cilindrada:\s*([\d\.]+)", text)
    kw = re.search(r"Potencia neta \(kW\):\s*([\d\.]+)", text)
    cvf = re.search(r"Potencia fiscal.*?:\s*([\d\.]+)", text)
    comb = re.search(r"Combustible:\s*([A-Z]+)", text)
    euro = re.search(r"Nivel de emisiones:\s*(EURO [A-Z0-9]+)", text)
    plazas = re.search(r"Plazas:\s*(\d+)", text)
    masa_max = re.search(r"Masa máxima:\s*(\d+)", text)

    # --- REPORT INFO ---
    fecha_informe = re.search(r"Fecha Informe:\s*([\d/]+)", text)
    csv_code = re.search(r"RETELE-[A-Z0-9]+", text)
    solicitante = re.search(r"Solicitante:\s*([A-Z0-9 .]+)", text)
    canal = re.search(r"Canal:\s*([A-Z]+)", text)

    # --- COMPILE OUTPUT ---
    data = {
        "vehicle": {
            "matricula": matricula.group(1) if matricula else None,
            "bastidor": bastidor.group(1) if bastidor else None,
            "marca": marca.group(1).strip() if marca else None,
            "modelo": modelo.group(1).strip() if modelo else None,
            "renting": renting.group(1) if renting else None,
            "titular": titular.group(1).strip() if titular else None,
            "domicilio": domicilio.group(1).strip() if domicilio else None,
            "aseguradora": aseguradora.group(1).strip() if aseguradora else None,
        },
        "itv_history": itv_entries,
        "odometer_history": odometer,
        "technical": {
            "cilindrada": cil.group(1) if cil else None,
            "potencia_kw": kw.group(1) if kw else None,
            "potencia_fiscal": cvf.group(1) if cvf else None,
            "combustible": comb.group(1) if comb else None,
            "plazas": plazas.group(1) if plazas else None,
            "masa_maxima": masa_max.group(1) if masa_max else None,
            "nivel_emisiones": euro.group(1) if euro else None
        },
        "report": {
            "fecha_informe": fecha_informe.group(1) if fecha_informe else None,
            "csv_code": csv_code.group(0) if csv_code else None,
            "solicitante": solicitante.group(1) if solicitante else None,
            "canal": canal.group(1) if canal else None
        }
    }

    st.subheader("✅ Extracted Data (Confirm Before Sending)")
    st.json(data, expanded=True)

    # (Optional)
    if st.button("Export JSON"):
        st.download_button(
            label="Download JSON",
            file_name=f"{data['vehicle']['matricula']}_itv.json",
            mime="application/json",
            data=json.dumps(data, indent=4)
        )
