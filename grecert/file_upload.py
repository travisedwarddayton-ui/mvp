#!/usr/bin/env python3
"""
ZIP ingestion → DGT PDF continuation repair → Upload to Snowflake stage
"""

import fitz
import sys
import re
import os
import zipfile
import snowflake.connector


##############################
# 1. Continuation Header Logic
##############################
def add_continuation_headers(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    modifications_made = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        blocks = page.get_text("dict")["blocks"]

        # === TABLE 1: ITV INSPECTIONS ===
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
                section_y = fecha_itv_y - 15
                page.insert_text(
                    (40, section_y),
                    "HISTORIAL DE INSPECCIONES TECNICAS (Continuacion)",
                    fontsize=10,
                    fontname="helv"
                )
                modifications_made += 1

        # === TABLE 2: ODOMETER READINGS ===
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
                section_y = fecha_lectura_y - 15
                page.insert_text(
                    (40, section_y),
                    "HISTORIAL DE LECTURAS DEL CUENTAKILOMETROS (Continuacion)",
                    fontsize=10,
                    fontname="helv"
                )
                modifications_made += 1
            else:
                # fallback
                dates = list(re.finditer(r'\d{2}/\d{2}/\d{4}', text))
                if dates:
                    first_date_rect = page.search_for(dates[0].group())
                    if first_date_rect:
                        section_y = first_date_rect[0].y0 - 50
                        page.insert_text(
                            (40, section_y),
                            "HISTORIAL DE LECTURAS DEL CUENTAKILOMETROS (Continuacion)",
                            fontsize=10,
                            fontname="helv"
                        )

                        y_position = first_date_rect[0].y0 - 25
                        headers = [
                            (60, y_position, "Fecha de Lectura"),
                            (240, y_position, "Lectura"),
                            (500, y_position, "Responsable de Lectura")
                        ]

                        for x, y, label in headers:
                            page.insert_text((x, y), label, fontsize=8, fontname="helv")

                        page.draw_line((60, y_position + 5), (780, y_position + 5), width=1)
                        modifications_made += 1

    doc.save(output_pdf)
    doc.close()
    return modifications_made


##############################
# 2. Upload file to Snowflake
##############################
def upload_to_snowflake_stage(local_path, stage_name, conn):
    file_name = os.path.basename(local_path)
    put_cmd = f"""
        PUT file://{local_path} @{stage_name}
        AUTO_COMPRESS=FALSE
        OVERWRITE=TRUE;
    """
    print(f"Uploading {file_name} → {stage_name}")
    conn.cursor().execute(put_cmd)


##############################
# 3. Main ZIP Processing
##############################
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python process_zip.py input.zip")
        sys.exit(1)

    zip_file_path = sys.argv[1]
    stage_name = "GRECERT_DB.PUBLIC.GRECERT_STAGE/ingest"

    extract_dir = "./zip_extract/"
    output_dir = "./pdf_processed/"
    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print("\n=== Extracting ZIP ===")
    with zipfile.ZipFile(zip_file_path, 'r') as z:
        z.extractall(extract_dir)

    pdf_files = [
        os.path.join(extract_dir, f)
        for f in os.listdir(extract_dir)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print("No PDFs found in ZIP.")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDFs\n")

    # ---- Snowflake connection ----
    conn = snowflake.connector.connect(
        user="STREAMLIT_USER",
        password="YOUR_PASSWORD",
        account="UILIVGK-NR22639",
        warehouse="GRECERT_WH",
        role="STREAMLIT_ROLE",
        database="GRECERT_DB",
        schema="PUBLIC"
    )

    total_modified = 0

    for pdf_path in pdf_files:
        pdf_name = os.path.basename(pdf_path)
        output_pdf = os.path.join(output_dir, pdf_name)

        print(f"\n--- Processing {pdf_name} ---")
        modified = add_continuation_headers(pdf_path, output_pdf)
        total_modified += modified

        if modified > 0:
            print(f"✓ Added {modified} continuation header(s)")
        else:
            print("✓ No header added")

        # Upload processed file
        upload_to_snowflake_stage(output_pdf, stage_name, conn)

    conn.close()

    print("\n===============================================")
    print(f"Complete! Total continuation headers added: {total_modified}")
    print(f"Uploaded PDFs saved to stage: @{stage_name}")
    print("===============================================")
