# Week 7 — Validation Log

**Project:** Customer Lifetime Value & Segmentation Engine
**Extract checked:** `data/processed/olist_customer_clv.csv`
**Pulse extract:** `data/tableau/week7_high_value_risk_pulse.csv`
**Companion notes:** `docs/week7_manual_clv_qa.md`, `docs/week7_pulse_metric_implementation.md`, `docs/week7_alert_rule_and_campaign_escalation.md`

The CLV formula and the segment thresholds were not changed. No Week 1–6 notebook, output, or note was edited. Raw data was not edited.

## Population and keys

| Check | Result |
| --- | --- |
| Scored customers in the processed extract | 93,358 |
| Distinct `customer_unique_id` in the processed extract | 93,358 |
| Duplicate customer keys | 0 |
| Same keys, `clv_score`, and `customer_segment` as `data/tableau/tableau_customer_clv.csv` | Yes, 0 mismatches |
| High Value customers | 13,144 |
| Rows in the pulse extract | 13,144 |
| Distinct `customer_unique_id` in the pulse extract | 13,144 |
| Duplicate keys in the pulse extract | 0 |
| `customer_segment` values in the pulse extract | High Value only |
| Reference date on every pulse row | 2018-08-29 15:00:37 |

High Value average CLV on these 13,144 rows is 82.35 (unrounded mean 82.3505). Average review score is 4.998 (unrounded mean 4.997985). Median recency is 85 days. All three match the Week 5 published profile. Every High Value row has a review score. Blank `average_review_score` in the pulse file: 0.

## Manual CLV calculation

Independent recalculation from `recency_score`, `frequency_score`, `monetary_score`, and `average_review_score`, using RFM weight 0.50 and review weight 0.50.

| Check | Result |
| --- | --- |
| Sample customers | 12, covering score boundaries at 80, 60, and 40, a review score of 1, a review of 4.5, a three-order customer, and four customers with no review |
| Sample pass | 12 of 12 |
| Full-population `rfm_index` mismatches | 0 |
| Full-population `review_index` mismatches | 0 |
| Full-population `clv_score` mismatches | 0 |
| Maximum absolute difference on `rfm_index`, `review_index`, and `clv_score` | 0, tolerance 1e-6 |
| Segment mismatches against the recalculated score | 0 |

Worked rows and the selection rule are in `docs/week7_manual_clv_qa.md`.

## Segment classification

Thresholds applied to the recalculated score: High Value ≥ 80, Medium-High Value ≥ 60, Medium Value ≥ 40, Low Value below 40. A boundary score enters the higher band.

| Probe | Calculated score | Segment | Result |
| --- | ---: | --- | --- |
| `0000366f3b9a7992bf8c76cfdf3221e2` | 80 | High Value | Pass |
| `00324c9f4d710e7bac5c5ba679714430` | 60 | Medium-High Value | Pass |
| `05530f12381a5556c040029ac0036a18` | 40 | Medium Value | Pass |
| `00053a61a98854899e70ed204dd4bafe` | 30 | Low Value | Pass |
| `02e9109b7e0a985108b43e573b6afb23` | 78.33333333333333 | Medium-High Value | Pass |

Full-population segment labels match the stored labels on all 93,358 rows.

## Missing reviews

| Check | Result |
| --- | --- |
| `review_data_available = False` | 603 customers (0.65%) |
| Blank `average_review_score` and blank `review_index` on those rows | 603 of 603 |
| CLV score equal to `rfm_index` on those rows | 603 of 603 |
| Missing review treated as 0 | Not observed. The score stays on the RFM index |
| Segments among the 603 | Medium-High Value 136, Medium Value 321, Low Value 146, High Value 0 |

## Pulse threshold

Rule used to fill the file: `risk_flag = 1` when `recency_days > 170`, else 0. Status is `Recency watch` when the flag is 1 and `Within band` otherwise. `days_beyond_threshold` is `recency_days - 170` when the flag is 1, and 0 otherwise. The value 170 is `2 ×` the High Value median of 85 days.

| Check | Result |
| --- | --- |
| Rows where the flag, status, and days-beyond columns disagree with that rule | 0 |
| `risk_recency_threshold_days` | 170 on all 13,144 rows |
| Flagged (`Recency watch`) | 2,051 (15.60%) |
| Within band | 11,093 (84.40%) |
| Recency exactly 170, correctly unflagged | 47 |
| Customers called churned in the file | 0 |
| High Value recency range used before setting 170 | 0 to 370 days; median 85; mean 98.29; 75th percentile 144; 90th percentile 201 |

Alert evaluation at the documented cuts, not as a second column in the file: 15.60% is above 10% and at or below 20%, so the simulated indicator is **Alert**. It is not **Escalation**.

## What this log does and does not validate

The log validates three things: the CLV arithmetic against the stored extract, the segment bands, and the recency rule that filled the pulse file.

The Olist dataset in this project does not provide verified churn labels. The risk flags have not been validated against actual churn outcomes. Rule validation and predictive-model validation are different checks. Only the rule check was run.

The pulse file is one historical snapshot for a Tableau Public simulation. It is not a live production feed. No campaign was executed, so the log contains no campaign outcome.
