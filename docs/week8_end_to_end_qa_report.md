# Week 8 — End-to-End QA Report

**Project:** Customer Lifetime Value & Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce Public Dataset
**Requirement:** R1, final QA of every join and calculation across the nine Olist tables and the CLV formula
**Audit date:** 16 November 2026
**Mode:** Read-only. No notebook, source file, raw table, processed extract, or Tableau CSV was modified.

The audit reloaded the complete files. It did not use a sample for any count, join, or formula. A check is **PASS** when the recomputation matches the stored result. It is **FAIL** when a required figure or join disagrees. It is **WARNING** when the figure is internally consistent but the source data, a definition boundary, or the fitness of a result needs to be carried into the viva. It is **NOT VERIFIED** when this review could not execute the check.

## 1. Executive QA summary

The joins and the CLV calculation hold on the full data. The order extract has one row for each of the 99,441 orders. The customer RFM and CLV tables have one row for each of the 93,358 customers with a delivered order. Recomputing recency, frequency, monetary value, the 0.50 / 0.50 CLV score, the segment bands, delivered revenue, the funnel, the state-month grid, seller-to-buyer distance, and the Week 7 pulse rule reproduced the stored outputs. The largest absolute difference on the CLV score was 0. Delivered product revenue is R$ 13,221,498.11 at every layer that uses that definition.

No check failed. Eleven warnings are source-data defects or definition boundaries that the project already mostly documents. Two checks were not run: the published Tableau Public workbook is not in the repository, and the Week 7 alert screen was not opened in Tableau. Those two are presentation checks. They are not unanswered join or formula checks.

The CLV score remains a 0–100 composite of the RFM index and the review index. This audit does not relabel it as predicted future revenue or as a churn probability.

| Result | Checks |
| --- | ---: |
| PASS | 33 |
| FAIL | 0 |
| WARNING | 11 |
| NOT VERIFIED | 2 |
| Total | 46 |

No critical defect requires a correction before R1 is declared complete for the joins and calculations.

### Scoreboard

| Check | Expected result | Actual result | Status | Evidence |
| --- | --- | --- | --- | --- |
| C01 Raw inventory | 9 tables at the Week 1 shapes | All 9 present. Rows: customers 99,441; geolocation 1,000,163; items 112,650; payments 103,886; reviews 99,224; orders 99,441; products 32,951; sellers 3,095; translation 71. Columns: 5, 5, 7, 5, 7, 8, 9, 4, 2 | PASS | `data/raw/` reloaded in full |
| C02 `customer_id` and orders | `customer_id` unique and 1:1 with `orders` | 99,441 unique ids, 0 unmatched in either direction | PASS | `olist_customers_dataset.csv`, `olist_orders_dataset.csv` |
| C03 `customer_unique_id` | Not a primary key. 96,096 people, some with several order rows | 96,096 distinct ids, 3,345 extra rows, 2,997 people with more than one row, maximum 17 rows | PASS | Customers table. Matches `docs/data_dictionary/data_charter.md` |
| C04 `order_id` | Unique order header | 99,441 unique `order_id` values | PASS | `olist_orders_dataset.csv` |
| C05 Order items | Composite key `(order_id, order_item_id)`; product and seller foreign keys match | 112,650 rows, 0 duplicate keys, 0 unmatched products, 0 unmatched sellers, 0 items pointing at a missing order | PASS | `olist_order_items_dataset.csv` |
| C06 Payments | Composite key `(order_id, payment_sequential)`; many payments per order allowed | 103,886 rows, 0 duplicate keys, 0 payments pointing at a missing order, 2,961 orders with more than one payment, maximum 29 | PASS | `olist_order_payments_dataset.csv` |
| C07 `review_id` | Documented as not unique | 98,410 distinct ids, 789 ids repeated, 1,603 affected rows, 1,412 orders. 0 exact duplicate rows. Scores all in 1–5 | WARNING | `olist_order_reviews_dataset.csv`. Matches `docs/data_dictionary/data_dictionary.md` |
| C08 Review score domain | Scores from 1 to 5, no null score | 0 null scores, 0 scores outside 1–5. Comment title null on 87,656 rows (88.34%). Comment message null on 58,247 rows (58.70%) | PASS | Reviews table. Comments are optional and are not inputs to CLV |
| C09 Product, seller, translation keys | Each parent key unique | `product_id` 32,951 unique, `seller_id` 3,095 unique, `product_category_name` 71 unique | PASS | Products, sellers, translation tables |
| C10 Category references | Small documented gap | 610 products have a null category. 13 products use `pc_gamer` or `portateis_cozinha_e_preparadores_de_alimentos`, which are absent from the translation table | WARNING | Products and `product_category_name_translation.csv` |
| C11 Geolocation key | ZIP prefix is not a primary key. Out-of-box points are excluded before the median | 19,015 prefixes across 1,000,163 rows. 261,831 exact duplicate rows. 42 rows outside latitude −34 to 5.5 and longitude −74.5 to −34, touching 21 prefixes. Median lookup has 19,010 prefixes | WARNING | `olist_geolocation_dataset.csv`. The 42-row exclusion matches the Week 3 notebook output |
| C12 ZIP referential gaps | Documented unmatched prefixes | 278 customer rows (0.28%) and 7 seller rows (0.23%) have a prefix with no geolocation row | WARNING | Customers, sellers, geolocation |
| C13 Order timestamps | Purchase timestamps parse. Known sequence anomalies remain | 0 unparsed purchase timestamps. Nulls: approved 160, carrier 1,783, customer delivery 2,965. Carrier before purchase: 166. Customer delivery before carrier: 23. Delivered status with no customer timestamp: 8 orders. Non-delivered status with a customer timestamp: 6 orders | WARNING | `olist_orders_dataset.csv`. The 166 and 23 are the Week 1 warnings |
| C14 Payment values | Payments should be usable as amounts | 0 negative amounts. 9 rows have `payment_value` 0 (6 voucher, 3 `not_defined`). 3 rows have type `not_defined`. 2 rows have `payment_installments` 0. Range of installments is 0 to 24 | WARNING | `olist_order_payments_dataset.csv` |
| C15 Week 2 grain | 99,441 orders, one row each | 99,441 rows, `order_id` unique, identifier set equal to the orders table, 24 columns | PASS | `data/processed/olist_order_level_cleaned.csv` |
| C16 Item aggregation | Sum of price before the join, no row multiplication | Item aggregate has 98,666 orders. Raw `price` sum R$ 13,591,643.70. Extract `total_product_value` matches within 2.3e-13. Item counts, product counts, seller counts, and freight match | PASS | Raw items vs cleaned extract |
| C17 Payment aggregation | Sum of payments before the join | Payment aggregate has 99,440 orders. Raw payment sum R$ 16,008,872.12. Stored totals match within 2.3e-13. Primary payment type mismatches: 0 | PASS | Raw payments vs cleaned extract |
| C18 Missing children | Orders without items or payments stay in the extract | 775 orders have no items and `total_product_value` 0. 1 order has no payment. That delivered order is `bfbd0f9bdef84302105ad712db648a6c`, product value R$ 134.97, stored payment value 0, primary type blank | PASS | Cleaned extract |
| C19 RFM population | Delivered orders only, one row per `customer_unique_id` | 96,478 delivered orders, 93,358 customers, reference date 2018-08-29 15:00:37 | PASS | Cleaned extract and `data/processed/olist_customer_rfm.csv` |
| C20 RFM components | Recency in whole days, frequency as distinct delivered orders, monetary as delivered `total_product_value` | Recency, frequency, last purchase, freight, and monetary match. Maximum absolute monetary difference 2.3e-13 | PASS | Recomputed from the cleaned extract |
| C21 Repeat counts | 90,557 customers with one delivered order; 2,801 with two or more | 90,557 and 2,801. Frequency ranges from 1 to 15 | PASS | RFM extract, confirmed by the recompute |
| C22 RFM scores | Recency and monetary use five-bin `qcut`. Frequency uses the distinct-value fallback | Scores match on all 93,358 rows. Frequency score 1 contains frequency 1 and 2: 93,130 customers (99.76%) | PASS | `quintile_score` from `notebooks/03_week3_rfm_analysis.ipynb` reapplied |
| C23 Distance | One shipment row per item. Haversine on ZIP medians, Earth radius 6,371.0088 km | 112,650 rows, 0 duplicate keys, 112,095 distances, 0 negative, maximum absolute difference 4.5e-13 | PASS | `data/processed/olist_order_distance_analysis.csv` |
| C24 Delay and association | Delay is customer date minus estimated date, in fractional days. Association is not causal | 110,197 delivered shipments, 110,189 with a delay. Pearson r = −0.0783 and Spearman r = −0.1823 on 109,652 delivered pairs with both measures | PASS | Distance extract. Matches the Week 3 printed correlations |
| C25 Duplicate geolocation rows | Median of in-box rows is the implemented rule | Dropping 261,831 exact duplicate rows before the median would change 14,174 of 19,010 prefix coordinates and 98,200 shipment distances by more than 0.01 km. 57 shipments would move by more than 10 km. Maximum change 799.13 km | WARNING | Sensitivity run against the same Haversine. The stored file matches the median that keeps the duplicate rows |
| C26 Delay on non-delivered rows | Delay statistics use delivered shipments | The column is filled for 7 non-delivered shipments that have both dates. Week 6 tells the dashboard to average only `is_delivered_order = 1` | WARNING | Distance extract and `docs/week6_tableau_validation.md` |
| C27 CLV formula and segments | `0.50 × RFM index + 0.50 × review index`. Bands 80 / 60 / 40 | Maximum absolute score difference 0 on 93,358 rows. High 13,144, Medium-High 52,727, Medium 15,220, Low 12,267 | PASS | `data/processed/olist_customer_clv.csv` |
| C28 Missing reviews | Blank review index. Score falls back to the RFM index | 603 customers. 0 of them have a stored review index. All 603 scores equal `rfm_index`. High Value has 0 of these customers | PASS | CLV extract |
| C29 Review rebuild | Order-level mean, then customer-level mean, delivered orders only | 96,361 review rows, 95,832 delivered orders with a review, 92,755 customers. Average score, review count, and reviewed-order count match with maximum absolute difference 0. 189 orders have disagreeing scores and keep the mean | PASS | Raw reviews joined to delivered orders |
| C30 Forecast arithmetic | Six complete quarters. Separate OLS line per segment. Holdout 2018Q2 | Complete quarters are 2017Q1–2018Q2. Partial quarters are 2016Q3, 2016Q4, and 2018Q3. Recomputed MAE 2,131.225, MAPE 12.465%, naive MAE 4,741.5. Forward 2018Q3 predictions match `week4_segment_forecast.csv` | PASS | `data/output/week4_quarterly_segment_trends.csv` |
| C31 Snapshot segments vs baseline | Same labels can be misread as the same counts | 2018Q3 snapshot, using quarter-specific quintiles: High 12,905, Medium-High 52,748, Medium 15,487, Low 12,218. Baseline table, using Week 3 scores: 13,144 / 52,727 / 15,220 / 12,267. Both totals are 93,358 | WARNING | `docs/week4_methodology.md` states the two scoring bases |
| C32 Forecast use | Exploratory only. Not a monetary lifetime forecast | Holdout errors are 1,901, 3,900, 972, and 1,751 customers. The methodology already calls the series short and the forecast exploratory | WARNING | `data/output/week4_forecast_validation.csv` |
| C33 Week 5 revenue | Segment counts sum to 93,358 and revenue to R$ 13,221,498.11 | High R$ 3,317,992.65, Medium-High R$ 6,532,268.84, Medium R$ 1,597,899.78, Low R$ 1,773,336.84 | PASS | CLV `monetary` grouped by segment, and `data/output/week5_segment_revenue_summary.csv` |
| C34 Funnel | 99,441 → 99,440 → 96,477 → 95,831. Stage 3 requires payment and delivery | Recomputed counts match Week 5 and `tableau_funnel.csv`. The one delivered order without a payment is excluded from stages 3 and 4 and remains inside delivered revenue | PASS | `data/output/week5_funnel_summary.csv` |
| C35 State-month grid | 675 state-month cells, 99,441 orders, delivered revenue R$ 13,221,498.11 | Week 5 and Tableau grids match on all 675 keys. Order-count mismatches 0. Revenue maximum absolute difference 1.5e-11. Delivered-order sum 96,478 | PASS | `data/output/week5_state_month_summary.csv`, `data/tableau/tableau_state_month.csv` |
| C36 Causal language | Recommendations are tests, not measured effects | Week 5 personas, Week 6 findings, and the Week 7 escalation note say no campaign result exists | PASS | `docs/week5_marketing_personas.md`, `docs/week6_leadership_findings.md`, `docs/week7_alert_rule_and_campaign_escalation.md` |
| C37 Tableau grains | 93,358; 99,441; 112,650; 675; 4 stages; 4 segments | All six counts and their keys match. Shipment orders are a subset of orders. 775 orders have no shipment. Files are separate, so shipments are not physically joined onto order revenue | PASS | `data/tableau/` |
| C38 Tableau shipment measures | Distance and delay copied from Week 3 | 112,650 keys match. Distance and delay maximum absolute difference 0. Delivered flags match after reading 1/0 as boolean | PASS | `tableau_shipments.csv` vs `olist_order_distance_analysis.csv` |
| C39 Blank segment | Undelivered orders may have no CLV segment | 2,758 orders have a blank segment. 0 delivered orders have a blank segment | PASS | `tableau_orders.csv` |
| C40 Rendered Tableau workbook | Dashboard opens and the published sheets match the guide | No `.twb` or `.twbx` file is in the repository. Tableau Public was not opened | NOT VERIFIED | Repository search |
| C41 Week 7 pulse rule | 13,144 High Value rows, flag when `recency_days > 170` | 13,144 unique ids, all High Value, 2,051 flagged (15.6041%, reported 15.60%), 11,093 within band, 47 customers at exactly 170 days and none of them flagged. Status text is `Recency watch` or `Within band` | PASS | `data/tableau/week7_high_value_risk_pulse.csv` vs the CLV extract |
| C42 Alert arithmetic | Alert above 10% and at or below 20%. Escalation above 20% | 15.60% falls in the Alert band. It is not Escalation | PASS | Pulse file and `docs/week7_alert_rule_and_campaign_escalation.md` |
| C43 Rendered pulse screen | Parameter controls and the alert tile behave as written | The CSV and the calculated-field text were checked. Tableau was not opened, so the on-screen indicator was not clicked | NOT VERIFIED | `docs/week7_pulse_metric_implementation.md` |
| C44 Customer-count gap | 96,096 people in the customers table and 93,358 scored customers | The 2,738-person gap is the set of `customer_unique_id` values with no delivered order. RFM eligibility is delivered status | PASS | Customers table vs delivered orders |
| C45 Seventeen orders vs fifteen delivered | Charter says up to 17 orders. RFM maximum is 15 | Both are true. 17 is the maximum order rows per person. 15 is the maximum delivered orders | PASS | Customers table and RFM `frequency` |
| C46 One-order rate vs frequency score | 97.0% have one delivered order. 99.76% have frequency score 1 | 90,557 / 93,358 = 97.0%. Score 1 also contains the 2,573 customers with two delivered orders. Week 6 states the distinction | WARNING | RFM score table and `docs/week6_leadership_findings.md` |

## 2. Audit coverage of the nine original tables

Every table in `data/raw/` was read in full.

| Table | File | Rows | Columns | Key result |
| --- | --- | ---: | ---: | --- |
| Customers | `olist_customers_dataset.csv` | 99,441 | 5 | `customer_id` is unique. `customer_unique_id` is not |
| Geolocation | `olist_geolocation_dataset.csv` | 1,000,163 | 5 | ZIP prefix is not unique. 261,831 rows are exact duplicates |
| Order items | `olist_order_items_dataset.csv` | 112,650 | 7 | `(order_id, order_item_id)` is unique |
| Payments | `olist_order_payments_dataset.csv` | 103,886 | 5 | `(order_id, payment_sequential)` is unique |
| Reviews | `olist_order_reviews_dataset.csv` | 99,224 | 7 | `review_id` is not unique. `review_score` is always 1–5 |
| Orders | `olist_orders_dataset.csv` | 99,441 | 8 | `order_id` is unique |
| Products | `olist_products_dataset.csv` | 32,951 | 9 | `product_id` is unique. 610 category names are null |
| Sellers | `olist_sellers_dataset.csv` | 3,095 | 4 | `seller_id` is unique |
| Category translation | `product_category_name_translation.csv` | 71 | 2 | Portuguese category name is unique |

Order status counts are delivered 96,478, shipped 1,107, canceled 625, unavailable 609, invoiced 314, processing 301, created 5, and approved 2. Those 96,478 delivered orders are the RFM population. Payment types are credit card 76,795, boleto 19,784, voucher 5,775, debit card 1,529, and `not_defined` 3.

`customer_id` is the order-scoped key. It matches orders one to one. `customer_unique_id` is the person. Using `customer_id` for RFM would count a repeat buyer as several people. The pipeline does not do that. Week 3 groups delivered orders by `customer_unique_id`.

## 3. Join integrity audit

| Relationship | Grain | Unmatched child rows | Rows left without a child | Fanout |
| --- | --- | ---: | ---: | --- |
| `orders.customer_id` → customers | 1:1 | 0 | 0 | None. The cleaned extract stays at 99,441 |
| `order_items.order_id` → orders | many items to one order | 0 | 775 orders | Prevented by aggregating items to one row per order before the Week 2 join |
| `order_items.product_id` → products | many to one | 0 | Products with no sales were not required | Not used as a row-multiplying join in CLV |
| `order_items.seller_id` → sellers | many to one | 0 | Sellers with no sales were not required | Seller coordinates are attached one seller to many items. Shipment row count stays 112,650 |
| `payments.order_id` → orders | many payments to one order | 0 | 1 order | Prevented by aggregating payments before the join |
| `reviews.order_id` → orders | some orders have 2 or 3 review rows | 0 | 768 orders have no review row | Prevented by averaging to `order_id`, then to `customer_unique_id` |
| Customer ZIP → geolocation | many to many | 278 customer rows | — | Week 3 collapses geolocation to one median per prefix before the distance join |
| Seller ZIP → geolocation | many to many | 7 sellers | — | Same median lookup |
| `products.product_category_name` → translation | many to one | 13 product rows, plus 610 nulls | Translation rows with no products were not required | Not on the CLV path |

Week 2 checks that matter for revenue:

- `total_product_value` is the sum of `order_items.price`.
- `total_freight_value` is the sum of `order_items.freight_value`.
- `total_payment_value` is the sum of `payment_value`.
- The primary payment type is the type with the largest summed amount on that order.
- The cleaned extract has the same 99,441 order identifiers as the orders table.

Delivered product revenue on the cleaned extract is R$ 13,221,498.11. The all-status product total is R$ 13,591,643.70, equal to the raw price sum. Freight is not inside the revenue KPI.

The delivered order without a payment row is `bfbd0f9bdef84302105ad712db648a6c`. It also has a valid review. Funnel stage 3 is payment and delivery, so this order is among the 96,478 delivered orders and is not among the 96,477 funnel stage-3 orders. Its R$ 134.97 stays in delivered revenue. The missing payment is not dropped silently.

## 4. Week-by-week calculation audit

### Week 2 — integration

Source: `notebooks/02_week2_data_integration.ipynb` and `data/processed/olist_order_level_cleaned.csv`.

The extract is one row per `order_id`. Item and payment aggregates were rebuilt from the raw tables and compared with the extract. Differences sit at binary floating-point noise, below 1e-12. There is no join fanout. Orders with no items remain, with product and freight value set to 0 and `has_order_items` false. The order with no payment remains, with payment value stored as 0 and the primary type left blank.

### Week 3 — RFM and geography

Source: `notebooks/03_week3_rfm_analysis.ipynb`, `data/processed/olist_customer_rfm.csv`, and `data/processed/olist_order_distance_analysis.csv`.

Eligibility is `order_status = delivered`. Frequency counts distinct delivered `order_id` values. Monetary value sums `total_product_value` and does not add freight. Recency is the whole-day gap from the latest delivered purchase to 2018-08-29 15:00:37. Recomputed components match the stored customer file.

The frequency score cannot be a normal five-bin quantile because almost everyone ordered once. The distinct-value fallback assigns score 1 to frequency 1 and 2, score 2 to frequency 3 and 4, score 3 to frequency 5, score 4 to frequency 6 and 7, and score 5 to frequency 9 and 15. Recency and monetary scores are ordinary five-bin quantiles. All three stored score columns match the reapplied function.

Distance uses the median latitude and longitude of geolocation rows inside the Brazil box, then the Haversine formula with radius 6,371.0088 km. Rebuilt distances match the 112,095 stored values. None are negative. Delivery delay matches on the rows where both timestamps exist. On the 109,652 delivered shipments with both a distance and a delay, Pearson correlation is −0.0783 and Spearman correlation is −0.1823. Both are very weak. The Week 3 text treats them as association. That reading is the one supported by the coefficients.

### Week 4 — CLV and forecast

Covered in section 5. The forecast arithmetic is included here because it is a Week 4 calculation.

`data/output/week4_quarterly_segment_trends.csv` has nine snapshots. Six are complete: 2017Q1, 2017Q2, 2017Q3, 2017Q4, 2018Q1, and 2018Q2. Three are partial: 2016Q3, 2016Q4, and 2018Q3. On every snapshot the four segment counts sum to the snapshot total.

An ordinary least-squares line was refit independently for each segment on quarter indexes 0 through 5. The 2018Q3 predictions match `data/output/week4_segment_forecast.csv`: High 11,420.20, Medium-High 52,934.73, Medium 16,237.00, and Low 12,122.73. The holdout, fit on 2017Q1–2018Q1 and scored on 2018Q2, matches `data/output/week4_forecast_validation.csv`, including MAE 2,131.225 customers per segment and MAPE 12.465%.

### Week 5 — profiles, map, and funnel

Source: `notebooks/05_week5_advanced_visualizations.ipynb`, `data/output/week5_segment_revenue_summary.csv`, `data/output/week5_funnel_summary.csv`, and `data/output/week5_state_month_summary.csv`.

Segment counts and delivered revenue were grouped again from the CLV extract. They match the Week 5 summary and the persona counts in `docs/week5_marketing_personas.md`. The funnel was rebuilt from order status, the payment-order set, and delivered orders that have a review score from 1 to 5. The four stage counts match. The state-month grid has 27 states by 25 months, 675 cells, and reconciles cell by cell to the Tableau grid, including the delivered-revenue total.

The persona note says the marketing actions are tests and that the analysis does not estimate a causal effect. The correlation result in Week 3 is also described as association. This audit found no document that claims a campaign produced revenue.

## 5. CLV formula verification

The stored score was recomputed for every customer:

```
rfm_index = (recency_score + frequency_score + monetary_score) / 15 × 100
review_index = (average_review_score − 1) / 4 × 100
clv_score = 0.50 × rfm_index + 0.50 × review_index
```

When `average_review_score` is missing, `review_index` stays missing and `clv_score = rfm_index`. That is the weight renormalisation with only the RFM weight left. A missing review is not coded as 0.

Bands, with a boundary score entering the higher band:

| Rule | Segment | Customers |
| --- | --- | ---: |
| Score ≥ 80 | High Value | 13,144 |
| Score ≥ 60 and < 80 | Medium-High Value | 52,727 |
| Score ≥ 40 and < 60 | Medium Value | 15,220 |
| Score < 40 | Low Value | 12,267 |

The score ranges from 10 to 100. The mean is 62.58 and the median is 66.67, matching `data/output/week4_clv_summary.csv`. The RFM component scores on the CLV file are the same values as on `olist_customer_rfm.csv`.

The average review was also rebuilt from `olist_order_reviews_dataset.csv`: keep scores 1 to 5, keep delivered orders, average at `order_id`, then average those order means at `customer_unique_id`. That rebuild matches the stored average, the review count, and the reviewed-order count for all 92,755 reviewed customers.

This score is not a forecast of future spend in Brazilian reais. Monetary value in the RFM input is historical delivered product value. The 0–100 result is a value-and-experience index.

## 6. Tableau data-source reconciliation

The Week 6 files in `data/tableau/` were checked against the processed extracts. `data/tableau/validation_checks.csv` records a preparation-script pass. This audit did not trust that log on its own. The grains and the money totals were recomputed.

| File | Rows | Grain | Reconciliation |
| --- | ---: | --- | --- |
| `tableau_customer_clv.csv` | 93,358 | `customer_unique_id` | Same keys, scores, and segments as the CLV extract |
| `tableau_orders.csv` | 99,441 | `order_id` | Delivered revenue R$ 13,221,498.11. `is_delivered` sums to 96,478. `has_payment_record` sums to 99,440 |
| `tableau_shipments.csv` | 112,650 | `order_id` + `order_item_id` | Distance and delay match the Week 3 file exactly |
| `tableau_state_month.csv` | 675 | state + month | Matches the Week 5 grid |
| `tableau_funnel.csv` | 4 | stage | 99,441, 99,440, 96,477, 95,831 |
| `tableau_segment_profile.csv` | 4 | segment | Counts and revenue match Week 5 |

`has_valid_review` on the orders file sums to 98,673. That flag is any order with a valid review, including orders that were not delivered. Funnel stage 4 is the nested count, 95,831, and it matches the stage file. The dictionary tells the dashboard not to use the raw flag as stage 4. That instruction is necessary and correct.

Customer, order, and shipment files are separate. A physical join of shipments onto orders would repeat revenue once per item. The prepared files do not do that. Whether the Tableau relationship dialog was set as the guide describes was not visible from the CSV files. That is part of C40.

## 7. Week 7 pulse verification

Source: `data/tableau/week7_high_value_risk_pulse.csv` and the four Week 7 notes.

| Rule | Result |
| --- | --- |
| Population | 13,144 rows, 13,144 distinct `customer_unique_id`, set equal to High Value on the CLV extract |
| Threshold | `risk_recency_threshold_days` is 170 on every row, equal to 2 × the High Value median of 85 days |
| Flag | `risk_flag = 1` exactly when `recency_days > 170`. Disagreements: 0 |
| Flagged | 2,051 customers, 15.60% |
| Exactly 170 days | 47 customers, all unflagged |
| Status values | `Recency watch` and `Within band` only. The word churn does not appear in the status field |
| Reference date | 2018-08-29 15:00:37 on every row |
| Alert | 15.60% is above the 10% alert cut and at or below the 20% escalation cut, so the documented status is Alert |

The parameter formula in the implementation guide, `IF [recency_days] > [Risk recency threshold (days)] THEN 1 ELSE 0 END`, returns the stored `risk_flag` when the parameter is 170. That identity was checked on all 13,144 rows. The screen that would display the amber Alert tile was not opened.

The Week 7 notes describe the flag as a recency watch on a historical snapshot. They do not say the flag was validated against a churn outcome. The Olist files used here have no verified churn label, so this audit also did not attempt that validation.

## 8. Cross-project metric reconciliation

These pairs look like conflicts until the grain is named. Each one was traced.

| Pair | Values | Resolution | Status |
| --- | --- | --- | --- |
| People vs scored customers | 96,096 and 93,358 | 93,358 is the delivered-order subset | PASS, C44 |
| All orders vs delivered orders per person | Maximum 17 and maximum 15 | Different filters | PASS, C45 |
| Delivered orders vs funnel stage 3 | 96,478 and 96,477 | One delivered order has no payment row | PASS, C34 |
| One delivered order vs frequency score 1 | 97.0% and 99.76% | Score 1 contains one-order and two-order customers | WARNING, C46. Week 6 now states this in prose |
| Baseline segments vs 2018Q3 snapshot | High Value 13,144 and 12,905, with the other bands also different | Snapshot quintiles are refit inside the quarter. The baseline uses the published Week 3 scores | WARNING, C31 |
| `has_valid_review` vs funnel stage 4 | 98,673 and 95,831 | The flag is not nested. Stage 4 also requires payment and delivery | PASS, C34 and C37 |
| Customer monetary, segment revenue, state-month revenue, delivered orders | Each is R$ 13,221,498.11 | Same delivered-product definition | PASS, C33 and C35 |

No unexplained numeric break remained between the raw tables, the processed extracts, the Week 3–5 output CSVs, the Tableau CSVs, and the Week 4–7 notes that quote these figures.

## 9. Failed checks and warnings

Failed checks: none.

Warnings, in the scoreboard's wording:

| ID | Severity | What to say in the viva |
| --- | --- | --- |
| C07 | Low | `review_id` is repeated across orders. The review grain used for CLV is the order mean, not `review_id` |
| C10 | Low | 610 products have no category and 13 use a name the translation table does not contain. CLV does not use category |
| C11 | Medium | A ZIP prefix has many geolocation rows, including exact duplicate rows. See C25 |
| C12 | Low | 278 customer rows and 7 sellers do not match a ZIP prefix. Together with prefixes that have no in-box coordinate, this leaves 555 of 112,650 shipments without a distance |
| C13 | Low | A small set of timestamps is out of sequence. Recency uses the purchase timestamp, which parsed for every order |
| C14 | Low | Nine payment amounts are zero and three payment types are `not_defined`. They do not enter the product-revenue KPI |
| C25 | Medium | Keeping exact duplicate geolocation rows inside the median is reproducible, and it is also sensitive. Removing those duplicates would move 98,200 distances by more than 0.01 km and 57 by more than 10 km, with a maximum of 799.13 km. CLV does not use this coordinate |
| C26 | Low | Seven non-delivered shipments have a delay value stored. The delay average is valid on delivered shipments only |
| C31 | Medium | Do not quote 12,905 as the High Value count. The reporting count is 13,144. The 12,905 figure is the quarter-specific snapshot |
| C32 | Medium | The segment forecast reproduces, and the holdout is still off by about 2,131 customers per segment. It is an exploratory line, not an operating forecast |
| C46 | Low | Say 90,557 customers, 97.0%, have one delivered order. Say 99.76% only for frequency score 1 |

## 10. Unverified checks and reasons

| ID | Check | Reason |
| --- | --- | --- |
| C40 | The Week 6 dashboard as rendered in Tableau Public | The repository has the CSV sources, the data dictionary, the implementation guide, and `validation_checks.csv`. It has no `.twb` or `.twbx`. Filters, colours, and parameter widgets were not clicked |
| C43 | The Week 7 alert tile as rendered in Tableau Public | The flag column matches the documented parameter formula at 170 days. The workbook that would show the Alert state was not opened |

Everything required to audit the joins, the RFM inputs, the CLV formula, the revenue definition, the funnel, and the pulse rule was executed on the full data.

## 11. Severity classification

| Severity | IDs | Correction required for R1 |
| --- | --- | --- |
| Critical | None | No |
| High | None | No |
| Medium | C11, C25, C31, C32 | No formula change. Disclose the coordinate sensitivity, use 13,144 as the High Value count, and keep the forecast labelled exploratory |
| Low | C07, C10, C12, C13, C14, C26, C46 | No. These are documented data limits or definition labels |

C11 and C25 are the same underlying geolocation issue. C11 is the key structure. C25 is the measured effect on distance.

## 12. Final R1 readiness assessment

R1 can be declared complete for the end-to-end QA of the joins and the calculations.

The nine source tables were profiled. The Week 2 order grain does not multiply rows. The Week 3 RFM measures, scores, distances, delays, and correlations reproduce. The Week 4 CLV formula, the missing-review rule, the four segments, and the six-quarter forecast arithmetic reproduce. The Week 5 revenue, funnel, and state-month outputs reconcile to R$ 13,221,498.11 and to the documented stage counts. The Week 6 extracts keep those grains. The Week 7 pulse flags 2,051 of 13,144 High Value customers, 15.60%, under `recency_days > 170`, and the resulting alert band is Alert.

The declaration does not cover a click-through of Tableau Public. That screen was not in the files under review. It also does not mean the geolocation median is insensitive to duplicate rows, or that the quarterly line is a reliable forecast. Those are the Medium warnings above. None of them breaks the CLV score or the delivered-revenue total.
