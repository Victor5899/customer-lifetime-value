# Week 7 — Manual CLV Quality Assurance

**Project:** Customer Lifetime Value & Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce Public Dataset
**Requirement:** R1, QA the CLV logic against a manual sample calculation
**Source extract:** `data/processed/olist_customer_clv.csv`
**Check date of the method:** the formula and thresholds in `docs/week4_methodology.md` and `notebooks/04_week4_clv_analysis.ipynb`

This note recalculates the published CLV score from the stored RFM component scores and the stored average review. It does not change the formula, the weights, or the segment thresholds. Week 4 does not refit the 1–5 RFM scores, so this check does not re-bin recency, frequency, or monetary value. Those scores remain the Week 3 inputs.

## Fields used

The processed customer extract has one row per `customer_unique_id`. The columns read for this check are:

| Column | Role in the check |
| --- | --- |
| `customer_unique_id` | Customer key |
| `recency_days` | Days from the latest delivered purchase to the reference date. Reported, not re-derived |
| `frequency` | Count of delivered orders. Reported, not re-derived |
| `monetary` | Delivered product value in Brazilian reais. Reported, not re-derived |
| `recency_score`, `frequency_score`, `monetary_score` | Week 3 scores, integers 1 to 5 |
| `average_review_score` | Mean review on delivered orders, or blank when no valid review exists |
| `rfm_index`, `review_index`, `clv_score` | Stored results compared with the recalculation |
| `review_data_available` | `True` or `False` |
| `customer_segment` | Stored segment compared with the recalculated band |

`data/tableau/tableau_customer_clv.csv` carries the same 93,358 customer keys, the same `clv_score`, and the same `customer_segment`. It does not carry the three RFM component scores, so the arithmetic uses the processed extract.

Recency on both files is measured from the Week 3 reference date **2018-08-29 15:00:37**, the latest delivered `order_purchase_timestamp`. `recency_days` is the number of whole days between that timestamp and the customer's latest delivered purchase.

## Formula under test

Weights: RFM 0.50 and review 0.50. The weights sum to 1.

```
rfm_index = (recency_score + frequency_score + monetary_score) / 15 * 100
review_index = (average_review_score - 1) / 4 * 100
```

When a review is present:

```
clv_score = (0.50 * rfm_index) + (0.50 * review_index)
```

When `average_review_score` is missing, `review_index` stays missing. The review term is dropped and the remaining weight is the RFM weight, so:

```
clv_score = (0.50 * rfm_index) / 0.50 = rfm_index
```

A missing review is not scored as 0.

Segment assignment, with a boundary score entering the higher band:

| Condition | Segment |
| --- | --- |
| `clv_score` ≥ 80 | High Value |
| `clv_score` ≥ 60 and < 80 | Medium-High Value |
| `clv_score` ≥ 40 and < 60 | Medium Value |
| `clv_score` < 40 | Low Value |

Agreement rule: absolute difference at most 1e-6 on `rfm_index`, `review_index`, and `clv_score`, and an exact segment label. A blank review index matches only a blank stored review index.

## Sample

Twelve customers. Each role keeps the lexicographically first `customer_unique_id` that matches it. The first High Value customer with recency above 170 days is also the first High Value repeat customer, so the single-order watch role uses the first High Value customer with `frequency = 1` and `recency_days > 170`.

| Role | `customer_unique_id` |
| --- | --- |
| High Value, score exactly 80, review 5, one order | `0000366f3b9a7992bf8c76cfdf3221e2` |
| High Value, two delivered orders, recency 227 | `004288347e5e88a27ded2bb23747066c` |
| High Value, recency 0 | `0421e7a23f21e5d54efed456aedbc513` |
| High Value, one order, recency 180 | `0064a1b5f5cddd047c987b988a90c8c1` |
| Medium-High Value, score exactly 60 | `00324c9f4d710e7bac5c5ba679714430` |
| Medium Value, score exactly 40, no review | `05530f12381a5556c040029ac0036a18` |
| Low Value, review score 1 | `00053a61a98854899e70ed204dd4bafe` |
| Medium Value, no review | `00bee19e1199bc5cede1c674177b9e22` |
| Medium-High Value, no review | `025cf7c2f32536f0be1ab412bb6602d2` |
| Low Value, no review | `049ac10f22b18d0a463429e2dfbbb353` |
| Fractional review 4.5 | `000bfa1d2f1a41876493be685390d6d3` |
| Three delivered orders, fractional review | `02e9109b7e0a985108b43e573b6afb23` |

Monetary values are delivered product value in Brazilian reais.

### 1. High Value boundary — `0000366f3b9a7992bf8c76cfdf3221e2`

Recency 111 days. Frequency 1. Monetary R$ 129.90. Scores 4, 1 and 4. Review 5.0.

```
rfm_index = (4 + 1 + 4) / 15 * 100 = 60
review_index = (5 - 1) / 4 * 100 = 100
clv_score = 0.50 * 60 + 0.50 * 100 = 80
```

Stored CLV 80. Segment High Value, because 80 meets the high threshold. **Pass.**

### 2. High Value repeat customer — `004288347e5e88a27ded2bb23747066c`

Recency 227 days. Frequency 2. Monetary R$ 317.89. Scores 3, 1 and 5. Review 5.0.

```
rfm_index = (3 + 1 + 5) / 15 * 100 = 60
review_index = (5 - 1) / 4 * 100 = 100
clv_score = 0.50 * 60 + 0.50 * 100 = 80
```

Stored CLV 80. Segment High Value. **Pass.** Frequency 2 does not by itself raise the score above the RFM sum. This customer is also past the Week 7 recency watch of 170 days.

### 3. High Value, purchased on the reference date — `0421e7a23f21e5d54efed456aedbc513`

Recency 0 days. Frequency 1. Monetary R$ 109.90. Scores 5, 1 and 3. Review 5.0.

```
rfm_index = (5 + 1 + 3) / 15 * 100 = 60
review_index = 100
clv_score = 80
```

Stored CLV 80. Segment High Value. **Pass.**

### 4. High Value, one order, recency 180 — `0064a1b5f5cddd047c987b988a90c8c1`

Recency 180 days. Frequency 1. Monetary R$ 215.60. Scores 3, 1 and 5. Review 5.0.

```
rfm_index = (3 + 1 + 5) / 15 * 100 = 60
review_index = 100
clv_score = 80
```

Stored CLV 80. Segment High Value. **Pass.**

### 5. Medium-High boundary — `00324c9f4d710e7bac5c5ba679714430`

Recency 433 days. Frequency 1. Monetary R$ 29.90. Scores 1, 1 and 1. Review 5.0.

```
rfm_index = (1 + 1 + 1) / 15 * 100 = 20
review_index = 100
clv_score = 0.50 * 20 + 0.50 * 100 = 60
```

Stored CLV 60. Segment Medium-High Value, because a score of 60 enters that band and does not enter High Value. **Pass.**

### 6. Medium boundary, no review — `05530f12381a5556c040029ac0036a18`

Recency 576 days. Frequency 1. Monetary R$ 113.00. Scores 1, 1 and 4. Review missing. `review_data_available` is False. Stored `review_index` is blank.

```
rfm_index = (1 + 1 + 4) / 15 * 100 = 40
review_index = missing
clv_score = rfm_index = 40
```

Stored CLV 40. Segment Medium Value. **Pass.** The missing review stays missing. It is not inserted as 0, which would have produced `0.50 * 40 + 0.50 * 0 = 20` and a Low Value label.

### 7. Low Value with review score 1 — `00053a61a98854899e70ed204dd4bafe`

Recency 182 days. Frequency 1. Monetary R$ 382.00. Scores 3, 1 and 5. Review 1.0.

```
rfm_index = (3 + 1 + 5) / 15 * 100 = 60
review_index = (1 - 1) / 4 * 100 = 0
clv_score = 0.50 * 60 + 0.50 * 0 = 30
```

Stored CLV 30. Segment Low Value. **Pass.** The monetary score is 5 and the review index is 0. The low band here comes from the review term.

### 8. Medium Value, no review — `00bee19e1199bc5cede1c674177b9e22`

Recency 284 days. Frequency 1. Monetary R$ 649.90. Scores 2, 1 and 5. Review missing.

```
rfm_index = (2 + 1 + 5) / 15 * 100 = 53.333333333333336
review_index = missing
clv_score = 53.333333333333336
```

Stored CLV 53.333333333333336. Segment Medium Value. **Pass.**

### 9. Medium-High Value, no review — `025cf7c2f32536f0be1ab412bb6602d2`

Recency 12 days. Frequency 1. Monetary R$ 1,788.00. Scores 5, 1 and 5. Review missing.

```
rfm_index = (5 + 1 + 5) / 15 * 100 = 73.33333333333333
review_index = missing
clv_score = 73.33333333333333
```

Stored CLV 73.33333333333333. Segment Medium-High Value. **Pass.** A review score of 5 would have raised the score. The renormalisation rule leaves it on the RFM index.

### 10. Low Value, no review — `049ac10f22b18d0a463429e2dfbbb353`

Recency 302 days. Frequency 1. Monetary R$ 19.90. Scores 2, 1 and 1. Review missing.

```
rfm_index = (2 + 1 + 1) / 15 * 100 = 26.666666666666668
clv_score = 26.666666666666668
```

Stored CLV 26.666666666666668. Segment Low Value. **Pass.**

### 11. Fractional review — `000bfa1d2f1a41876493be685390d6d3`

Recency 334 days. Frequency 1. Monetary R$ 35.00. Scores 2, 1 and 1. Review 4.5.

```
rfm_index = (2 + 1 + 1) / 15 * 100 = 26.666666666666668
review_index = (4.5 - 1) / 4 * 100 = 87.5
clv_score = 0.50 * 26.666666666666668 + 0.50 * 87.5 = 57.083333333333336
```

Stored CLV 57.083333333333336. Segment Medium Value. **Pass.**

### 12. Three delivered orders — `02e9109b7e0a985108b43e573b6afb23`

Recency 107 days. Frequency 3. Monetary R$ 532.87. Scores 4, 2 and 5. Review 4.333333333333333.

```
rfm_index = (4 + 2 + 5) / 15 * 100 = 73.33333333333333
review_index = (4.333333333333333 - 1) / 4 * 100 = 83.33333333333333
clv_score = 0.50 * 73.33333333333333 + 0.50 * 83.33333333333333 = 78.33333333333333
```

Stored CLV 78.33333333333333. Segment Medium-High Value. The score is below 80, so it does not enter High Value. **Pass.**

## Sample result

| Customer | Calculated CLV | Stored CLV | Calculated segment | Stored segment | Review handling | Result |
| --- | ---: | ---: | --- | --- | --- | --- |
| `0000366f3b9a7992bf8c76cfdf3221e2` | 80 | 80 | High Value | High Value | Review present | Pass |
| `004288347e5e88a27ded2bb23747066c` | 80 | 80 | High Value | High Value | Review present | Pass |
| `0421e7a23f21e5d54efed456aedbc513` | 80 | 80 | High Value | High Value | Review present | Pass |
| `0064a1b5f5cddd047c987b988a90c8c1` | 80 | 80 | High Value | High Value | Review present | Pass |
| `00324c9f4d710e7bac5c5ba679714430` | 60 | 60 | Medium-High Value | Medium-High Value | Review present | Pass |
| `05530f12381a5556c040029ac0036a18` | 40 | 40 | Medium Value | Medium Value | Missing review equals RFM index | Pass |
| `00053a61a98854899e70ed204dd4bafe` | 30 | 30 | Low Value | Low Value | Review score 1 maps to index 0 | Pass |
| `00bee19e1199bc5cede1c674177b9e22` | 53.333333333333336 | 53.333333333333336 | Medium Value | Medium Value | Missing review equals RFM index | Pass |
| `025cf7c2f32536f0be1ab412bb6602d2` | 73.33333333333333 | 73.33333333333333 | Medium-High Value | Medium-High Value | Missing review equals RFM index | Pass |
| `049ac10f22b18d0a463429e2dfbbb353` | 26.666666666666668 | 26.666666666666668 | Low Value | Low Value | Missing review equals RFM index | Pass |
| `000bfa1d2f1a41876493be685390d6d3` | 57.083333333333336 | 57.083333333333336 | Medium Value | Medium Value | Fractional review | Pass |
| `02e9109b7e0a985108b43e573b6afb23` | 78.33333333333333 | 78.33333333333333 | Medium-High Value | Medium-High Value | Fractional review | Pass |

Twelve of twelve sample rows pass. The same function was then applied to all 93,358 rows. Every `rfm_index`, `review_index`, `clv_score`, and `customer_segment` matched. The maximum absolute difference on each numeric field was 0, inside the 1e-6 tolerance. All 603 customers with `review_data_available = False` have a blank review index and a CLV score equal to `rfm_index`.

## Limitations

- The check confirms the Week 4 arithmetic and the 80 / 60 / 40 bands. It does not re-create the Week 3 quintile scores from raw recency, frequency, and monetary value.
- Recency days and monetary amounts were taken from the extract. They were not recomputed from order lines in this note.
- High Value in this extract has a review for every customer (13,144 of 13,144). The missing-review cases sit in Medium-High Value (136), Medium Value (321), and Low Value (146).
- A pass means the stored score follows the documented formula. It does not mean the score forecasts future revenue in Brazilian reais.
