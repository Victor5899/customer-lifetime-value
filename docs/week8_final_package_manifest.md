# Week 8 — Final Package Manifest

**Project:** Customer Lifetime Value and Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce public dataset
**Date:** 16 November 2026
**Scope:** Inventory of the working directory after the Tableau workbook and dashboard screenshots were added. No existing file was modified or deleted. No commit, push, or zip was made. The executive summary and final presentation are R3 and are not part of this package.

The expected workbook name in the request was `Customer_Intelligence_and_Risk_Pulse.twbx`. The file on disk is `Customer_Lifetime_Value_and_Segmentation.twbx`. The screenshot names match the request.

## 1. Readiness

R2 can be declared complete for the on-disk package.

The workbook opens as a valid `.twbx`, contains both dashboards, and embeds the Week 6 and Week 7 data. Both screenshots open and show those dashboards with the locked figures. The nine source tables, the processed extracts, the nine `data/tableau/` files, the notebooks, the Week 6 script, the Week 4–8 notes, the README, and the AI disclosure are in the working directory.

There is no remaining R2 blocker. Two conditions still govern how the folder is handed in:

- Do not submit by cloning or pulling `origin/main`. That branch is at `b6338d0` and does not contain the Week 8 reports, this manifest, the workbook, or the screenshots. `data/raw/`, `data/processed/`, and `data/output/` are gitignored, so they would be missing as well. No commit or push was made.
- Do not zip `.venv/` (512 MB), `src/__pycache__/`, `.git/`, or the `.DS_Store` files. A zip was not created in this pass.

The executive summary and the final presentation are absent on purpose. They belong to R3.

## 2. Tableau workbook

| Check | Result |
| --- | --- |
| Path | `deliverables/tableau/Customer_Lifetime_Value_and_Segmentation.twbx` |
| Size | 11,260,865 bytes (11 MB) |
| Format | Zip archive, deflate compression. `unzip -t` reported no errors |
| Contents | 6 members, 19,872,546 bytes uncompressed |
| Workbook | `Customer_Lifetime_Value_and_Segmentation.twb`, 277,282 bytes, XML workbook version 18.1 |
| Tableau build stored in the file | `source-build` 2026.2.3 (20262.26.0912.1023). The file comment also records build 20263.26.1103.1048 |

Embedded extracts, all under `Data/tableau-temp/`:

| Embedded file | Uncompressed size | Workbook connection |
| --- | ---: | --- |
| `#TableauTemp_0ep1arh01lrbvs1e75aaw1czcjts.hyper` | 18,743,296 | `tableau_customer_clv+`, the relationship of `tableau_customer_clv.csv`, `tableau_orders.csv`, and `tableau_shipments.csv` |
| `#TableauTemp_0p1n74e18djk0l1ec0uhm09dnbhr.hyper` | 655,360 | `week7_high_value_risk_pulse.csv` |
| `#TableauTemp_0s6lv3b00ap9x6131u0k217pjnwp.hyper` | 65,536 | `tableau_segment_profile.csv` |
| `#TableauTemp_1s5j1k716s2fy916xo7mx1uc8pmf.hyper` | 65,536 | `tableau_state_month.csv` |
| `#TableauTemp_0qj938j0g9od5z1b5pe9l12il8r8.hyper` | 65,536 | `tableau_funnel.csv` |

The workbook XML names these seven CSV sources: `tableau_customer_clv.csv`, `tableau_orders.csv`, `tableau_shipments.csv`, `tableau_segment_profile.csv`, `tableau_funnel.csv`, `tableau_state_month.csv`, and `week7_high_value_risk_pulse.csv`. Orders, shipments, and the customer file share one Hyper extract. The smaller extracts are stored at Tableau's 65,536-byte allocation. No CSV is stored loose inside the `.twbx`. The data travels inside the five Hyper files.

Dashboards in the workbook:

| Dashboard | Sheets placed on it |
| --- | --- |
| Customer Intelligence Dashboard | KPI — Total Revenue, Total Customers, Average CLV, Delivered Orders, Total Orders, Average Order Value; Customer Segment Revenue Treemap; Customer Segment Profile; State-Month Order Heatmap; Monthly Orders & Revenue Trend; Order Conversion Funnel; Delivery Distance vs Delay |
| High-Value Segment Churn Risk Pulse | Pulse KPI Overview; Pulse Alert Status; High Value Customers on Recency Watch |

Those are the Week 6 and Week 7 dashboards. The workbook has 15 worksheets, and each one is on one of those two dashboards. There is no third dashboard.

Portability note, not a missing file: five connection entries still record the absolute directory `/Users/victo/Documents/CODING/PythonProjects/customer-lifetime-value/data/tableau`. A refresh on another machine would look for that path. Opening the packaged extracts does not require that directory, because the Hyper files are inside the `.twbx`.

## 3. Screenshots

Both files are PNG, 2940 by 1912 pixels, RGBA, and both opened.

| File | Bytes | MD5 | What is on the screen |
| --- | ---: | --- | --- |
| `deliverables/screenshots/week6_customer_intelligence_dashboard.png` | 626,585 | `ecfecf064da0c6c9dfeb3158faece986` | Customer Intelligence Dashboard. Revenue R$ 13,221,498.11, customers 93,358, average CLV 62.58, delivered 96,478. Segment counts 13,144, 52,727, 15,220, and 12,267. Funnel 99,441, 99,440, 96,477, and 95,831 |
| `deliverables/screenshots/week7_high_value_risk_pulse.png` | 626,499 | `c0ab3589c5f30c0f8d99902f18a5ce01` | Pulse KPI Overview and Pulse Alert Status. Flagged 2,051, High Value 13,144, risk 15.60%, status Alert |

The two files are not copies of each other. Both are Tableau Desktop authoring captures: the sheet list and sidebar are visible. They are evidence that the dashboards were built. They are not cropped presentation slides.

On the Week 6 capture, the Total Orders tile reads 96,683. That is 99,441 minus the 2,758 orders that have no CLV segment. The funnel on the same capture still starts at 99,441. The tile and the funnel are counting different sets. The published order grain remains 99,441.

## 4. Documentation

| Week | File | Bytes | Status |
| --- | --- | ---: | --- |
| 1 | `docs/data_dictionary/data_charter.md` | 8,014 | Present. This is the Week 1 charter, not a file named `week1` |
| 1 | `docs/data_dictionary/data_dictionary.md` | 13,333 | Present |
| 1 | `docs/er_diagram/olist_er_diagram.drawio` | 14,869 | Present |
| 1 | `docs/er_diagram/olist_er_diagram.png` | 406,254 | Present |
| 2 | — | — | No `docs/week2` file. The written record is `notebooks/02_week2_data_integration.ipynb` |
| 3 | — | — | No `docs/week3` file. The written record is `notebooks/03_week3_rfm_analysis.ipynb` and the Week 3 files in `data/output/` |
| 4 | `docs/week4_methodology.md` | 10,702 | Present |
| 4 | `docs/week4_mid_project_deck.pptx` | 41,129 | Present. Mid-project deck, not the final presentation |
| 5 | `docs/week5_marketing_personas.md` | 8,062 | Present |
| 6 | `docs/week6_leadership_findings.md` | 17,112 | Present |
| 6 | `docs/week6_tableau_data_dictionary.md` | 19,191 | Present |
| 6 | `docs/week6_tableau_implementation_guide.md` | 31,925 | Present |
| 6 | `docs/week6_tableau_validation.md` | 12,981 | Present |
| 7 | `docs/week7_alert_rule_and_campaign_escalation.md` | 9,472 | Present |
| 7 | `docs/week7_manual_clv_qa.md` | 11,868 | Present |
| 7 | `docs/week7_pulse_metric_implementation.md` | 10,618 | Present |
| 7 | `docs/week7_validation_log.md` | 4,981 | Present |
| 8 | `docs/week8_end_to_end_qa_report.md` | 32,962 | Present. Untracked |
| 8 | `docs/week8_performance_and_packaging_report.md` | 21,716 | Present. Untracked |
| 8 | `docs/ai_use_disclosure.md` | 1,254 | Present. Untracked |
| 8 | `docs/week8_final_package_manifest.md` | this file | Created by this audit. Untracked |
| — | `README.md` | 3,601 | Present. Modified and uncommitted |
| — | `deliverables/submission/README.txt` | created with this audit | Package guide |

No file named `docs/week1*`, `docs/week2*`, or `docs/week3*` exists. The Week 1 charter, dictionary, and ER diagram do exist. Weeks 2 and 3 were not given a separate note outside the notebooks. That is the project as built. It does not remove an R2 artifact that this audit was asked to add.

## 5. Notebooks and scripts

| Path | Bytes |
| --- | ---: |
| `notebooks/01_week1_data_audit.ipynb` | 251,712 |
| `notebooks/02_week2_data_integration.ipynb` | 335,027 |
| `notebooks/03_week3_rfm_analysis.ipynb` | 1,302,987 |
| `notebooks/04_week4_clv_analysis.ipynb` | 6,297,392 |
| `notebooks/05_week5_advanced_visualizations.ipynb` | 5,185,346 |
| `src/prepare_week6_tableau_sources.py` | 33,622 |
| `requirements.txt` | 2,058 |
| `.gitignore` | 515 |

There is no Week 7 generator script. The pulse rule is in `docs/week7_pulse_metric_implementation.md`, and the extract is `data/tableau/week7_high_value_risk_pulse.csv`. `sql/` and `dashboard/` exist and are empty.

## 6. Source data and reproduction

All nine Olist files are on disk in `data/raw/`. Git ignores that directory (`.gitignore` lines 41–43 also ignore `data/processed/` and `data/output/`). A clone does not reproduce the results until those directories are restored. The public source is the Olist Brazilian E-Commerce dataset (`olistbr/brazilian-ecommerce`). Row counts below are CSV records, not physical line counts. The reviews file contains line breaks inside comments, so `wc -l` overstates it.

| File | Rows | Bytes |
| --- | ---: | ---: |
| `olist_customers_dataset.csv` | 99,441 | 9,033,957 |
| `olist_geolocation_dataset.csv` | 1,000,163 | 61,273,883 |
| `olist_order_items_dataset.csv` | 112,650 | 15,438,671 |
| `olist_order_payments_dataset.csv` | 103,886 | 5,777,138 |
| `olist_order_reviews_dataset.csv` | 99,224 | 14,451,670 |
| `olist_orders_dataset.csv` | 99,441 | 17,654,914 |
| `olist_products_dataset.csv` | 32,951 | 2,379,446 |
| `olist_sellers_dataset.csv` | 3,095 | 174,703 |
| `product_category_name_translation.csv` | 71 | 2,613 |

Processed extracts, also gitignored:

| File | Rows | Bytes |
| --- | ---: | ---: |
| `data/processed/olist_order_level_cleaned.csv` | 99,441 | 27,762,447 |
| `data/processed/olist_customer_rfm.csv` | 93,358 | 8,535,654 |
| `data/processed/olist_customer_clv.csv` | 93,358 | 10,881,278 |
| `data/processed/olist_order_distance_analysis.csv` | 112,650 | 33,586,097 |
| `data/processed/olist_quarterly_customer_segments.csv` | 324,219 | 38,606,124 |

Week 3–5 outputs in `data/output/` are present and gitignored: three summary CSVs for Week 3, five Week 4 tables, three Week 5 tables, four Plotly HTML charts, the dashboard wireframe HTML, and `week5_dashboard_wireframe.png` (451,784 bytes). The four Plotly HTML files are 4.6–5.0 MB each because each one embeds the Plotly library. They are the chart outputs, not a second copy of the customer table.

Reproduction order is in `README.md`. Notebooks must be run with `notebooks/` as the working directory. `src/prepare_week6_tableau_sources.py` locates the project from its own path. Re-running Weeks 2–5 overwrites the extracts. Python 3.12 and `requirements.txt` are the recorded environment. Pandas in that file is 3.0.5.

## 7. Tableau CSV directory

All nine files are present. These, unlike the raw and processed data, are tracked by Git.

| File | Rows | Bytes |
| --- | ---: | ---: |
| `data/tableau/tableau_customer_clv.csv` | 93,358 | 8,969,235 |
| `data/tableau/tableau_orders.csv` | 99,441 | 14,969,486 |
| `data/tableau/tableau_shipments.csv` | 112,650 | 8,995,894 |
| `data/tableau/tableau_state_month.csv` | 675 | 24,509 |
| `data/tableau/tableau_funnel.csv` | 4 | 351 |
| `data/tableau/tableau_segment_profile.csv` | 4 | 794 |
| `data/tableau/week7_high_value_risk_pulse.csv` | 13,144 | 1,471,532 |
| `data/tableau/validation_checks.csv` | 28 checks | 2,891 |
| `data/tableau/validation_summary.json` | — | 4,681 |

The Week 7 pulse is the seventh file in that list. The same grains are embedded in the `.twbx`.

## 8. What to leave out of a zip

| Item | Evidence | Action |
| --- | --- | --- |
| `.venv/` | Present, 512 MB | Exclude. It is gitignored |
| `src/__pycache__/prepare_week6_tableau_sources.cpython-312.pyc` | Present, about 40 KB | Exclude. It is gitignored |
| `.DS_Store` | Project root, `docs/`, `data/`, `deliverables/`, and `deliverables/screenshots/` | Exclude |
| `.git/` | Present. Branch `main`, aligned with `origin/main` at `b6338d0` | Exclude from a folder hand-in |
| Secrets | No `.env`, `.pem`, key, or credential file outside `.venv` | None found |
| `sql/`, `dashboard/` | Empty placeholders | Harmless. They contain no script |

The Tableau CSVs and the Hyper extracts inside the workbook describe the same grains. Both stay. One is the reproducible text extract. The other is what Tableau packaged. The quarterly snapshot is not a duplicate of the CLV file. It is the customer-quarter grain.

## 9. Git status

Inspected on `main`, tracking `origin/main`, HEAD `b6338d0` (`Completed Week 7 CLV QA and simulated churn risk pulse`). The branch is not ahead of the remote. Nothing was staged, committed, or pushed.

Modified and uncommitted:

- `README.md` (54 lines changed in the diff stat)
- `notebooks/03_week3_rfm_analysis.ipynb`
- `src/prepare_week6_tableau_sources.py`

Untracked at inspection, before this manifest and the submission README were added:

- `deliverables/`
- `docs/ai_use_disclosure.md`
- `docs/week8_end_to_end_qa_report.md`
- `docs/week8_performance_and_packaging_report.md`

This audit then added `docs/week8_final_package_manifest.md` and `deliverables/submission/README.txt`. Both are untracked. Ignored and therefore absent from Git: `data/raw/`, `data/processed/`, `data/output/`, `.venv/`, and the cache and `.DS_Store` files.

## 10. Package inventory

Working files outside `.venv` and `.git`, before this audit's two new files: 75 files, 331,728,313 bytes. About 291 MB of that is `data/`. The workbook and screenshots add 11.95 MB under `deliverables/`.

```text
customer-lifetime-value/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/                         5 notebooks, Weeks 1–5
├── src/prepare_week6_tableau_sources.py
├── data/raw/                          9 Olist CSVs, gitignored
├── data/processed/                    5 extracts, gitignored
├── data/output/                       Week 3–5 tables and charts, gitignored
├── data/tableau/                      9 files, tracked
├── docs/                              Weeks 1, 4–8 notes, dictionary, ER diagram
├── deliverables/
│   ├── tableau/Customer_Lifetime_Value_and_Segmentation.twbx
│   ├── screenshots/week6_customer_intelligence_dashboard.png
│   ├── screenshots/week7_high_value_risk_pulse.png
│   └── submission/README.txt
├── sql/                               empty
└── dashboard/                         empty
```

## 11. Missing evidence

| Item | State |
| --- | --- |
| `.twbx` workbook | Present, under a different file name from the example in the request |
| Week 6 screenshot | Present and opened |
| Week 7 screenshot | Present and opened |
| Week 6 and Week 7 dashboards inside the workbook | Both present |
| Nine source tables and processed extracts | Present on disk, absent from Git |
| Nine `data/tableau/` files, including the pulse | Present |
| Week 8 QA report, performance report, AI disclosure, README | Present |
| `docs/week2` and `docs/week3` as separate notes | Not created. Notebooks and outputs are the record |
| Executive summary | Not created. R3 |
| Final presentation | Not created. R3. The Week 4 deck is the mid-project deck |
| Zip archive | Not created |
| Commit of the Week 8 and deliverable files | Not made |
