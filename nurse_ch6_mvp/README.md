
# Data → Wisdom: Interactive Learning Lab (Streamlit)

This Streamlit app turns Chapter 6 (*Data and Data Processing*) into a hands-on, interactive learning experience:
- **DIKW** continuum explainer with a mini activity.
- **Big Data (6 Vs)** and **Data States** overview.
- **Drag-and-drop CSV** playground (descriptive analytics + data quality + SQL sandbox).
- **DBMS models** and **storage options** (warehouse, mart, lake).
- **KPI dashboard** demo with quick grouping/aggregation.
- **KDD** mini demo (rule-based classifier).
- **Auto‑graded quiz** from end-of-chapter concepts.

## Run locally

```bash
pip install streamlit pandas numpy
streamlit run app.py
```

> Optional: The app uses only standard libraries. No external custom components required.

### Files
- `app.py` — the Streamlit app
- `ER_admissions.csv` — small sample dataset for the playground
