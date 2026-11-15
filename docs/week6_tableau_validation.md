# Week 6 Tableau Validation

**Project:** Customer Lifetime Value and Segmentation Engine
**Run:** `src/prepare_week6_tableau_sources.py`
**Result:** 28 checks passed. The check log is `data/tableau/validation_checks.csv`.

The script reads the Week 2 order extract, the Week 4 CLV table, the Week 3 shipment file, and the payment and review files used by the Week 5 funnel. It writes `data/tableau/` and then reads those CSVs back. Protected Week 2–5 files were hashed before the write and hashed again after it. The hashes match.

Week 4 scores, Week 4 thresholds, and Week 5 published totals were used as the benchmark. They were not refit.

## Reconciliation

| Question | Result | Benchmark |
| --- | ---: | --- |
| Customers | 93,358 | Week 4 CLV rows |
| Customer primary key | 0 duplicates, 0 missing | `customer_unique_id` |
| Sum of customer `monetary` | R$ 13,221,498.11 | Week 2 delivered product value |
| Largest customer-level monetary gap | under R$ 0.000001 | Same delivered orders |
| Orders | 99,441 | Week 2 rows |
| Order primary key | 0 duplicates, 0 missing | `order_id` |
| Delivered orders | 96,478 | `order_status = delivered` |
| Delivered product revenue | R$ 13,221,498.11 | Week 2 delivered `total_product_value` |
| Delivered orders with a segment | 96,478 of 96,478 | Week 4 assignment |
| Orders with a blank segment | 2,758 | Customers with no delivered order |
| State-month cells | 675 | 27 states × 25 observed months |
| State-month key | 0 duplicates | `customer_state`, `purchase_month` |
| Sum of `distinct_order_count` | 99,441 | Week 5 heat map, cell by cell |
| Sum of `delivered_order_count` | 96,478 | Delivered orders |
| Sum of `total_product_revenue` | R$ 13,221,498.11 | Week 5 revenue, cell by cell (0 cells off by more than R$ 0.01) |
| Orders with no customer state | 0 | Week 5 also found none |
| Funnel counts | 99,441 → 99,440 → 96,477 → 95,831 | Week 5, including conversion and drop-off |
| Funnel direction | Each stage is less than or equal to the previous stage | Nested order sets |
| Segment rows | 4, in score order | Week 4 bands |
| Segment customer counts | 13,144; 52,727; 15,220; 12,267 | Week 5 profile, exact |
| Segment revenue | R$ 3,317,992.65; R$ 6,532,268.84; R$ 1,597,899.78; R$ 1,773,336.84 | Week 5 profile, within R$ 0.01 |
| Customer percentages | Sum to 100 | Week 5 |
| Revenue shares | Sum to 100 | Week 5 |
| Shipment rows | 112,650 | Week 3 |
| Shipment key | 0 duplicates on `order_id` + `order_item_id` | Composite key |
| Shipment orders missing from Orders | 0 | Referential check |
| Orders with no shipment row | 775 | Orders with no item row |
| Orders with more than one shipment customer state | 0 | Week 5 state audit |
| Customers with a null review score | 603 | Week 4. The flag `review_data_available` matches the nulls |
| Source files modified by this run | None | MD5 of the Week 2–5 inputs |

Segment labels were also checked against the thresholds on every customer. High Value is only scores of 80 or more, Medium-High is 60 up to but not including 80, Medium is 40 up to but not including 60, and Low Value is below 40.

## Grain checks

The three detail grains were validated separately and were not flattened.

| Extract | Rows | Distinct key | Duplicate keys | Missing keys |
| --- | ---: | ---: | ---: | ---: |
| Customer CLV | 93,358 | 93,358 | 0 | 0 |
| Orders | 99,441 | 99,441 | 0 | 0 |
| Shipments | 112,650 | 112,650 | 0 | 0 |
| State Month | 675 | 675 | 0 | 0 |
| Funnel Stages | 4 | 4 | 0 | 0 |
| Segment Profile | 4 | 4 | 0 | 0 |

Attaching `customer_segment` to orders was a many-to-one merge. The order count before and after the merge is 99,441. Payment records and reviews were reduced to a 0/1 flag per `order_id` before they were written. The order file does not contain one row per payment or one row per review.

State-month counts use `nunique(order_id)`. Within each state-month the distinct-order count equals the row count of the order file, because that file is already one row per order. The funnel uses Python sets of `order_id`, so a second review on the same order cannot increase stage 4.

## Blending QA

This is the check against mixing grains. The safe Tableau model is in `docs/week6_tableau_implementation_guide.md`. The failures below are what the extracts were built to prevent.

| Combination | What goes wrong | Decision |
| --- | --- | --- |
| Physical join of Shipments to Orders on `order_id` | An order with two items appears twice. `SUM(total_product_value)` counts that order's revenue twice | Relationship on `order_id`, or no join. Revenue stays on Orders |
| Physical join of Orders to Customer CLV on `customer_unique_id` | Customer measures are repeated on every order. `SUM(monetary)` counts a repeat customer more than once | Relationship, many orders to one customer. Customer KPIs use only Customer CLV fields |
| One flat file of customers, orders, and shipments | Both problems above happen together | Three tables, or three files. This project uses one relationship model plus three summary sources |
| Relationship or blend from State Month to Orders on `customer_state` only | Many months match many orders. Revenue and the pre-aggregated counts no longer have a single grain | State Month stays a separate data source |
| Blend of Segment Profile onto an order view, linked only by a field that is not unique in the profile | Tableau marks the blended measure with an asterisk or repeats the profile total | Link on `customer_segment` only when the view is at segment grain, or use the profile file on its own sheet |
| `COUNT(order_id)` on Shipments | Counts items, not orders. Week 3's state-pair counts are item counts | `COUNTD(order_id)` for orders. Label a row count as shipment rows |
| `SUM(distance_km)` or `SUM(delivery_delay_days)` | Distance and delay are intensities, not additive quantities | `AVG` |
| `AVG(delivery_delay_days)` without the delivered flag | 7 non-delivered shipments have a delay value. Week 3 excluded them | Average `IF is_delivered_order = 1` |
| `ZN(average_review_score)` or replacing null with 0 | 603 customers have no score. Zero is not their review | Leave the null. `AVG` skips it |
| `SUM(total_payment_value)` or freight as the revenue KPI | Payment value and freight are different quantities. Week 5 revenue is delivered product value | `SUM` of product value where status is delivered |
| Quick filter that ticks the four segment names on Orders | Tableau drops the 2,758 orders with a blank segment. Stage 1 of the funnel falls below 99,441 | Segment parameter whose "All segments" value keeps blank segments |
| Funnel stage 3 defined as `is_delivered = 1` | That count is 96,478. The published stage is 96,477 because one delivered order has no payment | Stage 3 requires `has_payment_record = 1` and `is_delivered = 1` |
| Segment filter applied to State Month, Funnel Stages, or Segment Profile | Those files have no customer, or already one row per segment. The filter cannot recompute them | Interactive sheets read Orders or Customer CLV. Summary files are the unfiltered benchmark |

Data blending is the legacy primary/secondary link. It is not required for this workbook. Relationships cover Customer CLV, Orders, and Shipments. The summary files are separate worksheets, which avoids a blend on a non-unique key.

## Dates and types

| Field | Check |
| --- | --- |
| `order_purchase_timestamp` | All 99,441 values match `YYYY-MM-DD HH:MM:SS`. None are missing |
| `purchase_month` | All 675 values match `YYYY-MM`. Range 2016-09 through 2018-10, with 2016-11 absent |
| `purchase_month_date` | All 675 values match `YYYY-MM-DD` and are the first of the month |
| Measures | After the CSVs were read back, customer, order, state-month, shipment, funnel, and segment measures are numeric |
| Review nulls | 603 null scores. The same 603 rows have `review_data_available = 0`. Empty CSV cells were not written as the text `nan` |

Observed months are 2016-09, 2016-10, 2016-12, then every month from 2017-01 through 2018-10. November 2016 is reported here and is not given a zero column, matching Week 5.

## Missing values that were kept

| Field | Missing | Treatment |
| --- | ---: | --- |
| `average_review_score` | 603 customers | Left null |
| `customer_segment` on orders | 2,758 orders | Left blank. None of these orders are delivered |
| `segment_sort` on orders | 2,758 orders | Left blank with the segment |
| `primary_payment_type` | 1 order | The delivered order with no payment row |
| `total_payment_value` | 0 | The unpaid order is stored as 0 by the Week 2 extract. Four orders in total have payment value 0 |
| `customer_state` | 0 orders | No state code was filled in |
| `seller_state` | 0 shipments | |
| `distance_km` | 555 shipments | Left null. `AVG` ignores them |
| `delivery_delay_days` | 2,454 shipments | Left null. 8 of these are delivered |

No geographic code, review score, or segment was imputed.

## Funnel arithmetic

| Stage | Orders | Share of orders placed | Share of previous stage | Drop-off |
| --- | ---: | ---: | ---: | ---: |
| Orders Placed | 99,441 | 100% | 100% | 0 |
| Orders with Payment Records | 99,440 | 99.999% | 99.999% | 1 |
| Delivered Orders | 96,477 | 97.019% | 97.020% | 2,963 |
| Orders with Valid Reviews | 95,831 | 96.370% | 99.330% | 646 |

The largest drop is 2,963 orders between payment and delivery, 2.98% of orders with a payment record. The review drop is 646 orders, 0.67% of the delivered funnel stage.

The Week 2 payment flag matches the distinct `order_id` set in the payments file. Stage 2 is that set. Stage 4 uses review scores from 1 to 5 only.

## Segment distribution

| Segment | Customers | Share | Delivered revenue | Revenue share |
| --- | ---: | ---: | ---: | ---: |
| High Value | 13,144 | 14.08% | R$ 3,317,992.65 | 25.10% |
| Medium-High Value | 52,727 | 56.48% | R$ 6,532,268.84 | 49.41% |
| Medium Value | 15,220 | 16.30% | R$ 1,597,899.78 | 12.09% |
| Low Value | 12,267 | 13.14% | R$ 1,773,336.84 | 13.41% |
| Total | 93,358 | 100% | R$ 13,221,498.11 | 100% |

These are the Week 5 figures. Average CLV, average monetary value, frequency, recency, and review score on the profile file were computed from the same customer rows and the same delivered orders. Review averages omit the customers with no score. Repeat shares, confirmed again from the customer extract, are 5.39%, 2.73%, 3.12%, and 1.46%. Median frequency is 1 in every segment. Minimum recency is 0 days in every segment.

## State and month spot checks

| State | Distinct orders | Share of 99,441 |
| --- | ---: | ---: |
| SP | 41,746 | 41.98% |
| RJ | 12,852 | 12.92% |
| MG | 11,635 | 11.70% |
| RS | 5,466 | 5.50% |
| PR | 5,045 | 5.07% |

| Month | Distinct orders |
| --- | ---: |
| 2017-11 | 7,544 |
| 2018-01 | 7,269 |
| 2018-03 | 7,211 |
| 2018-04 | 6,939 |
| 2018-05 | 6,873 |

2018-09 has 16 orders and R$ 0 delivered revenue. 2018-10 has 4 orders and R$ 0 delivered revenue. Those orders stay in `distinct_order_count`.

## Warnings to carry into Tableau

1. **Blank segment.** 2,758 orders have no CLV segment. A filter that lists only the four names drops them. "All segments" on the parameter keeps them. Delivered revenue does not include them.
2. **Two delivered counts.** Status delivered is 96,478. Funnel stage 3 is 96,477. The difference is order `bfbd0f9bdef84302105ad712db648a6c`.
3. **Two grains of "orders" on the state-month file.** `distinct_order_count` is every status. `total_product_revenue` is delivered product value. September and October 2018 show orders and zero revenue for that reason.
4. **Summary files ignore the segment parameter.** Filter the interactive sheets from Orders and Customer CLV. Use State Month, Funnel Stages, and Segment Profile to confirm the totals above when every filter is cleared.
5. **Delay average.** Restrict it to `is_delivered_order = 1`. Seven non-delivered shipments would otherwise enter the mean. A negative delay is an early delivery.
6. **Percent fields on the summary files are already 0–100.** Format them as numbers. Calculated shares built with `TOTAL()` are 0–1 ratios and should use Tableau's percent format.
7. **CLV does not change with the purchase-date filter.** The score is a lifetime index on the customer table. Apply the date filter to order-grain sheets only. A date-filtered customer average would still be the lifetime score of the customers who remain, which is a different question from "CLV in that month."
8. **Do not republish raw files.** The Tableau extracts contain pseudonymous customer ids, state codes, and order values. They do not contain review text, full addresses, or zip codes.

## Rerun

From the project root, with the existing virtual environment:

```bash
.venv/bin/python src/prepare_week6_tableau_sources.py
```

The script fails if a reconciliation check fails, and it refuses to leave a changed hash on the Week 2–5 inputs. It writes only under `data/tableau/`.
