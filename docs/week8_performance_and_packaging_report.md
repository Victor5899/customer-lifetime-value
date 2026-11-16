# Week 8 — Performance and Packaging Report

**Project:** Customer Lifetime Value and Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce public dataset
**Requirement:** R2, performance optimization and final package preparation
**Date:** 16 November 2026
**Runtime used for the timings:** Python 3.12.14, pandas 3.0.5, NumPy 2.5.2, on this machine

R1 is the join and formula audit in `docs/week8_end_to_end_qa_report.md`. This report does not reopen those definitions. It measures where time and memory go, changes only the two paths that had a measured and checkable gain, and records what a submission folder still lacks.

The full notebooks were not re-executed. Re-running Weeks 2–5 would overwrite the exported extracts. The heavy operations were timed on the complete files in isolation. The Week 6 script was re-run in full, because it is the export path and it checks that it does not modify the Week 2–5 files.

## 1. Repository audit

The working tree holds the analysis. Git does not. `git ls-files` tracks 33 files: the notebooks, `src/prepare_week6_tableau_sources.py`, the docs that were already committed, `requirements.txt`, and the nine files under `data/tableau/`. `.gitignore` excludes `data/raw/`, `data/processed/`, and `data/output/`. A clone or `git archive` therefore has the Tableau CSVs and does not have the nine source tables, the order extract, the RFM or CLV files, the distance file, or the Week 3–5 outputs. Those files are on disk in this working copy. A submission has to be packed from the working directory.

| Location | What is there | Size |
| --- | --- | ---: |
| `data/raw/` | All 9 Olist tables | 120 MB |
| `data/processed/` | Order extract, RFM, CLV, distance, quarterly snapshot | 114 MB |
| `data/output/` | Week 3–5 tables, Plotly HTML, wireframe | 24 MB |
| `data/tableau/` | Six Week 6 CSVs, Week 7 pulse, validation log | 33 MB |
| `notebooks/` | Weeks 1–5 | 13 MB |
| `docs/` | Weekly notes, ER diagram, mid-project deck, Week 8 reports | under 1 MB |
| `src/` | `prepare_week6_tableau_sources.py` only | 32 KB |
| `.venv/` | Local environment | 512 MB |
| `sql/`, `dashboard/` | Empty directories | 0 |

No `.twb` or `.twbx` file is in the project. No executive summary and no final presentation are in the project. `docs/week4_mid_project_deck.pptx` is the mid-project deck. There is no second script that builds the Week 7 pulse. The pulse CSV is present, and the rule is in `docs/week7_pulse_metric_implementation.md`.

The largest single objects are the geolocation table (1,000,163 rows, 58.4 MB on disk, 129.4 MB once loaded), the quarterly snapshot (324,219 customer-quarter rows, 36.8 MB on disk, 91.9 MB loaded), and the distance file (112,650 rows, 32.0 MB on disk, 72.0 MB loaded). The loaded size is larger than the file because customer identifiers and other text columns are Python strings.

The six Week 6 extracts are already one file per grain. `tableau_orders.csv` is 14.3 MB and 14 columns. `tableau_shipments.csv` is 8.6 MB and 7 columns, against 19 columns in the distance file. `tableau_customer_clv.csv` is 8.6 MB and 10 columns. Those sizes are usable in Tableau Public. Nothing in them is a repeated join of shipments onto revenue. The quarterly snapshot is not a duplicate of the CLV file. It is one row per customer per snapshot quarter, and `docs/week4_methodology.md` cites it. The Plotly HTML files are a separate size issue, covered in section 2.

`__pycache__/build_week4_notebook.cpython-312.pyc` was a cache for a script that is no longer in `src/`. That cache was removed. No source file was removed.

## 2. Measured performance bottlenecks

Timings below are wall-clock seconds from `time.perf_counter` on the complete data, without an allocation tracer. Memory for a frame is `DataFrame.memory_usage(deep=True)`. Peak memory for the Week 6 script is the process RSS sampled while the script ran. One earlier pass wrapped the ZIP-prefix mode in `tracemalloc` and timed it at about 1.5 seconds. That figure is not used. The tracer penalises the Python callback, and the uninstrumented repeats below are the measurement.

### File reads and frame memory

Each major CSV loaded in well under a second. The cost is memory, not parse time.

| File | Disk | Read | Loaded |
| --- | ---: | ---: | ---: |
| `olist_geolocation_dataset.csv` | 58.4 MB | 0.202 s | 129.4 MB |
| `olist_order_level_cleaned.csv` | 26.5 MB | 0.167 s | 84.4 MB |
| `olist_order_distance_analysis.csv` | 32.0 MB | 0.159 s | 72.0 MB |
| `olist_quarterly_customer_segments.csv` | 36.8 MB | 0.174 s | 91.9 MB |
| `olist_orders_dataset.csv` | 16.8 MB | 0.181 s | 52.9 MB |
| `tableau_orders.csv` | 14.3 MB | 0.120 s | 48.9 MB |

Inside the geolocation frame, `geolocation_city` is 57.8 MB and `geolocation_state` is 48.6 MB. Both are short strings stored as Python objects. Latitude, longitude, and the ZIP prefix are about 7.6 MB each. The city column is not used by the distance, the state-centroid median, RFM, or CLV.

### Operations that were timed because they looked expensive

| Operation | Data | Time | Result |
| --- | --- | ---: | --- |
| Week 2 item aggregation | 112,650 items | 0.033 s | 98,666 orders |
| Week 2 payment aggregation, including the primary type | 103,886 payments | 0.113 s | 99,440 orders |
| Week 2 customer, item, and payment joins | 99,441 orders | 0.037 s | row count unchanged |
| Nine quarterly snapshot cores: filter, group-by, quintile, review filter | up to 96,478 delivered orders | 0.494 s | nine cutoffs, ending at 93,358 customers |
| ZIP-prefix median plus `Series.mode().iat[0]` | 1,000,121 in-box geolocation rows, 19,010 prefixes | 0.429 s median of 5 runs (0.426–0.438) | the published lookup rule |
| Same mode on the frame after dropping the city column | same rows | 0.427 s median | dropping the city does not speed the mode |
| Reading the distance file with all 19 columns | 112,650 rows | 0.159 s | 72.0 MB |
| Reading the 7 distance columns the Tableau script uses | 112,650 rows | 0.078 s | the written shipment extract does not use the other 12 |
| Reading the order extract with all 24 columns | 99,441 rows | 0.167 s | 84.4 MB |
| Reading the 10 order columns the Tableau script uses | 99,441 rows | 0.095 s | the written order extract does not use the other 14 |
| MD5 of the nine protected Week 2–5 files | processed and output CSVs | 0.134 s | integrity check |
| Week 6 script, before the column cut | full export and 28 checks | 2.336 s, peak RSS 445.8 MB | 28 checks passed |
| Copy of every in-box geolocation column | 1,000,121 × 5 | 0.034 s | 137.0 MB working frame |

The slowest measured calculation is the per-prefix mode. It is still under half a second. The quarterly loop, which is the largest piece of Week 4 arithmetic, is about half a second for the data work. Joins do not dominate. There is no multi-minute step in the paths that were timed.

The Week 6 script's peak of 446 MB comes from holding the full order extract and the full distance file, then reading the CSVs it has just written so the checks see the bytes on disk. The second read is the validation. It was left in place.

### Code review, not a measured bottleneck

These were inspected and were not changed.

- Week 1's delay label uses `Series.apply` on 99,441 rows. A traced comparison put that apply at 0.092 seconds and a vectorised version at 0.037 seconds, with no label disagreements. That is not a reason to edit the audit notebook.
- Week 3's flow map uses `iterrows` on the top 40 state pairs. The loop is small.
- Week 1's `apply` on the relationship table is a handful of rows.
- Each notebook reads its inputs again. Those reads are the sub-second loads above. A shared cache or a database would be a new runtime for a gain of less than a second per notebook.
- Four Plotly HTML files embed the Plotly library: `week3_distance_delivery_delay.html` (5.00 MB), `week3_state_distance_map.html` (4.62 MB), and the three Week 5 charts at about 4.60 MB each. Together with the 12 KB wireframe they are almost the whole 24 MB output folder. Pointing them at a shared or CDN copy of Plotly would shrink the folder and would also change finished offline charts. They were left as exported.
- The Tableau numeric columns are already short in the CSV text. The first 5,000 order product values had a mean width under 5 characters. Rewriting them with a fixed number of decimals would change the files that currently reconcile to R$ 13,221,498.11.

## 3. Optimizations implemented

Two changes were made. Both keep the same grain, the same formulas, and the same output schemas.

### ZIP-prefix lookup in Week 3

**Existing implementation.** `notebooks/03_week3_rfm_analysis.ipynb` copied every in-box geolocation column, including the unused city string, and computed `geo_modal_state` with `lambda s: s.mode().iat[0]` inside the group-by. The median of latitude and longitude was already a normal group-by. The bounding box is still latitude −34 to 5.5 and longitude −74.5 to −34. Duplicate geolocation rows are still kept. That is the documented rule, including the sensitivity in R1 check C25.

**Change.** The working frame keeps the ZIP prefix, latitude, longitude, and state. The modal state is the most frequent state for the prefix. A tie keeps the ascending label, which is the same choice as the first value from `Series.mode()`. The median is unchanged. The later state-centroid median still reads latitude, longitude, and state from that working frame.

**Measured benefit.** The lookup median fell from 0.429 seconds to 0.050 seconds across five runs (0.050–0.052). The working frame fell from 137.0 MB to 79.2 MB. Running the old mode on the narrower frame still took 0.427 seconds, so the time change is the mode and the memory change is the dropped city column.

**Risk.** A different tie break, or a different set of rows, would move `geo_modal_state` and could move a centroid. The median coordinates are the distance input. A change there would move `distance_km`.

**Validation.** On all 19,010 prefixes, latitude and longitude differed by 0, and the modal state had 0 disagreements. State centroids differed by 0. Rebuilding the Haversine distances from the new lookup and comparing them with `olist_order_distance_analysis.csv` gave 112,650 aligned shipment keys, 112,095 distances on both sides, a maximum absolute difference of 4.55e-13, and no difference above 1e-6. The 555 missing distances were missing on both sides. That noise is the same floor R1 reported for the original distance rebuild (4.5e-13). The distance file was not rewritten.

The notebook cell was not executed inside Jupyter. Its saved preview still shows prefixes 1001–1005, which the identical lookup still produces. A later full run of the notebook will export the distance file again. The comparison above is the check that this cell does not move those distances.

### Column selection in the Week 6 script

**Existing implementation.** `src/prepare_week6_tableau_sources.py` read all 24 order-extract columns, all 16 CLV columns, and all 19 distance columns, then wrote 14, 10, and 7 columns.

**Change.** Each `read_csv` now requests the columns the script checks or writes. The files on disk are not narrowed. The written Tableau schemas are not narrowed.

**Measured benefit.** One run of the previous script took 2.336 seconds and peaked at 445.8 MB. One run of the revised script, in a fresh process, took 2.151 seconds and peaked at 371.2 MB. The isolated reads of the order and distance files dropped from 0.167 and 0.159 seconds to 0.095 and 0.078 seconds. This is a memory cut of about 75 MB on a script that already finished in a little over two seconds. It is not a change to the extracts.

**Risk.** Omitting a column the checks still use would make the script fail, or would change a written value.

**Validation.** The revised script passed all 28 of its own checks. MD5 of all nine files in `data/tableau/`, including the Week 7 pulse and the validation log, matched the copies taken before the edit. Week 2–5 source hashes were unchanged, which is also one of those 28 checks.

### Considered and not implemented

| Proposal | Why it was left |
| --- | --- |
| Rewrite Weeks 1, 2, 4, or 5 | The timed joins, aggregations, and nine snapshot cores are each under half a second. A rewrite could move a score or a forecast for no measured gain. |
| Vectorise the Week 1 delay labels | The traced apply was already under a tenth of a second. |
| Store the hot files as Parquet, or load them into a database | CSV reads are already under 0.3 seconds a file. A second format would be a new dependency and a second copy of the data. |
| Drop or compress `olist_quarterly_customer_segments.csv` | It is the 324,219-row snapshot grain named in the Week 4 methodology. The aggregate trend file does not replace it. |
| Deduplicate the Plotly library inside the HTML exports | It would shrink about 23 MB of charts and would change files that are already the Week 3 and Week 5 visual outputs. |
| Round Tableau money columns | The current files reconcile to the cent. A format change would break the byte comparison used in this report. |
| Remove the Week 6 reload of the files it just wrote | That reload is what the 28 checks read. The script is 2.2 seconds with it included. |

## 4. Before and after

| Path | Before | After | Outputs |
| --- | --- | --- | --- |
| ZIP-prefix lookup | 0.429 s median, 137.0 MB working frame | 0.050 s median, 79.2 MB working frame | 19,010 prefixes identical. Distances within 4.55e-13 of the stored file |
| Week 6 script | 2.336 s, peak RSS 445.8 MB | 2.151 s, peak RSS 371.2 MB | all 9 Tableau-directory files byte-identical, 28 checks passed |

The Week 6 pair is one run on each side, not a five-run median. A tenth of a second either way would not change the conclusion: the script was already short, and the useful change is the unused columns leaving memory.

No other exported CSV, HTML file, or notebook output was regenerated.

## 5. Regression test results

The stored extracts were read again after the edits. Nothing in this section was accepted from the Week 6 log alone. The distance and lookup checks recompute from `data/raw/olist_geolocation_dataset.csv`.

| Check | Result |
| --- | --- |
| Cleaned orders | 99,441 rows, `order_id` unique |
| Delivered orders | 96,478 |
| Delivered product revenue | R$ 13,221,498.11 |
| RFM and CLV customers | 93,358 each, same `customer_unique_id` set |
| CLV score against `0.50 × RFM index + 0.50 × review index`, with the RFM index kept where the review is missing | maximum absolute difference 0 on 93,358 rows |
| Customers with no review | 603, and each stored score equals the stored RFM index |
| Segments and thresholds | High 13,144, Medium-High 52,727, Medium 15,220, Low 12,267. Every row sits in the band its score selects |
| RFM components on the CLV file against `olist_customer_rfm.csv` | recency, frequency, monetary, and the three scores match, with monetary at a maximum absolute difference of 0 |
| Week 7 pulse | 13,144 rows, all High Value, same identifiers as the High Value segment, threshold 170 on every row, 2,051 flagged, 47 customers at exactly 170 and none of them flagged. 2,051 / 13,144 = 15.6041%, which rounds to 15.60% |
| Week 6 grains | customers 93,358, orders 99,441, shipments 112,650, state-month 675, funnel 4, segment profile 4 |
| Tableau delivered revenue and delivered-order count | R$ 13,221,498.11 and 96,478 |
| Funnel | 99,441, 99,440, 96,477, 95,831 |
| State-month delivered orders and revenue | 96,478 and R$ 13,221,498.11 |
| Week 6 script | 28 / 28 passed, protected Week 2–5 files unchanged |
| Tableau directory MD5 | 9 / 9 files identical to the pre-change copies |
| Geolocation lookup and state centroids | exact match to the previous median-and-mode rule |
| Rebuilt shipment distance | maximum absolute difference 4.55e-13, no difference above 1e-6 |

A fresh evaluation of the RFM index from the stored component scores matches the stored `rfm_index` on 93,355 rows. The other 3 rows differ by 1.42e-14, one binary step. The CLV score built from the same arithmetic matches on all 93,358 rows. The CLV file was not rewritten in this pass, so those three rows are a property of the stored file, not a result of the optimization.

## 6. Analytical invariants

The following are unchanged in definition and in the stored results.

| Invariant | Confirmed value |
| --- | --- |
| Order-level cleaned dataset | 99,441 rows |
| Customer RFM dataset | 93,358 rows |
| Delivered orders | 96,478 |
| Delivered product revenue | R$ 13,221,498.11 |
| CLV score | 0.50 × RFM index + 0.50 × review index, missing-review weight left on the RFM index |
| CLV maximum absolute difference | 0 across 93,358 customers |
| Segment thresholds | High ≥ 80, Medium-High ≥ 60, Medium ≥ 40, Low < 40 |
| Week 7 High Value population | 13,144 |
| Week 7 flagged customers | 2,051 |
| Week 7 risk percentage | 15.60% |
| Week 7 threshold | `recency_days > 170` |

The geolocation method is the same median of in-box rows, with duplicate pings kept and the 42 out-of-box rows excluded. The forecast was not refit. The documented limits remain the ones in the Week 4 methodology and in R1: the quarterly line is exploratory, the 2018Q3 snapshot is not the baseline segment count, and the distance median is sensitive to the duplicate geolocation rows. None of those notes were removed.

## 7. Final package folder structure

Pack the working directory. Do not pack `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`, `.git/`, or `.DS_Store`. Do not use `git archive` as the submission. It omits `data/raw/`, `data/processed/`, and `data/output/`.

```text
customer-lifetime-value/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── 01_week1_data_audit.ipynb
│   ├── 02_week2_data_integration.ipynb
│   ├── 03_week3_rfm_analysis.ipynb
│   ├── 04_week4_clv_analysis.ipynb
│   └── 05_week5_advanced_visualizations.ipynb
├── src/
│   └── prepare_week6_tableau_sources.py
├── data/
│   ├── raw/                          nine Olist CSVs
│   ├── processed/                    five analytical extracts
│   ├── output/                       Week 3–5 tables and charts
│   └── tableau/                      six Week 6 CSVs, Week 7 pulse, validation log
├── docs/
│   ├── ai_use_disclosure.md
│   ├── data_dictionary/
│   ├── er_diagram/
│   ├── week4_methodology.md
│   ├── week4_mid_project_deck.pptx
│   ├── week5_marketing_personas.md
│   ├── week6_*.md
│   ├── week7_*.md
│   ├── week8_end_to_end_qa_report.md
│   └── week8_performance_and_packaging_report.md
├── sql/                              empty
└── dashboard/                        empty
```

The working files outside `.venv` and `.git` total 319,173,652 bytes, about 304 MB, of which `data/` is 291 MB. No second copy of the datasets was created for this package. The empty `sql/` and `dashboard/` directories are the original placeholders. They contain no script to run.

## 8. Missing artifacts and remaining manual steps

| Artifact | State |
| --- | --- |
| Nine raw Olist tables | Present locally in `data/raw/`. Absent from Git. |
| Processed extracts and Week 3–5 outputs | Present locally. Absent from Git. |
| Six Week 6 Tableau CSVs | Present, and tracked. Byte-identical after the script change. |
| Week 7 pulse CSV | Present. No generator script is checked in. Rebuilds follow `docs/week7_pulse_metric_implementation.md`. |
| Tableau workbook (`.twb` or `.twbx`) | Missing. Searched the project. Tableau Public was not opened. |
| Weekly documentation and both Week 8 reports | Present once this report is included. |
| Week 4 mid-project deck | Present. This is not a final presentation. |
| Executive summary | Missing. |
| Final presentation | Missing. |
| README with setup and execution steps | Updated in this pass. |
| AI-use disclosure | Added at `docs/ai_use_disclosure.md`. |

Remaining manual steps:

1. Build the Week 6 workbook in Tableau from `docs/week6_tableau_implementation_guide.md`, export `.twbx`, and put that file in the submission folder. R1 checks C40 and C43 stay unverified until the workbook is opened.
2. Add the Week 7 pulse sheet and confirm the alert tile at the 170-day parameter.
3. Write the executive summary and the final presentation. Do not replace the baseline High Value count of 13,144 with the quarter-specific snapshot count.
4. Zip the working directory with the exclusions in section 7. Do not include the virtual environment, and do not publish the zip from this pass.

## 9. R2 readiness assessment

R2 is not complete.

The performance work that could be justified from a measurement is done. The ZIP-prefix mode is about eight times faster on the full geolocation file and no longer copies the unused city column. The Week 6 script no longer loads columns it does not write. The CLV score, the segment counts, the delivered revenue, the grains, and the Week 7 pulse match the locked values. The Tableau CSVs are byte-identical to the files from before the script change. The distance file matches a rebuild from the revised lookup at the same floating-point floor as R1.

The submission package is not ready. The Tableau workbook is not in the project, the executive summary and the final presentation have not been created, and a Git export would leave out the source and processed data. Those are manual steps. They are not inferred from the CSVs that are already checked.
