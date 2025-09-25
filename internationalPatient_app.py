# app.py
import io, json, zipfile, datetime as dt
from dateutil import tz
from babel.numbers import format_currency
import pandas as pd
import streamlit as st
import pycountry

st.set_page_config(page_title="Intl Patient Onboarding", page_icon="🌍", layout="wide")

# -----------------------
# Simple i18n dictionary
# -----------------------
I18N = {
    "en": {
        "title": "International Patient Onboarding",
        "clinic_settings": "Clinic Settings",
        "clinic_country": "Clinic Country",
        "default_currency": "Default Currency",
        "lang": "Language",
        "patient_info": "Patient Information",
        "first_name": "First name",
        "last_name": "Last name",
        "dob": "Date of birth",
        "sex": "Sex (for clinical use)",
        "sex_opts": ["Female", "Male", "Intersex", "Unknown", "Prefer not to say"],
        "email": "Email",
        "phone": "Phone (intl format, e.g., +44 20…)",
        "nationality": "Nationality",
        "passport": "Passport / National ID",
        "visa": "Visa / Entry Permit (optional)",
        "insurance": "Insurance Card / Letter (optional)",
        "records": "Prior Medical Records (optional)",
        "address": "Current Address (where you're staying)",
        "line1": "Address line 1",
        "line2": "Address line 2 (optional)",
        "city": "City",
        "state": "State/Province/Region",
        "postal": "Postal code",
        "country": "Country",
        "emergency": "Emergency Contact",
        "em_name": "Full name",
        "em_phone": "Phone",
        "em_relationship": "Relationship",
        "appt": "Appointment Preferences",
        "tz": "Home Time Zone",
        "pref_lang": "Preferred Language for Care",
        "visit_reason": "Reason for visit",
        "date_range": "Preferred date range",
        "insurance_details": "Insurance Details",
        "has_ins": "Do you have insurance that covers care here?",
        "insurer": "Insurer name",
        "policy": "Policy/Member ID",
        "estimates": "Payment & Estimates",
        "est_amt": "Estimated deposit / self-pay estimate",
        "privacy": "Privacy, Consent & Comms",
        "consent": "I consent to processing my personal and health data for care delivery. (HIPAA/GDPR)",
        "marketing": "I agree to receive non-essential communications (optional).",
        "submit": "Submit Onboarding",
        "download_bundle": "Download Intake Bundle (FHIR JSON + PDF + CSV)",
        "success": "✅ Onboarding captured. Download your bundle or save to your system.",
        "validation": "Please complete required fields highlighted in red.",
        "doc_note": "Accepted file types: PDF, JPG, PNG; max 25 MB each.",
        "gdpr": "Note: Your data is processed under HIPAA/GDPR principles, minimized to care delivery needs.",
        "admin_note": "Admin: set your country to auto-format currency and detect locale."
    },
    "es": {
        "title": "Admisión de Pacientes Internacionales",
        "clinic_settings": "Ajustes de la Clínica",
        "clinic_country": "País de la clínica",
        "default_currency": "Moneda predeterminada",
        "lang": "Idioma",
        "patient_info": "Datos del Paciente",
        "first_name": "Nombre",
        "last_name": "Apellidos",
        "dob": "Fecha de nacimiento",
        "sex": "Sexo (uso clínico)",
        "sex_opts": ["Femenino", "Masculino", "Intersexual", "Desconocido", "Prefiero no decir"],
        "email": "Correo electrónico",
        "phone": "Teléfono (formato internacional, p. ej., +34…)",
        "nationality": "Nacionalidad",
        "passport": "Pasaporte / ID",
        "visa": "Visa / Permiso de entrada (opcional)",
        "insurance": "Seguro médico (opcional)",
        "records": "Historial médico previo (opcional)",
        "address": "Dirección actual (donde se aloja)",
        "line1": "Dirección (línea 1)",
        "line2": "Dirección (línea 2, opc.)",
        "city": "Ciudad",
        "state": "Estado/Provincia/Región",
        "postal": "Código postal",
        "country": "País",
        "emergency": "Contacto de Emergencia",
        "em_name": "Nombre completo",
        "em_phone": "Teléfono",
        "em_relationship": "Relación",
        "appt": "Preferencias de Cita",
        "tz": "Zona horaria de origen",
        "pref_lang": "Idioma preferido para la atención",
        "visit_reason": "Motivo de la visita",
        "date_range": "Rango de fechas preferido",
        "insurance_details": "Detalles del Seguro",
        "has_ins": "¿Tiene seguro que cubra la atención aquí?",
        "insurer": "Aseguradora",
        "policy": "Póliza/ID de miembro",
        "estimates": "Pagos y Presupuestos",
        "est_amt": "Depósito estimado / Autopago",
        "privacy": "Privacidad, Consentimiento y Comunicaciones",
        "consent": "Consiento el tratamiento de mis datos personales y de salud para la atención. (HIPAA/GDPR)",
        "marketing": "Acepto comunicaciones no esenciales (opcional).",
        "submit": "Enviar Admisión",
        "download_bundle": "Descargar Paquete (FHIR JSON + PDF + CSV)",
        "success": "✅ Admisión registrada. Descargue su paquete o guárdelo en su sistema.",
        "validation": "Complete los campos obligatorios resaltados en rojo.",
        "doc_note": "Tipos: PDF, JPG, PNG; máx. 25 MB c/u.",
        "gdpr": "Nota: Sus datos se procesan bajo principios HIPAA/GDPR, minimizados a lo necesario.",
        "admin_note": "Admin: Configure su país para formateo de moneda y detección de idioma."
    }
}

def t(key, lang):
    return I18N.get(lang, I18N["en"]).get(key, key)

# -----------------------
# Helpers
# -----------------------
def country_to_currency(country_name: str):
    # coarse default mapping
    mapping = {
        "United States": ("USD", "$"),
        "United Kingdom": ("GBP", "£"),
        "Ireland": ("EUR", "€"),
        "France": ("EUR", "€"),
        "Germany": ("EUR", "€"),
        "Spain": ("EUR", "€"),
        "Italy": ("EUR", "€"),
        "Canada": ("CAD", "$"),
        "Australia": ("AUD", "$"),
        "Japan": ("JPY", "¥"),
        "Saudi Arabia": ("SAR", "﷼"),
        "United Arab Emirates": ("AED", "د.إ"),
        "Mexico": ("MXN", "$"),
        "Brazil": ("BRL", "R$"),
        "India": ("INR", "₹"),
        "Malaysia": ("MYR", "RM"),
        "Singapore": ("SGD", "$")
    }
    return mapping.get(country_name, ("USD", "$"))

def format_money(amount, iso_code):
    try:
        return format_currency(amount, iso_code)
    except Exception:
        return f"{iso_code} {amount:,.2f}"

def bytes_zip(named_bytes: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, b in named_bytes.items():
            z.writestr(name, b)
    return buf.getvalue()

def make_fhir_patient(row: dict):
    # Minimal FHIR Patient + optional Coverage
    patient = {
        "resourceType": "Patient",
        "id": f"pat-{row['passport_number'] or row['email']}",
        "active": True,
        "name": [{"use": "official", "family": row["last_name"], "given": [row["first_name"]]}],
        "telecom": [
            {"system": "email", "value": row["email"]},
            {"system": "phone", "value": row["phone"]},
        ],
        "gender": row["sex_fhir"],
        "birthDate": row["dob"].isoformat(),
        "address": [{
            "line": [row["addr_line1"]] + ([row["addr_line2"]] if row["addr_line2"] else []),
            "city": row["city"],
            "state": row["state"],
            "postalCode": row["postal"],
            "country": row["country"]
        }],
        "communication": [{"language": {"text": row["pref_lang"]}}],
        "extension": [
            {"url": "http://hl7.org/fhir/StructureDefinition/patient-nationality",
             "valueCodeableConcept": {"text": row["nationality"]}}
        ],
        "contact": [{
            "relationship": [{"text": row["em_relationship"]}],
            "name": {"text": row["em_name"]},
            "telecom": [{"system": "phone", "value": row["em_phone"]}]
        }]
    }
    coverage = None
    if row["has_ins"]:
        coverage = {
            "resourceType": "Coverage",
            "id": f"cov-{row['policy']}",
            "status": "active",
            "beneficiary": {"reference": f"Patient/{patient['id']}"},
            "payor": [{"display": row["insurer"]}],
            "identifier": [{"system": "member-id", "value": row["policy"]}]
        }
    bundle = {"resourceType": "Bundle", "type": "collection", "entry": [{"resource": patient}]}
    if coverage:
        bundle["entry"].append({"resource": coverage})
    return bundle

def html_summary(row: dict, currency_iso: str, currency_symbol: str, lang: str):
    est = format_money(row["est_amt"] or 0.0, currency_iso)
    return f"""
    <html>
    <head><meta charset="utf-8"><style>
    body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color:#111; }}
    h1 {{ margin-bottom: 0; }}
    .muted {{ color:#555; }}
    .section {{ margin-top:18px; }}
    table {{ width:100%; border-collapse: collapse; }}
    td {{ padding:6px 8px; vertical-align: top; }}
    .label {{ width: 28%; color:#444; }}
    .box {{ border:1px solid #eee; padding:12px; border-radius:8px; }}
    </style></head>
    <body>
    <h1>{t('title', lang)}</h1>
    <div class="muted">{dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</div>

    <div class="section box">
      <h3>{t('patient_info', lang)}</h3>
      <table>
        <tr><td class="label">{t('first_name', lang)}</td><td>{row['first_name']}</td></tr>
        <tr><td class="label">{t('last_name', lang)}</td><td>{row['last_name']}</td></tr>
        <tr><td class="label">{t('dob', lang)}</td><td>{row['dob'].isoformat()}</td></tr>
        <tr><td class="label">{t('sex', lang)}</td><td>{row['sex_display']}</td></tr>
        <tr><td class="label">{t('email', lang)}</td><td>{row['email']}</td></tr>
        <tr><td class="label">{t('phone', lang)}</td><td>{row['phone']}</td></tr>
        <tr><td class="label">{t('nationality', lang)}</td><td>{row['nationality']}</td></tr>
      </table>
    </div>

    <div class="section box">
      <h3>{t('address', lang)}</h3>
      <table>
        <tr><td class="label">{t('line1', lang)}</td><td>{row['addr_line1']}</td></tr>
        <tr><td class="label">{t('line2', lang)}</td><td>{row['addr_line2'] or ''}</td></tr>
        <tr><td class="label">{t('city', lang)}</td><td>{row['city']}</td></tr>
        <tr><td class="label">{t('state', lang)}</td><td>{row['state']}</td></tr>
        <tr><td class="label">{t('postal', lang)}</td><td>{row['postal']}</td></tr>
        <tr><td class="label">{t('country', lang)}</td><td>{row['country']}</td></tr>
      </table>
    </div>

    <div class="section box">
      <h3>{t('appt', lang)}</h3>
      <table>
        <tr><td class="label">{t('tz', lang)}</td><td>{row['home_tz']}</td></tr>
        <tr><td class="label">{t('pref_lang', lang)}</td><td>{row['pref_lang']}</td></tr>
        <tr><td class="label">{t('visit_reason', lang)}</td><td>{row['reason']}</td></tr>
        <tr><td class="label">{t('date_range', lang)}</td><td>{row['date_from']} → {row['date_to']}</td></tr>
      </table>
    </div>

    <div class="section box">
      <h3>{t('insurance_details', lang)}</h3>
      <table>
        <tr><td class="label">{t('has_ins', lang)}</td><td>{"Yes" if row['has_ins'] else "No"}</td></tr>
        <tr><td class="label">{t('insurer', lang)}</td><td>{row['insurer'] or ''}</td></tr>
        <tr><td class="label">{t('policy', lang)}</td><td>{row['policy'] or ''}</td></tr>
      </table>
    </div>

    <div class="section box">
      <h3>{t('estimates', lang)}</h3>
      <table>
        <tr><td class="label">{t('est_amt', lang)}</td><td>{est}</td></tr>
      </table>
    </div>

    <div class="section muted">{t('gdpr', lang)}</div>
    </body></html>
    """

# -----------------------
# Sidebar: Admin / Settings
# -----------------------
with st.sidebar:
    st.markdown("### ⚙️ " + t("clinic_settings", "en"))
    lang = st.selectbox("Language / Idioma", ["en", "es"], index=0, key="lang")
    st.caption(t("admin_note", lang))
    countries = ["United States", "United Kingdom", "Ireland", "France", "Germany", "Spain", "Italy",
                 "Canada", "Australia", "Japan", "Saudi Arabia", "United Arab Emirates", "Mexico",
                 "Brazil", "India", "Malaysia", "Singapore"]
    clinic_country = st.selectbox(t("clinic_country", lang), countries, index=0)
    currency_iso, currency_symbol = country_to_currency(clinic_country)
    st.text_input(t("default_currency", lang), f"{currency_iso} ({currency_symbol})", disabled=True)

st.title("🌍 " + t("title", lang))

# -----------------------
# Patient form
# -----------------------
left, right = st.columns([1,1])

with left:
    st.subheader("🧍 " + t("patient_info", lang))
    first = st.text_input(t("first_name", lang))
    last = st.text_input(t("last_name", lang))
    dob = st.date_input(t("dob", lang), value=dt.date(1990,1,1), max_value=dt.date.today())
    sex_display = st.selectbox(t("sex", lang), I18N[lang]["sex_opts"])
    # Map to FHIR gender
    sex_map = {"Female":"female","Male":"male","Intersex":"other","Unknown":"unknown","Prefer not to say":"unknown",
               "Femenino":"female","Masculino":"male","Intersexual":"other","Desconocido":"unknown","Prefiero no decir":"unknown"}
    sex_fhir = sex_map.get(sex_display, "unknown")
    email = st.text_input(t("email", lang))
    phone = st.text_input(t("phone", lang))
    nationality = st.text_input(t("nationality", lang))

    st.markdown("**ID & Documents**  \n" + t("doc_note", lang))
    passport = st.file_uploader(t("passport", lang), type=["pdf","png","jpg","jpeg"])
    visa = st.file_uploader(t("visa", lang), type=["pdf","png","jpg","jpeg"])
    insurance_file = st.file_uploader(t("insurance", lang), type=["pdf","png","jpg","jpeg"])
    records = st.file_uploader(t("records", lang), type=["pdf","png","jpg","jpeg"], accept_multiple_files=True)

with right:
    st.subheader("📫 " + t("address", lang))
    addr1 = st.text_input(t("line1", lang))
    addr2 = st.text_input(t("line2", lang))
    city = st.text_input(t("city", lang))
    state = st.text_input(t("state", lang))
    postal = st.text_input(t("postal", lang))
    country = st.text_input(t("country", lang))

    st.subheader("🆘 " + t("emergency", lang))
    em_name = st.text_input(t("em_name", lang))
    em_phone = st.text_input(t("em_phone", lang))
    em_rel = st.text_input(t("em_relationship", lang))

    st.subheader("📅 " + t("appt", lang))
    all_tzs = sorted(tz.gettzdb().zones)
    home_tz = st.selectbox(t("tz", lang), ["UTC","America/New_York","Europe/London","Europe/Madrid","Asia/Singapore","Asia/Kuala_Lumpur","Asia/Dubai","America/Mexico_City"] + all_tzs[:0])
    pref_lang = st.text_input(t("pref_lang", lang), value="English")
    reason = st.text_area(t("visit_reason", lang))
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        date_from = st.date_input(t("date_range", lang) + " — From", value=dt.date.today())
    with col_d2:
        date_to = st.date_input("To", value=dt.date.today() + dt.timedelta(days=14))

    st.subheader("🧾 " + t("insurance_details", lang))
    has_ins = st.checkbox(t("has_ins", lang), value=False)
    insurer = st.text_input(t("insurer", lang)) if has_ins else ""
    policy = st.text_input(t("policy", lang)) if has_ins else ""

    st.subheader("💳 " + t("estimates", lang))
    est_amt = st.number_input(t("est_amt", lang), min_value=0.0, value=0.0, step=10.0, help=f"Shown as {currency_iso}")

st.subheader("🔒 " + t("privacy", lang))
consent = st.checkbox(t("consent", lang))
marketing = st.checkbox(t("marketing", lang), value=False)

# -----------------------
# Submit & validation
# -----------------------
def required_ok():
    req = [first,last,email,phone,addr1,city,state,postal,country,em_name,em_phone,em_rel,reason]
    return all(bool(x) for x in req) and consent

submit = st.button("✅ " + t("submit", lang))

if submit:
    if not required_ok():
        st.error(t("validation", lang))
        st.stop()

    row = {
        "first_name": first, "last_name": last, "dob": dob, "sex_display": sex_display, "sex_fhir": sex_fhir,
        "email": email, "phone": phone, "nationality": nationality,
        "addr_line1": addr1, "addr_line2": addr2, "city": city, "state": state, "postal": postal, "country": country,
        "em_name": em_name, "em_phone": em_phone, "em_relationship": em_rel,
        "home_tz": home_tz, "pref_lang": pref_lang, "reason": reason, "date_from": str(date_from), "date_to": str(date_to),
        "has_ins": has_ins, "insurer": insurer, "policy": policy, "est_amt": est_amt,
        "passport_number": None, "marketing_opt_in": marketing,
    }

    # FHIR Bundle
    fhir_bundle = make_fhir_patient(row)
    fhir_bytes = json.dumps(fhir_bundle, indent=2).encode("utf-8")

    # CSV row
    csv_df = pd.DataFrame([{
        "submitted_utc": dt.datetime.utcnow().isoformat(),
        **{k: (v.isoformat() if isinstance(v, (dt.date, dt.datetime)) else v) for k,v in row.items()},
        "clinic_country": clinic_country, "currency": currency_iso
    }])
    csv_bytes = csv_df.to_csv(index=False).encode("utf-8")

    # HTML "PDF-like" summary for printing/downloading
    html = html_summary(row, currency_iso, currency_symbol, lang)
    html_bytes = html.encode("utf-8")

    # Attachments ZIP (raw uploads)
    uploads = {}
    if passport: uploads[f"passport_{passport.name}"] = passport.getbuffer().tobytes()
    if visa: uploads[f"visa_{visa.name}"] = visa.getbuffer().tobytes()
    if insurance_file: uploads[f"insurance_{insurance_file.name}"] = insurance_file.getbuffer().tobytes()
    for i, f in enumerate(records or []):
        uploads[f"record_{i+1}_{f.name}"] = f.getbuffer().tobytes()
    uploads_zip = bytes_zip(uploads) if uploads else b""

    # Final bundle ZIP
    bundle_parts = {
        "fhir_bundle.json": fhir_bytes,
        "intake_summary.html": html_bytes,
        "intake_row.csv": csv_bytes
    }
    if uploads_zip:
        bundle_parts["uploads.zip"] = uploads_zip
    final_zip = bytes_zip(bundle_parts)

    st.success(t("success", lang))
    st.download_button(
        label="📦 " + t("download_bundle", lang),
        data=final_zip,
        file_name=f"onboarding_{last}_{first}.zip",
        mime="application/zip"
    )

    # Show quick receipt
    st.markdown("#### Receipt")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Patient", f"{first} {last}")
    with col2:
        st.metric("Clinic Country", clinic_country)
    with col3:
        st.metric("Estimate", format_money(est_amt, currency_iso))

    st.caption(t("gdpr", lang))
