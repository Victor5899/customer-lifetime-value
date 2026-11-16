# Week 8 — Executive Summary

**Project:** Customer Lifetime Value and Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce Public Dataset (`olistbr/brazilian-ecommerce`)
**Date:** 16 November 2026
**Population:** 99,441 orders and 93,358 scored customers
**Revenue in scope:** delivered product value of R$ 13,221,498.11

This summary closes the project. The figures below are the published results from Weeks 1–7 and the Week 8 audits. The CLV score is a 0–100 customer value and experience index. The Week 7 pulse is a simulated recency watch on the 29 August 2018 snapshot.

## 1. Project overview and business problem

Olist is a Brazilian marketplace. The public extract records orders, items, payments, reviews, products, sellers, and approximate ZIP locations from September 2016 through August 2018. The business problem is to tell leadership which customers carry the observed value, where experience is weak, and which High Value customers have gone quiet relative to their own segment.

A currency lifetime-value model would estimate purchases a customer has not yet made. This project does not calculate that quantity. It builds a reproducible score from observed recency, frequency, monetary value, and reviews, assigns fixed bands, and places the result on two Tableau dashboards.

The decisions the score can support are limited and specific:

- Which band holds the delivered product revenue.
- Which band combines higher spend with a strong review.
- Which band’s low score is an experience problem rather than a low-spend problem.
- Which High Value customers, on this snapshot, last purchased more than 170 days before 29 August 2018.

Campaign notes in Weeks 5–7 are tests to design. No campaign was run on this extract, so none has a measured effect.

The dataset is used on a non-commercial basis. The data charter records the Kaggle licence as CC BY-NC-SA 4.0 and attributes the source to Olist.

## 2. Dataset and nine-table data architecture

Week 1 audited nine raw tables. No raw file was edited. Row counts below were reloaded in full during the Week 8 QA.

| Table | File | Rows | Key result |
| --- | --- | ---: | --- |
| Customers | `olist_customers_dataset.csv` | 99,441 | `customer_id` is unique and matches orders 1:1 |
| Orders | `olist_orders_dataset.csv` | 99,441 | `order_id` is unique |
| Order items | `olist_order_items_dataset.csv` | 112,650 | `(order_id, order_item_id)` is unique |
| Payments | `olist_order_payments_dataset.csv` | 103,886 | `(order_id, payment_sequential)` is unique |
| Reviews | `olist_order_reviews_dataset.csv` | 99,224 | `review_id` is not unique |
| Products | `olist_products_dataset.csv` | 32,951 | `product_id` is unique |
| Sellers | `olist_sellers_dataset.csv` | 3,095 | `seller_id` is unique |
| Geolocation | `olist_geolocation_dataset.csv` | 1,000,163 | ZIP prefix is not unique (19,015 prefixes) |
| Category translation | `product_category_name_translation.csv` | 71 | Portuguese category name is unique |

`customer_id` is the order-scoped customer row. `customer_unique_id` is the person: 96,096 distinct people, 2,997 of them with more than one customer row, and a maximum of 17 order rows. Customer-level work uses `customer_unique_id`. Using `customer_id` would treat a repeat buyer as several people.

The relationship map is `docs/er_diagram/olist_er_diagram.png`, drawn from the Week 1 referential-integrity audit. Orders sit at the centre. Items, payments, and reviews hang off `order_id`. Items point to products and sellers. Customers and sellers meet geolocation through the ZIP prefix, which is a many-to-many lookup, not a primary key. The real-customer link from `customer_unique_id` to orders is one person to many orders and is derived through `customer_id`.

Order status on the raw orders table is delivered 96,478, shipped 1,107, canceled 625, unavailable 609, invoiced 314, processing 301, created 5, and approved 2. Payment types are credit card 76,795, boleto 19,784, voucher 5,775, debit card 1,529, and `not_defined` 3.

## 3. Data cleaning and integration methodology

Week 1 documented defects and removed nothing. Week 2 built one row per order. Items were summed to `order_id` before the join, and payments were summed the same way, so neither child table could multiply the order grain.

| Check | Result |
| --- | --- |
| Cleaned order grain | 99,441 rows, one per `order_id`, same identifiers as the orders table |
| Orders with an item aggregate | 98,666 |
| Orders with no items | 775, kept with product value and freight set to 0 |
| Orders with a payment aggregate | 99,440 |
| Orders with no payment | 1, kept |
| Raw item price, all statuses | R$ 13,591,643.70, matched by the extract |
| Raw payment sum | R$ 16,008,872.12, matched by the extract |
| Delivered product revenue | R$ 13,221,498.11 |

`total_product_value` is the sum of `order_items.price`. `total_freight_value` is the sum of freight. `total_payment_value` is the sum of `payment_value`. The primary payment type is the type with the largest summed amount on that order. The revenue KPI uses delivered product value only. Freight and payment value stay on the extract and stay out of the KPI.

The delivered order with no payment row is `bfbd0f9bdef84302105ad712db648a6c`. Its product value is R$ 134.97. It remains inside delivered revenue. Funnel stage 3 requires both a payment record and delivered status, so this order is one of the 96,478 delivered orders and is not one of the 96,477 stage-3 orders.

Reviews are reduced before they touch the customer score. Scores outside 1–5 do not occur. The score path keeps delivered orders, averages disagreeing scores at `order_id` (189 orders), then averages those order means at `customer_unique_id`. Each reviewed order has equal weight. `review_id` is not the grain: 789 identifiers repeat, affecting 1,603 rows and 1,412 orders, with no exact duplicate rows.

Geolocation is collapsed to one coordinate per ZIP prefix before any distance join. The coordinate is the median latitude and longitude of rows inside the documented Brazil box, latitude −34 to 5.5 and longitude −74.5 to −34. Forty-two points outside that box are excluded. Exact duplicate geolocation rows are kept. That choice is reproducible and sensitive; section 12 records the measured effect.

## 4. RFM analysis

RFM is calculated only for customers with at least one delivered order. The reference date is the latest delivered purchase timestamp, 2018-08-29 15:00:37.

| Component | Definition | Score direction |
| --- | --- | --- |
| Recency | Whole days from the customer’s latest delivered purchase to the reference date | Fewer days, higher score |
| Frequency | Count of distinct delivered orders | More orders, higher score |
| Monetary | Sum of delivered `total_product_value` | Higher value, higher score. Freight is excluded |

The scored file has 93,358 customers. The customers table has 96,096 people. The gap of 2,738 is the set of people with no delivered order. Frequency ranges from 1 to 15. The maximum of 17 in the customers table is the maximum order rows of any status, not the maximum delivered orders.

| Delivered-order count | Customers | Share |
| --- | ---: | ---: |
| Exactly one | 90,557 | 97.0% |
| Two or more | 2,801 | 3.0% |
| Scored customers | 93,358 | 100% |

Recency and monetary use five-bin quantiles. Frequency cannot. Almost everyone ordered once, so a standard five-bin split is not available. The distinct-value fallback assigns score 1 to frequency 1 and 2 (93,130 customers, 99.76%), score 2 to frequency 3 and 4, score 3 to frequency 5, score 4 to frequency 6 and 7, and score 5 to frequency 9 and 15. The 99.76% figure is the share with frequency score 1. It is not the share with one order. The one-order share is 97.0%.

Recomputing recency, frequency, monetary value, freight, and the three scores from the order extract matched the stored customer file. The largest absolute monetary difference was floating-point noise at 2.3e-13.

## 5. CLV scoring methodology and segment definitions

Week 4 does not refit the 1–5 RFM scores. It rescales them and combines them with the review.

```
rfm_index    = (recency_score + frequency_score + monetary_score) / 15 × 100
review_index = (average_review_score − 1) / 4 × 100
clv_score    = 0.50 × rfm_index + 0.50 × review_index
```

The RFM index runs from 20 to 100. A review of 1 maps to 0 and a review of 5 maps to 100. The baseline weights are 0.50 and 0.50 and sum to 1. On this run the score ranges from 10.00 to 100.00, with a mean of 62.58 and a median of 66.67.

When `average_review_score` is missing, `review_index` stays missing and the score equals the RFM index. That is the remaining-weight rule with only the RFM weight left. A missing review is not coded as 0. Coding it as 0 would pull the customer down by half the RFM index. The manual check shows the difference: a customer with an RFM index of 40 and no review stays at 40, which is Medium Value. Inserting a review index of 0 would have produced 20 and a Low Value label.

| Review treatment | Customers |
| --- | ---: |
| Valid delivered-order review | 92,755 (99.35%) |
| No valid review; score equals the RFM index | 603 (0.65%) |
| Of those 603, in High Value | 0 |
| Medium-High Value | 136 |
| Medium Value | 321 |
| Low Value | 146 |

Review averages omit the 603. High Value has a review on all 13,144 customers.

A boundary score enters the higher band.

| Rule | Segment | Customers | Share |
| --- | --- | ---: | ---: |
| Score ≥ 80 | High Value | 13,144 | 14.08% |
| Score ≥ 60 and < 80 | Medium-High Value | 52,727 | 56.48% |
| Score ≥ 40 and < 60 | Medium Value | 15,220 | 16.30% |
| Score < 40 | Low Value | 12,267 | 13.14% |

The same function was applied to all 93,358 rows in the Week 7 manual QA and again in the Week 8 audit. The maximum absolute difference on the CLV score was 0. Twelve hand-worked customers, covering both boundaries, a missing review, a review of 1, a fractional review, and a three-order customer, all matched the stored score and the stored segment.

The notebook also scored weight pairs 0.70/0.30 and 0.30/0.70, and threshold scenarios 85/65/45 and 75/55/35. Quarterly history, the forecast, the dashboards, and this summary use the 50/50 weights and the 80/60/40 bands. Under those alternative cuts, High Value would be 2,326 customers at 85/65/45 or 21,783 at 75/55/35. The published count remains 13,144.

## 6. Major segment and revenue findings

Delivered product revenue reconciles to R$ 13,221,498.11 in the customer file, the segment profile, the state-month grid, and the Tableau order extract. Shares below are rounded to two decimals. The currency amounts sum exactly.

| Segment | Customers | Customer share | Delivered product revenue | Revenue share | Average CLV | Average monetary | Median monetary | Average review |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High Value | 13,144 | 14.08% | R$ 3,317,992.65 | 25.10% | 82.35 | R$ 252.43 | R$ 170.30 | 4.998 |
| Medium-High Value | 52,727 | 56.48% | R$ 6,532,268.84 | 49.41% | 69.27 | R$ 123.89 | R$ 75.00 | 4.784 |
| Medium Value | 15,220 | 16.30% | R$ 1,597,899.78 | 12.09% | 51.29 | R$ 104.99 | R$ 69.90 | 3.465 |
| Low Value | 12,267 | 13.14% | R$ 1,773,336.84 | 13.41% | 26.63 | R$ 144.56 | R$ 80.00 | 1.352 |
| Total | 93,358 | 100% | R$ 13,221,498.11 | 100% | 62.58 | — | — | — |

Five findings follow from that profile. They are associations in the historical extract.

1. **Medium-High Value is the core revenue segment.** It holds 56.48% of scored customers and 49.41% of delivered product revenue. Average monetary value is R$ 123.89, so the revenue rank comes from the size of the band. The average CLV score is 69.27.

2. **High Value contributes a larger share of revenue than of customers.** The band is 14.08% of customers and 25.10% of revenue. Average monetary value, R$ 252.43, and the median, R$ 170.30, are the highest of the four bands. Review coverage is 100% and the average review is 4.998. Median recency is 85 days, against 244, 269, and 242 days in the other bands. The two upper bands together are 65,871 customers (70.56%) and R$ 9,850,261.49 (74.50% of delivered product revenue).

3. **The High Value label is a joint score, not a pure spend ranking.** The band’s average spend is the highest. The threshold can still be met with a review of 5 and an RFM index of 60. The manual sample includes a High Value customer at exactly 80 with monetary value R$ 109.90 and component scores 5, 1, and 3. Leadership should read the band as recent-or-strong purchase behaviour plus a top review, then use the monetary column when the question is spend.

4. **Low Value is an experience band on a material revenue pool.** The average review is 1.352, with 98.81% coverage. Average delivered product value is R$ 144.56, above Medium-High Value (R$ 123.89) and Medium Value (R$ 104.99). The median, R$ 80.00, is also above Medium Value (R$ 69.90). A discount aimed only at low spenders would miss that evidence. The band still accounts for R$ 1,773,336.84. Minimum recency in every band, including Low Value, is 0 days. Low Value is the score below 40. It is not a churn label.

5. **A second delivered order is uncommon in every band.** The median frequency is 1.00 everywhere. Repeat shares are 5.39% in High Value, 3.12% in Medium Value, 2.73% in Medium-High Value, and 1.46% in Low Value. Average frequency runs only from 1.015 to 1.067. Frequency therefore adds little separation. The score depends mainly on recency, monetary value, and reviews. Retention work on this extract is a test of a second order.

## 7. Geographic and delivery analysis

The state-month grid has 27 states and 25 observed months, 675 cells, and all 99,441 orders. It counts every order status. Delivered product revenue on the same grid is R$ 13,221,498.11. November 2016 has no column. November 2017 is the largest month, with 7,544 orders.

| Customer state | Orders | Share of 99,441 |
| --- | ---: | ---: |
| São Paulo (SP) | 41,746 | 41.98% |
| Rio de Janeiro (RJ) | 12,852 | 12.92% |
| Minas Gerais (MG) | 11,635 | 11.70% |
| Rio Grande do Sul (RS) | 5,466 | 5.50% |
| Paraná (PR) | 5,045 | 5.07% |

São Paulo’s 41.98% is a share of orders, not a share of scored customers, and not a persona map. September 2018 has 16 orders and October 2018 has 4. Both months contribute R$ 0 delivered revenue because those purchases were not delivered inside the extract. They remain in the order count.

Seller-to-buyer distance is a shipment measure, one row per item. The Haversine formula uses Earth radius 6,371.0088 km and the ZIP-prefix median. The shipment file has 112,650 rows, 112,095 distances, and no negative distance. Five hundred and fifty-five shipments have no distance because a prefix does not match an in-box coordinate. Distance is not an input to CLV.

Delivery delay is the customer timestamp minus the estimated date, in fractional days. Of 110,197 delivered shipments, 110,189 have a delay. On the 109,652 delivered shipments with both a distance and a delay, Pearson correlation is −0.0783 and Spearman correlation is −0.1823. Both are very weak. Week 3 reads them as association. A longer distance is not established here as the cause of a longer delay. The Week 1 audit separately flagged 2,830 orders, 2.93%, above an IQR upper bound of 8.4 days. Those orders were retained.

Seven non-delivered shipments have a delay value stored. Any delay average has to be restricted to delivered shipments. The dashboard guide states that rule.

## 8. Tableau dashboard outcomes

Week 6 publishes six extracts, one grain each, so a shipment row cannot repeat an order’s revenue.

| Extract | Rows | Grain |
| --- | ---: | --- |
| `tableau_customer_clv.csv` | 93,358 | `customer_unique_id` |
| `tableau_orders.csv` | 99,441 | `order_id` |
| `tableau_shipments.csv` | 112,650 | `order_id` + `order_item_id` |
| `tableau_state_month.csv` | 675 | state + month |
| `tableau_funnel.csv` | 4 | stage |
| `tableau_segment_profile.csv` | 4 | segment |

Customer CLV, Orders, and Shipments share one relationship: Shipments to Orders on `order_id`, and Orders to Customer CLV on `customer_unique_id`, many orders to one customer. State-month, funnel, and segment profile stay as separate sources. A physical join of shipments onto orders would store an order’s revenue once per item.

The order funnel is nested:

| Stage | Orders | Drop from the previous stage |
| --- | ---: | ---: |
| Orders placed | 99,441 | — |
| Orders with a payment record | 99,440 | 1 |
| Delivered and paid | 96,477 | 2,963 |
| Delivered, paid, and reviewed with a score from 1 to 5 | 95,831 | 646 |

The largest drop is the 2,963 orders between payment and delivery, 2.98% of orders with a payment record. Delivered orders with a review, before the payment condition, number 95,832. The one-order gap is the delivered, reviewed order that has no payment row. `has_valid_review` on the orders file sums to 98,673 because it includes reviews on orders that were not delivered. That flag is not stage 4.

The packaged workbook is `deliverables/tableau/Customer_Lifetime_Value_and_Segmentation.twbx` (11,260,865 bytes). It contains two dashboards and 15 worksheets. The Customer Intelligence Dashboard places revenue, customers, average CLV, delivered orders, total orders, and average order value with a revenue treemap, the segment profile, the state-month heatmap, the monthly trend, the funnel, and distance against delay. The captured screen shows:

- Total revenue R$ 13,221,498.11
- Customers 93,358
- Average CLV 62.58
- Delivered orders 96,478
- Average order value R$ 137.04, which is delivered product revenue divided by the 96,478 delivered orders
- Segment counts 13,144, 52,727, 15,220, and 12,267
- Funnel 99,441, 99,440, 96,477, and 95,831

The Total Orders tile on that capture reads **96,683**. That is 99,441 minus the 2,758 orders with no CLV segment. Those 2,758 orders are undelivered. The funnel on the same screen still starts at 99,441. The tile and the funnel are different counts. The published order grain remains 99,441.

Both screenshots are Tableau Desktop authoring captures, so the sheet list is visible. They are evidence that the dashboards were built. They are not cropped slides.

## 9. Week 7 Pulse metric and alert interpretation

The second dashboard is named High-Value Segment Churn Risk Pulse. The metric underneath that title is a recency watch. The status text on a customer is **Recency watch** or **Within band**. The word churn does not appear in the status field. The Olist files used here have no verified churn label, and the flag has not been checked against one.

| Rule | This snapshot |
| --- | --- |
| Population | 13,144 High Value customers, the Week 4 band |
| Reference date | 2018-08-29 15:00:37 |
| Customer flag | `recency_days > 170` |
| Why 170 | 2 × the High Value median recency of 85 days |
| Flagged | 2,051 customers, 15.60% |
| Within band | 11,093 customers, 84.40% |
| Recency exactly 170 days | 47 customers, none flagged |
| Indicator | Alert |

High Value recency on the extract runs from 0 to 370 days (median 85, mean 98.29, 75th percentile 144, 90th percentile 201, 95th percentile 231). A cut at the median would flag about half the segment and would not work as a watch list. A cut at the 90th percentile of this same file would force the share to about 10% by construction. One hundred and seventy days is a reusable assumption. The share can move on a later extract. It was not fitted to a churn rate.

The indicator uses two further assumptions. Alert when the flagged share is above 10% and at or below 20%. Escalation when the share is above 20%. Ten percent of 13,144 is 1,314.4 customers, so the alert also means 1,315 or more flagged customers. Twenty percent means 2,629 or more. This snapshot is Alert. It is not Escalation.

At Alert, the documented action is to review the watch list in the same week and prepare a re-engagement test on a sample with a holdout. It is not a launch to the whole High Value segment, and it is not a blanket discount. Every High Value customer has a review, and the segment average is 4.998, so the list is a silence list. Week 5 already showed that 94.61% of High Value customers have one delivered order. Silence after one order is the common pattern, including among customers who reviewed the order at 5.

The Tableau parameters are the recency threshold (default 170), the alert share (default 10%), and the escalation share (default 20%). Calculated fields apply those parameters to `recency_days`. The stored `risk_flag` remains the audit result at 170 days. The KPI sheet stays unfiltered so the denominator remains 13,144. The screen cannot see orders placed after 29 August 2018.

## 10. Leadership recommendations

Each row is a hypothesis. The objective names what a future test would be judged on.

| Audience | What the extract shows | Test to design | Read the test on |
| --- | --- | --- | --- |
| High Value | Highest average CLV (82.35), review near 5, median recency 85 days, 25.10% of revenue from 14.08% of customers. Median frequency is still 1. 94.61% have one delivered order. | A second-order offer: early access or a reward, on a sample. | Later delivered orders, and median recency of the segment. |
| Medium-High Value | 52,727 customers and R$ 6,532,268.84. Repeat share 2.73%. | A repeat-purchase offer or a recommendation test inside this band. | Second-order rate and delivered product revenue in the band. |
| Medium Value | Lowest average and median monetary value of the four bands (R$ 104.99 and R$ 69.90). Median frequency 1. | A small engagement test. Do not scale it first. | A later delivered order. |
| Low Value | Average review 1.352 on R$ 1,773,336.84 of delivered revenue. Average spend is above the two middle bands. | Service recovery and a support follow-up after a low review, before any discount test. | The next observed review score, then the second-order rate. |
| São Paulo | 41,746 orders, 41.98% of all orders. Rio de Janeiro and Minas Gerais are the next markets. | A regional offer in São Paulo with a comparison in other states. Keep the CLV definition unchanged. | Orders and delivered revenue against the comparison states. |
| Pulse watch list | 2,051 High Value customers with recency above 170 days. Status is Alert. | Review the list. If a message is sent, use a holdout that was also flagged. | Later delivered orders in the contacted group and in the holdout. |

The practical sequence is to protect the recent high-score relationship, earn a second order from the large middle of the revenue base, repair the review experience where the score is weak, and use São Paulo as the first geographic test. The pulse chooses who on the High Value list is silent. It does not choose the product, and it does not estimate incremental revenue.

## 11. Validation and performance improvements

The Week 8 join-and-formula audit reloaded the complete files. It did not use a sample for any count.

| Result | Checks |
| --- | ---: |
| Pass | 33 |
| Fail | 0 |
| Warning | 11 |
| Not verified at the time of that audit | 2 |
| Total | 46 |

The two items not verified in that pass were presentation checks: the rendered Week 6 workbook was not in the repository then, and the Week 7 alert screen was not opened. The workbook and both screenshots were added afterwards. The package manifest records that the packaged file opens, that both dashboards are inside it, and that the screenshots display the locked figures in sections 8 and 9. This summary does not relabel those two R1 rows as a new formal pass. The joins, the RFM inputs, the CLV formula, the revenue definition, the funnel, and the pulse rule were executed on the full data.

What the passing checks established:

- The CLV score recomputed on 93,358 customers with a maximum absolute difference of 0.
- Delivered product revenue is R$ 13,221,498.11 at every layer that uses that definition.
- Segment counts are 13,144, 52,727, 15,220, and 12,267.
- The pulse flags 2,051 of 13,144 High Value customers, and 47 customers at exactly 170 days stay unflagged.
- The Week 6 preparation script passed 28 of 28 grain and reconciliation checks.

The quarterly forecast was also recomputed. Six complete quarters, 2017 Q1 through 2018 Q2, each receive a separate ordinary-least-squares line. The 2018 Q2 holdout has MAE 2,131.225 customers per segment and MAPE 12.465%. A naive repeat of the previous quarter has MAE 4,741.5. Forward 2018 Q3 predictions are High 11,420.20, Medium-High 52,934.73, Medium 16,237.00, and Low 12,122.73. Partial quarters are 2016 Q3, 2016 Q4, and 2018 Q3. The 2018 Q3 snapshot, which refits quintiles inside the quarter, counts High Value at 12,905. That figure is not the baseline. The baseline High Value count is 13,144.

Two performance changes were measured and kept. Neither rewrote a published extract.

| Path | Before | After | Check |
| --- | --- | --- | --- |
| ZIP-prefix lookup | 0.429 s median, 137.0 MB working frame | 0.050 s median, 79.2 MB | 19,010 prefixes identical. Rebuilt distances within 4.55e-13 of the stored file. 555 missing on both sides |
| Week 6 export script | 2.336 s, peak RSS 445.8 MB | 2.151 s, peak RSS 371.2 MB | All 9 files in `data/tableau/` byte-identical. 28 checks passed. Week 2–5 hashes unchanged |

The lookup change drops the unused city string and replaces a Python mode callback with the same tie break. The script change reads only the columns it checks or writes. Joins, the quarterly cores, and the other notebooks were already under half a second for the data work and were left in place. Parquet, a database, rounding of money columns, and a shared Plotly library were considered and not implemented, because each would have changed finished files for a gain the timings did not justify.

The runtime used for those timings was Python 3.12.14, pandas 3.0.5, and NumPy 2.5.2. `requirements.txt` records pandas 3.0.5.

## 12. Limitations and future improvements

These limits are part of the method. They are not open defects in the arithmetic.

| Topic | What is true | What remains open |
| --- | --- | --- |
| CLV definition | The score is a 0–100 index of observed RFM and reviews. | A monetary CLV model would need a purchase-rate model, a margin, and a horizon. None of those was estimated. |
| Repeat behaviour | 97.0% of scored customers have one delivered order. Frequency score 1 also contains the two-order customers. | The score cannot separate loyalty that the extract barely contains. |
| Equal weights | 50/50 is the published baseline. Other weights were scored and not adopted. | The weights are a design choice, not a fitted importance. |
| Pulse | 2,051 customers sit above 170 days. The indicator is Alert. | The flag is a simulated recency watch. It is not a verified churn prediction, and it has no false-positive rate against actual churn. |
| Forecast | The holdout line beats a naive repeat on this one cut (MAE 2,131.225 against 4,741.5). | The series has six complete quarters. The forecast is exploratory. It is not an operating plan and it is not a monetary lifetime value. |
| Snapshot labels | The 2018 Q3 High Value count is 12,905 because quintiles were refit inside the quarter. | Quote 13,144 as the High Value result. |
| Geolocation | The median of in-box rows, with duplicate pings kept, reproduces the stored distances. | Dropping 261,831 exact duplicate rows would move 14,174 of 19,010 prefix coordinates and 98,200 shipment distances by more than 0.01 km. Fifty-seven would move by more than 10 km. The maximum change is 799.13 km. CLV does not use the coordinate. |
| Unmatched geography | 278 customer rows and 7 sellers miss a ZIP prefix. | 555 of 112,650 shipments have no distance. |
| Tableau order tile | The funnel starts at 99,441. | The Total Orders tile displays 96,683 because it excludes 2,758 orders with no segment. Those are different metrics. |
| Workbook portability | Five Hyper extracts are inside the `.twbx`. Opening them does not require the source folder. | Five connection entries still store the absolute directory `/Users/victo/Documents/CODING/PythonProjects/customer-lifetime-value/data/tableau`. A refresh on another machine would look for that path. |
| Causation | Segment, state, and distance results describe the extract. | No campaign result exists. Distance and delay are weakly associated. The analysis does not identify the cause of a review, a late delivery, or a second purchase. |
| Category and text | 610 products have no category and 13 use a name the translation table does not contain. Review comments are optional. | CLV does not use category or comment text. A cross-sell claim would need that analysis. |
| Package | The working directory holds the nine raw tables and the processed extracts. | Those folders are gitignored. A clone does not reproduce the results until they are restored. |

Future work that would change the claim, rather than restyle the dashboard, is a monetary CLV with an explicit horizon, a second-order model that accepts the 97% one-order base, a service-recovery test on Low Value with the next review as the outcome, and a geolocation sensitivity published beside any distance figure. A live pulse would need a new scored extract built with the same formula. Changing 170 days, or the 10% and 20% cuts, would be a new assumption and would have to be written down with the result.

## 13. Final conclusion

The engine does what it was built to do. From nine Olist tables it produces one row for each of 99,441 orders and one score for each of 93,358 customers with a delivered order. The score is half the RFM index and half the review index, with the RFM index kept where the review is missing. The bands at 80, 60, and 40 contain 13,144, 52,727, 15,220, and 12,267 customers. Delivered product revenue of R$ 13,221,498.11 reconciles across the customer file, the segment profile, the state-month grid, and the Tableau extract. The recomputed CLV score differs from the stored score by 0.

The commercial picture is concentrated and still mostly a first purchase. Medium-High Value contributes 49.41% of delivered product revenue. High Value contributes 25.10% from 14.08% of customers and reviews at 4.998. Low Value reviews at 1.352 while spending more, on average, than the two middle bands. São Paulo accounts for 41.98% of orders. The High Value recency watch flags 2,051 customers, 15.60%, and the indicator on this snapshot is Alert.

Those results are ready to brief. They become an operating system only after a test with a holdout, a monetary model if the question is future revenue, and a churn label if the question is verified leaving. None of those three is in this extract. The score, the bands, the revenue, and the recency watch are.

## Sources

Week 1 charter, data dictionary, and ER diagram; Weeks 2–5 notebooks and their published outputs; `docs/week4_methodology.md`; `docs/week5_marketing_personas.md`; the four Week 6 Tableau notes; the four Week 7 notes; `docs/week8_end_to_end_qa_report.md`; `docs/week8_performance_and_packaging_report.md`; `docs/week8_final_package_manifest.md`; the packaged workbook and the two dashboard screenshots. AI use is recorded in `docs/ai_use_disclosure.md`. There is no separate `docs/week2` or `docs/week3` note. Those weeks live in the notebooks and the processed extracts.
