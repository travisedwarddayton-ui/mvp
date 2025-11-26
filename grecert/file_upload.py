import streamlit as st
import zipfile
import tempfile
import os
import re
import pymupdf as fitz
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

# Hardcoded for testing — replace with st.secrets in prod
SNOWFLAKE_USER="STREAMLIT_USER"
SNOWFLAKE_ACCOUNT="UILIVGK-NR22639"
SNOWFLAKE_WAREHOUSE="STREAMLIT_WH"
SNOWFLAKE_ROLE="STREAMLIT_ROLE"
SNOWFLAKE_DATABASE="GRECERT_DB"
SNOWFLAKE_SCHEMA="PUBLIC"

PRIVATE_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC0EChas/P4r5iK
TUwMsxw1NKBdXCimfKnm5us87IUAa1phlG8tDM/P5B1t0svQTn/8iApDwWdeXAAT
OxBZl9Qy+zPEdDhYAsCwRG1ZZioEsreGLn1LSaA1yyB4fU5KfjtyHl0xBb04WiNE
W2ZLfklUQ0T3sVtlvE3QUwPMZ2cs6O58owA2qbbg8PF7pu7xUszcWisqv6GlvZv2
5VldmeMRKkpwchignSBArMinvYZLCRfJi/raLSwY6HRKn3HQN4pVkTxUDS7izp/g
/HBbGnLuSpUf/iVP4+4D6Zyq00BeZe4KU+CIphs92TMRV4Nva7AbKLwY0yUKviBQ
WisuL6DDAgMBAAECggEAJBezBw9YIWqNMHey/T6vskiEtoIBEfIeGk8CKxmbxUw/
dxzKNiUByMGIVpmwyeXaSLO6Hv+26RaW20P1EIha/AcXRtMm8hlHJ23n30oXtQ5f
tBFAgyVUbEP1k8FGPq9T2hmVA30Lgy6qMAsEE7DSIQZE3kNaNyfKDy58re2yJDGL
Rh5WEzT2ZtHZ5gWzKmZlgXpqvAHlIMYs5blg2argGTqU53Gwy1lbqb01nosIpsa0
UnCZJkZumQHJNfkS1UvkVJ4WevX7Osb+KarihbA0aur3gzHECmCr9xRpS0h1T8J3
x6TveoXyH4um37x6igISqlSZ//rq+dG899MEoxxxkQKBgQD9+qhTEhK3qfcMGf45
0VRAB5NZ2OKZNgPdoIrPM7Efg2x0xHlI5lUR7KMhYHlSx0h11d0d0DgO+mDMBdzb
K0MnuPMwvtWht2oLdPMSYsKePjNbiSpc+CE94u6+fChqzt0zCJozX0LuiPfEADzL
ti9jZmyMJ1SbEi13kHbOFngLEQKBgQC1fu/d3H6RJwy/AMErr6WIPocvq79ysJMd
ldlTPJzunpNM2SR9Cmbxl38vuetS5z1rjJhBh5VQk+MUXJuE+LfTIi2FfLZEM9sf
4e0qKSBHcs3f6dbi5FmsAxQY4BuHmI+q1uqZDRo9Nnpk73Y0/Z2bpwowpy36Sxnb
TKXheFDmkwKBgQCv2hssEWp2Uq+kaGb3H3JHNzeWUS5sSNMaZCtYVgFAwZ2Zp+QW
Tqz+USuOU58NasBIHoEQQHhgHophGXoXInhIC64OxUNjynwZXKtkwo7gRE8JBQsY
/hD+KZ+Gsq7FbWAJEt65zS6pvJpY0pVFs2pSV7u2uxDAojBrBdLM1Q/fEQKBgFUg
o7spF4hXi4fu/6vQ59A+m8PFR7ewkGA5D8UV0fmuESLjWlT30w8P4szs5C5vXYSb
XjKmOGeh5cmAIkW9LuNtzXIl64uT0vxiSI4U2hoJA/05PdwQBOtESmHcg60W5pPX
2BNPbPY3HjNHiecS6aC/OW1WjJ8wKIGOsuNNPozXAoGBANC8fCa+xgIvMOo2Nozx
JclHGgUy2UHyckWk+tGyq0f3HhHwROgyvCIpPlEtfNLdqt/1R4PHJmPVN/BFkzwi
DPl1W57Dm5MXiAu89YIYKGeX+zXLYzR8vAVwESmTr5cSglq4WHy3QdAo+RAqerUv
0Lyt2WbT0pvwIU1Tvw2ia6JI
-----END PRIVATE KEY-----
"""

def load_private_key_pkcs8():
    # Convert the PKCS1 private key → PKCS8 (required by Snowflake)
    key = serialization.load_pem_private_key(
        PRIVATE_KEY_PEM,
        password=None,
    )
    pkcs8_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return pkcs8_key

def upload_to_snowflake_stage(local_path, stage_path):
    private_key = load_private_key_pkcs8()

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        role=SNOWFLAKE_ROLE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        private_key=private_key
    )

    cs = conn.cursor()
    try:
        cs.execute(f"PUT file://{local_path} @{stage_path} AUTO_COMPRESS=FALSE")
    finally:
        cs.close()
        conn.close()
