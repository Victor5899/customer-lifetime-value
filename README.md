# Customer Lifetime Value and Segmentation Engine

Analysis of the Olist Brazilian E-Commerce public dataset. The work covers an order-level extract, customer RFM, a 0–100 CLV score, segment profiles, Tableau extracts, and a Week 7 recency pulse.

The checked results are:

- 99,441 orders in the cleaned extract, one row per `order_id`.
- 96,478 delivered orders and 93,358 scored customers.
- Delivered product revenue of R$ 13,221,498.11. Freight is not included.
- CLV score = 0.50 × RFM index + 0.50 × review index. A customer with no review keeps the RFM index.
- Segments: High Value at 80 and above (13,144), Medium-High at 60, Medium at 40, Low below 40.
- Week 7 pulse: High Value customers with `recency_days > 170`. That flags 2,051 customers, 15.60%.

These definitions are fixed. Later notebooks and the Tableau script read the saved files. They do not refit the score.

## Setup

Use Python 3.12. From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` is the environment used to produce the notebooks, including pandas 3.0.5. The virtual environment stays local. Do not put `.venv/` in a submission archive.

The notebooks use paths relative to `notebooks/`. Start Jupyter from the project root and open the files in `notebooks/`, or run them with that folder as the working directory. `src/prepare_week6_tableau_sources.py` finds the project root from its own location, so it can be run from the root.

## Data

The nine Olist source files belong in `data/raw/`. The processed extracts belong in `data/processed/`, and the Week 3–5 outputs belong in `data/output/`. Those three folders are listed in `.gitignore`. They are present in a complete working copy, and they are absent from a fresh `git clone` or `git archive`. A submission zip has to be made from the working directory, not from Git alone.

Public source: the Olist Brazilian E-Commerce dataset published by Olist on Kaggle (`olistbr/brazilian-ecommerce`). The copy used here is the nine CSV files already stored under `data/raw/`.

## Execution order

Run these only when the saved extracts need to be rebuilt. Re-running a notebook overwrites its exported CSV.

1. `notebooks/01_week1_data_audit.ipynb` reads the nine raw tables and does not write an extract.
2. `notebooks/02_week2_data_integration.ipynb` writes `data/processed/olist_order_level_cleaned.csv`.
3. `notebooks/03_week3_rfm_analysis.ipynb` writes the RFM file and `data/processed/olist_order_distance_analysis.csv`.
4. `notebooks/04_week4_clv_analysis.ipynb` writes the CLV file, the quarterly snapshot, and the forecast tables.
5. `notebooks/05_week5_advanced_visualizations.ipynb` writes the segment, funnel, and state-month summaries.
6. `python src/prepare_week6_tableau_sources.py` writes the six Week 6 Tableau CSVs and refreshes `data/tableau/validation_checks.csv`. It does not modify the Week 2–5 source files.

The Week 7 pulse file is `data/tableau/week7_high_value_risk_pulse.csv`. The rule is documented in `docs/week7_pulse_metric_implementation.md`. There is no separate generator script.

## Documentation

Weekly notes, the data dictionary, the ER diagram, the Week 4 mid-project deck, and the Week 8 QA and performance reports are in `docs/`. `docs/ai_use_disclosure.md` states how the coding agent was used.

The geolocation median keeps duplicate ZIP rows and drops 42 points outside the documented Brazil box. The quarterly forecast is an exploratory line on six complete quarters. Those limitations stay in the Week 3, Week 4, and Week 8 notes.
