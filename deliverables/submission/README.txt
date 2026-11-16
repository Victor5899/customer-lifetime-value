Customer Lifetime Value and Segmentation Engine
Olist Brazilian E-Commerce public dataset

This folder is the guide to the project hand-in. The project files stay in
their original locations. Nothing in this package was zipped by the audit.


1. Project overview

The analysis scores customers who have at least one delivered Olist order.
The cleaned order table has one row for each of 99,441 orders. The customer
tables have one row for each of 93,358 customers. Delivered product revenue
is R$ 13,221,498.11. Freight is not included in that figure.

The CLV score is a 0–100 index:

    0.50 x RFM index + 0.50 x review index

If a customer has no review, the score is the RFM index. It is not a forecast
of future spend and it is not a churn probability.

Segments use fixed thresholds. High Value is 80 and above (13,144 customers).
Medium-High is 60 and above. Medium is 40 and above. Low is below 40.

The Week 7 pulse keeps those 13,144 High Value customers and flags recency
above 170 days. That flag covers 2,051 customers, 15.60 percent. The on-screen
status is Alert. The status text is "Recency watch" or "Within band".


2. How to navigate the package

Start at the project README.md for setup and the execution order.

docs/                      weekly notes, data dictionary, ER diagram, Week 8 audits
notebooks/                 Weeks 1–5, in numbered order
src/                       the Week 6 Tableau extract script
data/raw/                  the nine Olist source files
data/processed/            order, RFM, CLV, distance, and quarterly extracts
data/output/               Week 3–5 tables and charts
data/tableau/              the six Week 6 CSVs, the Week 7 pulse, and the validation log
deliverables/tableau/      the Tableau packaged workbook
deliverables/screenshots/  captures of the Week 6 and Week 7 dashboards
deliverables/submission/   this file

The Week 8 records are:

    docs/week8_end_to_end_qa_report.md
    docs/week8_performance_and_packaging_report.md
    docs/week8_final_package_manifest.md
    docs/ai_use_disclosure.md

data/raw, data/processed, and data/output are on disk in a complete working
copy. They are listed in .gitignore, so a git clone does not include them.
Pack or copy the working directory. Do not rely on git archive.


3. Notebook execution order

Use Python 3.12. From the project root:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

requirements.txt is the recorded environment, including pandas 3.0.5.
Do not include the .venv directory in a hand-in archive.

The notebooks read paths relative to the notebooks directory. Open them from
the project root in Jupyter, or run them with notebooks/ as the working
directory. Run them only when an extract has to be rebuilt. A re-run
overwrites that week's exported CSV.

    1. notebooks/01_week1_data_audit.ipynb
    2. notebooks/02_week2_data_integration.ipynb
    3. notebooks/03_week3_rfm_analysis.ipynb
    4. notebooks/04_week4_clv_analysis.ipynb
    5. notebooks/05_week5_advanced_visualizations.ipynb
    6. python src/prepare_week6_tableau_sources.py

The Week 6 script can be run from the project root. It rewrites the Tableau
CSVs and does not modify the Week 2–5 source files. There is no separate
script for the Week 7 pulse. Its rule is documented in
docs/week7_pulse_metric_implementation.md.


4. Tableau workbook and screenshots

Workbook:

    deliverables/tableau/Customer_Lifetime_Value_and_Segmentation.twbx

It contains two dashboards: Customer Intelligence Dashboard, and High-Value
Segment Churn Risk Pulse. The packaged file includes Tableau Hyper extracts
for the Week 6 and Week 7 sources. The workbook XML also stores this
machine's absolute path to data/tableau. Opening the embedded extracts does
not require that path. Refreshing the text files on another computer would.

Screenshots:

    deliverables/screenshots/week6_customer_intelligence_dashboard.png
    deliverables/screenshots/week7_high_value_risk_pulse.png

Both are Tableau Desktop captures, so the application sidebar is visible.
The Week 6 funnel shows 99,441 orders placed. The Total Orders tile on that
same capture shows 96,683, which is the order count after the 2,758 orders
without a CLV segment. Those are different counts, and both can be read off
the screenshot.


5. Known limitations

These limits are part of the submitted method. They are argued in
docs/week4_methodology.md, docs/week6_leadership_findings.md,
docs/week7_alert_rule_and_campaign_escalation.md, and the two Week 8 reports.

- The geolocation lookup uses the median of points inside the documented
  Brazil box. Exact duplicate geolocation rows are kept. Removing them would
  move many distances. CLV does not use the coordinate.
- Some shipments have no distance because a ZIP prefix does not match an
  in-box coordinate. Delay averages are for delivered shipments.
- The quarterly line is exploratory. It is not an operating forecast and it
  is not a monetary lifetime value.
- The 2018 quarter-3 snapshot refits its own quintiles. Do not quote that
  snapshot in place of the baseline High Value count of 13,144.
- Frequency score 1 covers customers with one delivered order and customers
  with two. The one-order share is 97.0 percent, not 99.76 percent.
- One delivered order has no payment row. It stays in delivered revenue and
  stays out of funnel stage 3.
- review_id is not unique. The CLV review grain is the order mean, then the
  customer mean.
- No campaign result has been measured. The marketing notes are tests, not
  estimated effects.
- The pulse is a recency watch on a historical snapshot. The Olist files used
  here have no verified churn label.


6. AI-use disclosure

Read docs/ai_use_disclosure.md.

Cursor's coding agent drafted and revised code, validation checks, and
documentation, including the Week 8 reports. The published counts were
recomputed from the files in data/. The person submitting the project is
responsible for the figures, the definitions, and what is said about them.
