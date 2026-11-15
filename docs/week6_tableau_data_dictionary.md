# Week 6 Tableau Source Inventory and Data Dictionary

**Project:** Customer Lifetime Value and Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce Public Dataset
**Workbook target:** Tableau Public
**Preparation script:** `src/prepare_week6_tableau_sources.py`

Python prepares these files and checks them. The dashboard itself is built in Tableau Public. These extracts do not replace the Week 4 CLV score, the segment thresholds, or the Week 5 published results.

## Source inventory

Each file is one Tableau data source, or one table inside the single relationship model named **Customer Orders**. Grains are not stacked into one flat file.

| File | Tableau name | Rows | Grain | Key | Dashboard role |
| --- | ---: | ---: | --- | --- | --- |
| `data/tableau/tableau_customer_clv.csv` | Customer CLV | 93,358 | One customer | `customer_unique_id` | Customer KPIs and segment profile |
| `data/tableau/tableau_orders.csv` | Orders | 99,441 | One order | `order_id` | Revenue, trend, heat map, filterable funnel |
| `data/tableau/tableau_shipments.csv` | Shipments | 112,650 | One order-item shipment | `order_id` + `order_item_id` | Distance and delivery delay |
| `data/tableau/tableau_state_month.csv` | State Month | 675 | One state and purchase month | `customer_state` + `purchase_month` | Reconciliation grid for the Week 5 heat map |
| `data/tableau/tableau_funnel.csv` | Funnel Stages | 4 | One funnel stage | `stage_order` | Reconciliation of the Week 5 funnel |
| `data/tableau/tableau_segment_profile.csv` | Segment Profile | 4 | One CLV segment | `customer_segment` | Reconciliation of the Week 5 segment profile |

`validation_checks.csv` and `validation_summary.json` in the same folder are the check log from the preparation script. They are not dashboard data.

## How the tables relate

Use one relationship model for the three detail tables. Leave the three summary tables as their own data sources.

```
Customer Orders  (one Tableau data source, relationships only)
  Customer CLV  1  --------<  Orders  >--------  1  Shipments
                 customer_unique_id          order_id

State Month      separate data source, no relationship
Funnel Stages    separate data source, no relationship
Segment Profile  separate data source, no relationship
```

`customer_segment` on Orders is a copy of the customer attribute. The copy does not add rows: the join used to build the file is many orders to one customer. In Tableau, do not physically join the tables again.

A relationship is not a physical join and it is not a blend. Tableau aggregates each table at its own grain, then combines the aggregates. A physical join of Shipments onto Orders would repeat an order's revenue once per item. A blend of State Month onto Orders using only `customer_state` would not line up months.

## Populations

| Population | Rule | Size |
| --- | --- | ---: |
| Orders placed | Every row in the Week 2 order extract | 99,441 |
| Delivered orders | `order_status = delivered` | 96,478 |
| Delivered product revenue | Sum of `total_product_value` on delivered orders | R$ 13,221,498.11 |
| CLV customers | Week 4 scored customers. Every one has at least one delivered order | 93,358 |
| Orders with no CLV segment | The customer has no delivered order, so Week 4 did not score them | 2,758 |
| Shipments | Week 3 order-item rows | 112,650 |
| Orders with no shipment | Week 2 orders that have no item row | 775 |

Revenue in every KPI is delivered product value. Freight is a separate field. `total_payment_value` is not the revenue figure. On delivered orders, freight sums to about R$ 2,198,275.64 and stays out of the revenue KPI.

The Week 4 score is unchanged:

`CLV score = (0.50 × RFM index) + (0.50 × review index)`

Customers with no valid review keep the RFM index. Segments are unchanged:

| Segment | `segment_sort` | Rule |
| --- | ---: | --- |
| High Value | 1 | CLV score ≥ 80 |
| Medium-High Value | 2 | CLV score ≥ 60 and < 80 |
| Medium Value | 3 | CLV score ≥ 40 and < 60 |
| Low Value | 4 | CLV score < 40 |

A score on a boundary stays in the higher band. Low Value is a score band. It is not a churn label.

## A. Customer CLV — `tableau_customer_clv.csv`

**Grain:** one row per `customer_unique_id`.
**Primary key:** `customer_unique_id` (93,358 unique, 0 missing, 0 duplicates).
**Source:** `data/processed/olist_customer_clv.csv`, copied. Scores and segments were not recalculated.

| Column | Type | Nulls | Definition | Tableau aggregation |
| --- | --- | ---: | --- | --- |
| `customer_unique_id` | string | 0 | Persistent customer identifier | `COUNTD` for customer counts. Never `COUNT` after a join |
| `recency_days` | integer | 0 | Days from the latest delivered purchase to the Week 3 reference date | `AVG` on this table |
| `frequency` | integer | 0 | Count of delivered orders | `AVG` on this table. A value of 2 or more is a repeat customer |
| `monetary` | number | 0 | Sum of delivered `total_product_value` for this customer, in BRL | `SUM` on this table equals delivered revenue. `AVG` is the segment monetary mean |
| `average_review_score` | number | 603 | Mean review score on the customer's delivered orders. Scale 1 to 5 | `AVG`. Tableau already skips nulls. Do not replace null with 0 |
| `rfm_index` | number | 0 | Week 3 RFM index, from 20 to 100 | `AVG` |
| `clv_score` | number | 0 | Week 4 CLV score, from 10 to 100 | `AVG` |
| `customer_segment` | string | 0 | Week 4 band | Dimension. Sort by `segment_sort` |
| `review_data_available` | integer 0/1 | 0 | 1 when `average_review_score` is present. 603 customers are 0 | `AVG` is review coverage |
| `segment_sort` | integer | 0 | Display order 1–4 | Sort field only. Do not sum it |

`review_data_available` and `segment_sort` are the only columns beyond the requested customer list. The flag keeps a missing review from being treated as a score of 0. The sort field keeps the four bands in score order rather than alphabetical order.

Customer-level measures belong on worksheets whose dimensions come from this table (`customer_segment`, or a single KPI with no order dimension). Placing `SUM(monetary)` on a view that lists `order_id` repeats the customer's lifetime monetary value on every order.

## B. Orders — `tableau_orders.csv`

**Grain:** one row per `order_id`.
**Primary key:** `order_id` (99,441 unique, 0 missing, 0 duplicates).
**Source:** `data/processed/olist_order_level_cleaned.csv`. `customer_segment` is attached from Customer CLV, many orders to one customer. The row count is unchanged.

| Column | Type | Nulls | Definition | Tableau aggregation |
| --- | --- | ---: | --- | --- |
| `order_id` | string | 0 | Order identifier | `COUNTD` |
| `customer_unique_id` | string | 0 | Customer on the order | `COUNTD` when the question is "how many customers ordered" |
| `order_purchase_timestamp` | datetime `YYYY-MM-DD HH:MM:SS` | 0 | Purchase timestamp | Date filter and `DATETRUNC('month', ...)` |
| `order_status` | string | 0 | Final status. Delivered, shipped, canceled, unavailable, invoiced, processing, created, approved | Filter or the delivered-revenue calculation |
| `total_product_value` | number | 0 | Item price total for the order, in BRL. Excludes freight | Use inside **Delivered Product Revenue**. Do not treat every status as revenue |
| `total_freight_value` | number | 0 | Freight total for the order, in BRL | Separate measure. Exclude from the revenue KPI |
| `total_payment_value` | number | 0 | Recorded payment total. The one order with no payment row is stored as 0 | Do not use as delivered product revenue |
| `primary_payment_type` | string | 1 | Payment type with the largest value on the order | Dimension. The null is the unpaid order |
| `customer_state` | string | 0 | Customer state code | Dimension. Geographic role State/Province, with country Brazil |
| `customer_segment` | string | 2,758 | Week 4 segment of this customer | Dimension. Blank means the customer was never scored |
| `segment_sort` | integer | 2,758 | Display order of the segment | Sort field |
| `has_payment_record` | integer 0/1 | 0 | 1 when the order appears in the payments file | Funnel stage 2. 99,440 orders |
| `is_delivered` | integer 0/1 | 0 | 1 when `order_status` is delivered | 96,478 orders. This is not, by itself, funnel stage 3 |
| `has_valid_review` | integer 0/1 | 0 | 1 when the order has a review score from 1 to 5 | Not funnel stage 4 until payment and delivery are also true |

The three flags and `segment_sort` support the filterable funnel and the sort. They were collapsed to order grain before the file was written, so payment rows and review rows do not multiply orders.

Blank `customer_segment` is concentrated in orders that were never delivered: shipped 1,047, unavailable 576, canceled 544, invoiced 298, processing 287, created 4, approved 2. Every delivered order has a segment. Leave the blank blank. A fifth segment name would invent a score.

Status counts: delivered 96,478; shipped 1,107; canceled 625; unavailable 609; invoiced 314; processing 301; created 5; approved 2.

## C. State and month — `tableau_state_month.csv`

**Grain:** one row per observed `customer_state` and observed `purchase_month`.
**Composite key:** `customer_state` + `purchase_month` (675 unique rows, 0 duplicate keys).
**Grid:** 27 states × 25 purchase months. The 25 months are the months that contain at least one order anywhere. November 2016 is inside the calendar span and is omitted because it has no orders. Cells with no orders are stored as zeros so the rectangle matches the Week 5 heat map. Those zeros are empty combinations, not imputed states.

| Column | Type | Nulls | Definition | Tableau aggregation |
| --- | --- | ---: | --- | --- |
| `customer_state` | string | 0 | Customer state code | Dimension |
| `purchase_month` | string `YYYY-MM` | 0 | Purchase month | Discrete dimension. Sort alphabetically, which is chronological |
| `purchase_month_date` | date `YYYY-MM-DD` | 0 | First day of `purchase_month` | Use when a continuous date axis is required |
| `distinct_order_count` | integer | 0 | Distinct `order_id` in that state and month, all statuses | `SUM`. The column is already a distinct count. `SUM` across the grid is 99,441 |
| `delivered_order_count` | integer | 0 | Distinct delivered `order_id` in that cell | `SUM`. The grid total is 96,478 |
| `total_product_revenue` | number | 0 | Delivered `total_product_value` in that cell, in BRL | `SUM`. The grid total is R$ 13,221,498.11 |

`purchase_month_date` and `delivered_order_count` are included so the month can be a real date and so order volume is not read as if it were delivered volume. `distinct_order_count` includes every status. `total_product_revenue` includes delivered orders only.

September 2018 has 16 placed orders and no delivered revenue. October 2018 has 4 placed orders and no delivered revenue. 110 of the 675 cells have a zero order count.

This file has no `customer_segment`. A segment control cannot filter it. Build the interactive heat map from Orders. Use this file to confirm the unfiltered grid.

## D. Funnel — `tableau_funnel.csv`

**Grain:** one row per stage.
**Primary key:** `stage_order`.
**Stages are nested.** An order is in a stage only if it is also in every earlier stage. Distinct `order_id` values are counted. Payment rows and review rows are not counted.

| `stage_order` | `stage_name` | Rule | `order_count` | `conversion_percentage` | `drop_off_count` | `percentage_of_initial_orders` |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Orders Placed | Every order | 99,441 | 100 | 0 | 100 |
| 2 | Orders with Payment Records | Stage 1 and a payment row | 99,440 | 99.998994 | 1 | 99.998994 |
| 3 | Delivered Orders | Stage 2 and status delivered | 96,477 | 97.020314 | 2,963 | 97.019338 |
| 4 | Orders with Valid Reviews | Stage 3 and a review score from 1 to 5 | 95,831 | 99.330410 | 646 | 96.369707 |

`conversion_percentage` is the share of the previous stage. Stage 1 is 100. `percentage_of_initial_orders` is the share of orders placed. Both are on a 0–100 scale.

Stage 3 is not "every delivered order." Status delivered contains 96,478 orders. One of those orders has no payment row, so the nested rule stops it before the delivered stage. That order is `bfbd0f9bdef84302105ad712db648a6c`: delivered, product value R$ 134.97, payment value R$ 0, no payment type. Its product value remains inside delivered revenue.

`has_valid_review` on the order file means "this order has a valid score," including orders that never reached stage 3. Funnel stage 4 requires all three flags.

This four-row file does not respond to a segment or date filter. The interactive funnel is calculated from Orders. This file is the unfiltered benchmark.

## E. Segment profile — `tableau_segment_profile.csv`

**Grain:** one row per baseline segment.
**Primary key:** `customer_segment`.
**Customer metrics** come from Customer CLV. **Revenue** is the sum of delivered `total_product_value` for customers in the segment. The two totals match: the largest absolute gap between a customer's `monetary` and the sum of that customer's delivered product value is under R$ 0.000001 (floating-point noise).

Percent fields are stored on a 0–100 scale so they match Week 5. In Tableau, format them as a number with a percent sign. Tableau's built-in percent format multiplies by 100 and would show about 1,408% for High Value.

| Column | Type | Definition | Safe aggregation on this file |
| --- | --- | --- | --- |
| `customer_segment` | string | Segment name | Dimension |
| `segment_sort` | integer | Display order 1–4 | Sort only |
| `customer_count` | integer | Customers in the band | `SUM` |
| `customer_percentage` | number, 0–100 | Share of 93,358 customers | Already a share. Display it. Do not divide by the customer total again |
| `average_clv_score` | number | Mean CLV score | Display the value. `AVG` is safe because the grain is one row. `SUM` is not |
| `average_monetary` | number | Mean `monetary`, rounded to cents as in Week 5 | Display the value |
| `total_product_revenue` | number | Delivered product revenue, in BRL | `SUM` |
| `revenue_share` | number, 0–100 | Share of delivered product revenue | Display the value. The four shares sum to 100 |
| `average_frequency` | number | Mean delivered-order count | Display the value |
| `average_recency` | number | Mean `recency_days` | Display the value |
| `average_review_score` | number | Mean review score among customers who have a score | Display the value. Customers without a score are already excluded |

Published profile:

| Segment | Customers | Customer % | Average CLV | Average monetary | Delivered revenue | Revenue share | Average frequency | Average recency | Average review |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High Value | 13,144 | 14.08% | 82.35 | R$ 252.43 | R$ 3,317,992.65 | 25.10% | 1.067 | 98.3 days | 4.998 |
| Medium-High Value | 52,727 | 56.48% | 69.27 | R$ 123.89 | R$ 6,532,268.84 | 49.41% | 1.030 | 253.8 days | 4.784 |
| Medium Value | 15,220 | 16.30% | 51.29 | R$ 104.99 | R$ 1,597,899.78 | 12.09% | 1.032 | 278.5 days | 3.465 |
| Low Value | 12,267 | 13.14% | 26.63 | R$ 144.56 | R$ 1,773,336.84 | 13.41% | 1.015 | 261.3 days | 1.352 |

The interactive profile should be aggregated from Customer CLV with `AVG`, so the segment parameter works. Use this four-row file as the unfiltered benchmark. `AVG(clv_score)` on Customer CLV, with no filter, reproduces `average_clv_score`.

## F. Shipments — `tableau_shipments.csv`

**Grain:** one row per order item shipped. This is the Week 3 shipment grain.
**Composite key:** `order_id` + `order_item_id` (112,650 unique rows, 0 duplicate keys, 0 missing keys).
**Coverage:** 98,666 distinct orders. The other 775 orders have no item row and are absent here. Every shipment `order_id` exists in Orders. Each order has one customer state on its shipment rows.

`order_item_id` is part of the key, so Tableau can tell two items on the same order apart. `is_delivered_order` is required for the delay average. Week 3 calculated delay for any row with both a delivered date and an estimated date, then excluded non-delivered rows from the average.

| Column | Type | Nulls | Definition | Tableau aggregation |
| --- | --- | ---: | --- | --- |
| `order_id` | string | 0 | Order identifier | `COUNTD` for orders. `COUNT` of rows is a shipment count |
| `order_item_id` | integer | 0 | Item sequence inside the order | Part of the key |
| `customer_state` | string | 0 | Customer state | Dimension |
| `seller_state` | string | 0 | Seller state | Dimension |
| `distance_km` | number | 555 | Great-circle distance in kilometres. Missing distances were not filled in | `AVG`. Do not sum |
| `delivery_delay_days` | number | 2,454 | Delivered date minus estimated date, in days. Negative means early | `AVG` only where `is_delivered_order = 1` |
| `is_delivered_order` | integer 0/1 | 0 | 1 when the order status is delivered | Filter or the delay calculation |

Of the delay values, 8 delivered shipments have no delay, and 7 non-delivered shipments do have a delay. Those 7 rows are why the average must test `is_delivered_order` rather than "delay is not null."

Distance describes the shipment. It does not depend on delivery outcome. Week 3 averaged distance over shipments with a non-null distance, and averaged delay over delivered shipments only. Keep that split.

Do not sum `total_product_value` on this table. Product value is not on this table. If a view needs both revenue and distance, use the relationship and aggregate each measure on its own table. Do not physically join the tables first.

## Fields left out on purpose

The extracts omit zip codes, cities, coordinates, seller identifiers, product identifiers, review text, payment installments, and raw timestamps other than the purchase timestamp. Those fields are not required for the Week 6 workbook, and several of them would tempt a many-to-many join (geolocation has many rows per zip prefix; payments and reviews have many rows per order).

The quarterly forecast file is not an extract. The CLV score is not a forecast of future spend, and the Week 6 story uses the observed segments.

## Reconciliation targets

These are the unfiltered totals. A date, state, or segment selection is supposed to change the order-grain sheets. It should still land on these numbers when the selection is cleared.

| Check | Target |
| --- | ---: |
| Customer CLV rows | 93,358 |
| Sum of `monetary` | R$ 13,221,498.11 |
| Orders | 99,441 |
| Delivered orders | 96,478 |
| Sum of delivered `total_product_value` | R$ 13,221,498.11 |
| Sum of state-month `distinct_order_count` | 99,441 |
| Sum of state-month `delivered_order_count` | 96,478 |
| Sum of state-month `total_product_revenue` | R$ 13,221,498.11 |
| Funnel counts | 99,441 → 99,440 → 96,477 → 95,831 |
| Segment customer counts | 13,144 + 52,727 + 15,220 + 12,267 = 93,358 |
| Segment revenue | R$ 3,317,992.65 + R$ 6,532,268.84 + R$ 1,597,899.78 + R$ 1,773,336.84 |
| Mean CLV score | 62.58 |
| Customers with two or more delivered orders | 2,801 (3.00%) |
