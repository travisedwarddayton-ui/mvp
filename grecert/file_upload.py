import streamlit as st
import zipfile
import tempfile
import os
import fitz  # PyMuPDF
import re
from snowflake.connector import connect
from dotenv import load_dotenv

load_dotenv()

# =============================
#  PDF PROCESSOR (same as yours)
# =============================
def add_continuation_headers(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    modifications_made = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        blocks = page.get_text("dict")["blocks"]

        # === ITV TABLE ===
        has_itv_data = bool(re.search(
            r'\d{2}/\d{2}/\d{4}\s+\d{2}/\d{2}/\d{4}\s+\d+\s+(FAVORABLE|DESFAVORABLE)',
            text
        ))
        has_historial_header = "HISTORIAL DE INSPECCIONES" in text

        if has_itv_data and not has_historial_header:
            fecha_itv_y = None
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if "Fecha ITV" in span["text"]:
                                fecha_itv_y = block["bbox"][1]
                                break

            if fecha_itv_y:
                page.insert_text(
                    (40, fecha_itv_y - 15),
                    "HISTORIAL DE INSPECCIONES TECNICAS (Continuacion)",
                    fontsize=10,
                    fontname="helv"
                )
                modifications_made += 1

        # === ODOMETER TABLE ===
        has_odometer_data = bool(re.search(
            r'\d{2}/\d{2}/\d{4}\s+[\d.]+\s+Estaci[oó]n\s+ITV',
            text
        ))
        has_odometer_header = "HISTORIAL DE LECTURAS" in text or "CUENTAKILOMETROS" in text

        if has_odometer_data and not has_odometer_header:
            fecha_lectura_y = None
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if "Fecha de Lectura" in span["text"]:
                                fecha_lectura_y = block["bbox"][1]
                                break

            if fecha_lectura_y:
                page.insert_text(
                    (40, fecha_lectura_y - 15),
                    "HISTORIAL DE LECTURAS DEL CUENTAKILOMETROS (Continuacion)",
                    fontsize=10,
                    fontname="helv"
                )
                modifications_made += 1

    doc.save(output_pdf)
    doc.close()
    return modifications_made


# =============================
# SNOWFLAKE UPLOAD
# =============================

def upload_to_snowflake_stage(local_path, stage_path):
    conn = snowflake.connector.connect(
        user="STREAMLIT_USER",
        password="StrongPasswordHere123!",
        account="UILIVGK-NR22639",
        warehouse="GRECERT_WH",
        role="STREAMLIT_ROLE",
        database="GRECERT_DB",
        schema="PUBLIC"
    )

    cs = conn.cursor()
    try:
        cs.execute(f"PUT file://{local_path} @{stage_path} AUTO_COMPRESS=FALSE")
    finally:
        cs.close()
        conn.close()


# =============================
# STREAMLIT UI
# =============================
st.title("📄 PDF Processor + Snowflake Uploader")

uploaded_zip = st.file_uploader("Upload ZIP of PDFs", type="zip")

if uploaded_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "input.zip")

        # Save ZIP temporarily
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        st.write("### Extracted files:")
        pdf_files = [f for f in os.listdir(temp_dir) if f.lower().endswith(".pdf")]
        st.write(pdf_files)

        results = []

        for pdf_name in pdf_files:
            original_path = os.path.join(temp_dir, pdf_name)
            processed_path = os.path.join(temp_dir, f"processed_{pdf_name}")

            modifications = add_continuation_headers(original_path, processed_path)

            # Upload to Snowflake stage
            upload_to_snowflake_stage(
                processed_path,
                stage_path="GRECERT_STAGE/ingest"  # <-- Change to your internal stage
            )

            results.append((pdf_name, modifications))

        st.success("Processing complete!")
        st.write("### Results:")
        for pdf, mods in results:
            st.write(f"{pdf}: {mods} modifications")
