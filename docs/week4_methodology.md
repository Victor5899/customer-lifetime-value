# Week 4 Methodology — CLV Score, Segmentation, and Forecast Validation

This note describes the Week 4 customer-value score for the Olist Brazilian E-Commerce Public Dataset. The executable source is `notebooks/04_week4_clv_analysis.ipynb`. Figures in the results section are written by that notebook from the run that produced the output files.

## CLV score formula

The Week 4 CLV score is a customer-level index from 0 to 100. It combines the Week 3 RFM scores with the customer's average review score. It is a historical value-and-experience score.

A financial CLV, denominated in currency, would estimate purchases the customer has not yet made. This project does not calculate that quantity, and the score is not expressed in Brazilian reais.

Baseline formula, for a customer with a valid review:

`CLV_score = (0.50 * rfm_index) + (0.50 * review_index)`

## RFM component

Recency, Frequency, and Monetary scores are taken from `data/processed/olist_customer_rfm.csv`. Week 4 does not refit those scores for the current customer table. Each score is an integer from 1 to 5, using the Week 3 quintile rules: lower recency receives a higher score, and higher frequency and monetary value receive higher scores. Frequency is too concentrated for a standard five-bin `qcut`, so Week 3 used a distinct-value quantile fallback. Week 4 leaves that result in place.

`rfm_index = ((recency_score + frequency_score + monetary_score) / 15) * 100`

The index runs from 20, when every score is 1, to 100, when every score is 5.

## Review score component

Reviews are read from `data/raw/olist_order_reviews_dataset.csv` and linked to `customer_unique_id` through the Week 2 order extract. The path is nested:

1. Keep review rows with a score from 1 to 5.
2. Keep reviews whose order has final status `delivered`, so the review population matches the RFM population.
3. Average the score at `order_id`. Every review row counts in `review_count`. An order with disagreeing scores keeps the mean of those scores.
4. Average the order-level scores at `customer_unique_id`. Each reviewed order has equal weight. `reviewed_order_count` is the number of those orders.

`review_index = ((average_review_score - 1) / 4) * 100`

A review score of 1 maps to 0 and a score of 5 maps to 100.

There were no exact duplicate review rows. Some `review_id` values repeat on different `order_id` values with the same score, message, and creation date. Those rows are kept, because each one is the review evidence for a different order. `review_id` is not the grain. Reviews on non-delivered orders are excluded from the score and counted in the notebook.

The availability time of a review is `review_creation_date`. The seller answer timestamp is not used as that time.

## Missing review treatment

Customers with no valid delivered-order review keep a null `average_review_score` and a null `review_index`. Their count fields are 0, which records the absence of review rows and does not assign a score of 0. Their CLV score is the RFM index. That is the general rule of dropping the missing component and dividing by the remaining weight: with only the RFM weight left, the result equals `rfm_index`. These customers are flagged with `review_data_available = False`.

## Weight configuration

Weights are stored in `CLV_WEIGHTS` and checked to sum to 1. The baseline is RFM 0.50 and review 0.50. The notebook also scores RFM 0.70 / review 0.30 and RFM 0.30 / review 0.70 under the baseline thresholds. Quarterly history and the forecast use the 50/50 baseline. Customers without a review stay on the RFM index under every weight pair, because renormalization still has only one observed component.

## Segment thresholds

Segments are value bands of the CLV score. Low Value is the band below the medium threshold. It is not a churn label and it is not an 'at risk' label.

- High Value: score ≥ 80
- Medium-High Value: score ≥ 60 and < 80
- Medium Value: score ≥ 40 and < 60
- Low Value: score < 40

A score on a boundary enters the higher band. `assign_customer_segment(clv_score, thresholds)` is the only assignment function, and it reads the threshold dictionary it is given. In Tableau the same three cut-points would be parameters compared with the CLV score.

## Threshold simulation

Scenario A uses 80 / 60 / 40. Scenario B uses 85 / 65 / 45. Scenario C uses 75 / 55 / 35. Each scenario reports customer count, share of customers, average CLV score, average monetary value (R$), average frequency, and average recency (days). The saved comparison is `data/output/week4_segment_threshold_scenarios.csv`.

## Quarterly snapshot methodology

An active customer at a snapshot has at least one delivered order purchased on or before the cutoff. This is a cumulative population. New delivered customers, whose first delivered purchase falls inside the snapshot window, are reported as a separate flow.

A quarter is complete when the observed span covers its first and last day and every month in the quarter has a delivered purchase. Complete quarters, and partial quarters whose calendar end is still inside the span, close at the calendar quarter end. The closing quarter of the extract uses the latest observed purchase timestamp as its cutoff, because the calendar quarter continues past the data.

Inside a snapshot, orders purchased after the cutoff are excluded, recency is measured from the cutoff, and reviews created after the cutoff are excluded. RFM quintiles are fit on that snapshot's customers with the unchanged Week 3 helper. The current CLV table continues to use the published Week 3 scores. Final order status is used because the extract has no status history; purchase time and review time are censored exactly.

## Forecast method

The target is the cumulative number of customers in each segment. The selected model is a separate ordinary least-squares line for each segment, fit on complete quarters only:

`customers = intercept + slope * quarter_index`

Predictions are constrained to be at least zero. If fewer than three complete quarters were available, the notebook would use a last-quarter baseline instead of a line and would say so in the output. The forward forecast is the next calendar quarter after the last complete quarter. Partial actuals for an unfinished quarter are not the accuracy target.

## Forecast validation

The latest complete quarter is held out. The line is fit on the earlier complete quarters and compared with that holdout. MAE is the unweighted mean of the four absolute errors. MAPE is the unweighted mean of the absolute percentage errors where the actual count is not zero. Percentage error is signed: positive means the forecast is above the actual. A naive forecast that repeats the previous complete quarter is stored beside the linear errors as a benchmark.

## Limitations

- The score is an index of observed RFM and reviews. It is not a currency forecast of future purchases.
- Most customers placed one delivered order, so frequency adds little separation. The score depends mainly on recency, monetary value, and reviews.
- Customers without reviews are scored on RFM alone. Their index is not imputed from other customers' reviews.
- Snapshot segment labels use quintiles fit inside that quarter, then the fixed CLV thresholds. A band is therefore relative to the customers visible at the time as well as to the absolute cut-points.
- Segment stocks are cumulative. Growth in a band mixes new customers with customers whose relative scores changed.
- The order status used for eligibility is the final status.
- The complete-quarter series is short. The forecast is exploratory, and a small MAE on one holdout would still not establish a stable forecasting system.
- Segment lines are fit independently, so their sum need not match a separate forecast of the total customer count. Reported shares use the sum of the segment forecasts as the denominator.
- The Week 3 distance analysis describes association between distance and delivery delay. It does not identify a cause.

## Results from this run

- Customers: 93,358
- Customers with review data: 92,755 (99.35%)
- Customers without review data: 603 (0.65%)
- Delivered orders with a valid review: 99.33%
- CLV score range: 10.00 to 100.00 (mean 62.58, median 66.67)
- Formula weights: RFM 0.50, review 0.50
- Baseline segments:
  - High Value: 13,144 customers (14.1%), average CLV 82.4, average monetary value R$ 252.43
  - Medium-High Value: 52,727 customers (56.5%), average CLV 69.3, average monetary value R$ 123.89
  - Medium Value: 15,220 customers (16.3%), average CLV 51.3, average monetary value R$ 104.99
  - Low Value: 12,267 customers (13.1%), average CLV 26.6, average monetary value R$ 144.56
- High Value counts by threshold scenario:
  - Scenario A (80 / 60 / 40): 13,144
  - Scenario B (85 / 65 / 45): 2,326
  - Scenario C (75 / 55 / 35): 21,783
- Purchase span: 2016-09-15 12:16:38 to 2018-08-29 15:00:37
- Distinct calendar months with a delivered purchase: 23
- Elapsed coverage: 23.43 months
- Quarterly snapshots: 9
- Complete quarters: 2017Q1, 2017Q2, 2017Q3, 2017Q4, 2018Q1, 2018Q2
- Partial quarters: 2016Q3 — Observed purchases start after the calendar quarter begins. No delivered purchase in calendar month(s) 7, 8.; 2016Q4 — No delivered purchase in calendar month(s) 11.; 2018Q3 — Observed purchases end before the calendar quarter ends. No delivered purchase in calendar month(s) 9.
- Latest observed comparison (2018Q2 to 2018Q3, latest complete = False):
  - All active customers: 81,265 to 93,358 (absolute change 12,093; 14.9%)
  - High Value: 10,385 to 12,905 (absolute change 2,520; 24.3%)
  - Medium-High Value: 46,008 to 52,748 (absolute change 6,740; 14.6%)
  - Medium Value: 14,023 to 15,487 (absolute change 1,464; 10.4%)
  - Low Value: 10,849 to 12,218 (absolute change 1,369; 12.6%)
- Forecast method: linear_trend
- Holdout quarter: 2018Q2
- MAE: 2,131.23 customers per segment
- MAPE: 12.47%
- Naive last-quarter MAE: 4,741.50 customers per segment
- Forward forecast quarter: 2018Q3
  - High Value: 11,420 customers (12.3% of the forecast total)
  - Medium-High Value: 52,935 customers (57.1% of the forecast total)
  - Medium Value: 16,237 customers (17.5% of the forecast total)
  - Low Value: 12,123 customers (13.1% of the forecast total)

## Outputs

- `data/processed/olist_customer_clv.csv`
- `data/processed/olist_quarterly_customer_segments.csv`
- `data/output/week4_clv_summary.csv`
- `data/output/week4_segment_threshold_scenarios.csv`
- `data/output/week4_quarterly_segment_trends.csv`
- `data/output/week4_segment_forecast.csv`
- `data/output/week4_forecast_validation.csv`
- `docs/week4_mid_project_deck.pptx`
