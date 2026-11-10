# Week 5 Marketing Personas

These personas describe three Week 4 CLV segments for marketing planning. They are summaries of observed purchase and review metrics. They are not psychological profiles. Demographic attributes are outside this dataset and are not part of these personas.

The segment labels and thresholds come from Week 4 and are not refit here.

- High Value: CLV score of 80 or above.
- Medium-High Value: CLV score of 60 or above and below 80.
- Medium Value: CLV score of 40 or above and below 60.
- Low Value: CLV score below 40.

Low Value is a score band. It is not a churn label and it is not an inactivity label. Every segment includes at least one customer whose latest delivered purchase falls on the analysis reference date (minimum recency is 0 days).

Monetary value is the Week 4 RFM monetary field. Revenue is delivered-order `total_product_value` from the Week 2 extract. In this run those two totals reconcile for every segment. Frequency is the number of delivered orders. Recency is days since the latest delivered purchase. Review averages omit customers with no review score. Missing reviews are not treated as zero.

The median frequency is one delivered order in every segment. The personas are therefore not divided into loyal and infrequent buyers. High Value does have the highest share of customers with two or more delivered orders, and that share is still small. Medium Value is profiled in the comparison table and is not given a fourth persona. Its average and median monetary values are the lowest of the four bands.

Marketing actions below are recommendations to test. This analysis does not estimate a causal effect.

## Comparison of the observed metrics

| Metric | High Value | Medium-High Value | Medium Value | Low Value |
| --- | ---: | ---: | ---: | ---: |
| Customers | 13,144 | 52,727 | 15,220 | 12,267 |
| Customer share | 14.08% | 56.48% | 16.30% | 13.14% |
| Average CLV score | 82.35 | 69.27 | 51.29 | 26.63 |
| Median CLV score | 83.33 | 70.00 | 51.67 | 26.67 |
| Average monetary value | R$ 252.43 | R$ 123.89 | R$ 104.99 | R$ 144.56 |
| Median monetary value | R$ 170.30 | R$ 75.00 | R$ 69.90 | R$ 80.00 |
| Delivered product revenue | R$ 3,317,992.65 | R$ 6,532,268.84 | R$ 1,597,899.78 | R$ 1,773,336.84 |
| Revenue share | 25.10% | 49.41% | 12.09% | 13.41% |
| Average frequency | 1.067 | 1.030 | 1.032 | 1.015 |
| Median frequency | 1.00 | 1.00 | 1.00 | 1.00 |
| Customers with 2 or more delivered orders | 5.39% | 2.73% | 3.12% | 1.46% |
| Average recency (days) | 98.3 | 253.8 | 278.5 | 261.3 |
| Median recency (days) | 85.0 | 244.0 | 269.0 | 242.0 |
| Minimum recency (days) | 0 | 0 | 0 | 0 |
| Average review score | 4.998 | 4.784 | 3.465 | 1.352 |
| Review coverage | 100.00% | 99.74% | 97.89% | 98.81% |

## 1. High-Value Recent Customer

**Segment definition.** Week 4 High Value: CLV score of 80 or above. This persona contains 13,144 customers (14.08% of the CLV population).

**Typical observed behaviour.** The average CLV score is 82.35 and the median is 83.33. The average monetary value is R$ 252.43 and the median is R$ 170.30, both the highest of the four segments. These customers contribute R$ 3,317,992.65 of delivered product revenue, 25.10% of the total, from 14.08% of customers. The average frequency is 1.067 and the median is 1.00. 5.39% have two or more delivered orders, the highest repeat share, while 94.61% have one. The average recency is 98.3 days and the median is 85.0 days, the most recent band. Review coverage is 100.00% and the average review score is 4.998.

**Business objective.** Keep the recent high-spend relationship and test whether more of these customers place a second delivered order.

**Possible marketing action.** Test a second-purchase offer, early access to a promotion, or a rewards offer. The offer is a test of a second order. The current frequency does not show that most of this segment already buys repeatedly.

**Metric to monitor.** The share of High Value customers with a later delivered order, and the median recency of the segment.

## 2. Medium-High Core Customer

**Segment definition.** Week 4 Medium-High Value: CLV score of 60 or above and below 80. This persona contains 52,727 customers (56.48%).

**Typical observed behaviour.** This is the largest segment and the largest revenue pool: R$ 6,532,268.84, or 49.41% of delivered product revenue. The average CLV score is 69.27. The average monetary value is R$ 123.89 and the median is R$ 75.00, below High Value and close to the Low Value median. The average frequency is 1.030 and 2.73% have two or more delivered orders. The average recency is 253.8 days and the median is 244.0 days. The average review score is 4.784 with 99.74% coverage.

**Business objective.** Increase the second-order rate in the segment that already contributes the most delivered revenue.

**Possible marketing action.** Test a repeat-purchase incentive. A cross-sell test would need a product-category analysis, which this week does not contain, so cross-sell is not claimed from these metrics.

**Metric to monitor.** The share of Medium-High customers who place a second delivered order, and delivered product revenue in the segment.

## 3. Low-Value Low-Review Customer

**Segment definition.** Week 4 Low Value: CLV score below 40. This persona contains 12,267 customers (13.14%).

**Typical observed behaviour.** The average CLV score is 26.63 and the median is 26.67. The average review score is 1.352, with 98.81% coverage. That review level is the clearest separation from the other bands. The average monetary value is R$ 144.56 and the median is R$ 80.00. Both are higher than Medium Value (R$ 104.99 average, R$ 69.90 median) and the average is also higher than Medium-High Value. Delivered revenue is R$ 1,773,336.84, 13.41% of the total. The average frequency is 1.015 and 1.46% have two or more delivered orders. The median recency is 242.0 days. The minimum recency is 0 days, so the band is not defined by a completed lapse.

**Business objective.** Learn whether a follow-up after a low review score, and a separate second-purchase offer, change the next observed review score or the second-order rate.

**Possible marketing action.** Test a review follow-up and a first-to-second-purchase offer. A product-discovery message can be tested as well. These metrics do not show which products the customer has not bought, so discovery is a test design rather than a finding. The segment remains the Week 4 score band.

**Metric to monitor.** The review score on a later delivered order, and the share of Low Value customers who place a second delivered order.

## Persona review for the dashboard wireframe

The wireframe places this review under the charts so a marketing reader sees the segment profile and the proposed tests on the same page as the revenue, geography, and funnel.

- The treemap shows where delivered revenue sits. Medium-High is the largest area. High Value is the second area and a smaller share of customers, which matches its higher monetary value.
- The heat map is a geographic and calendar view of orders. It is not a persona map. State and month filters are planned so a later dashboard can ask whether a persona's orders are concentrated, without changing the persona definition.
- The funnel is an order-quality sequence. It is not a customer-segment sequence. A segment filter in Week 6 can restrict the funnel to the orders of one persona.
- The action attached to each persona is an experiment. The wireframe states the metric that would show whether the test moved the observed behaviour.

## Limits

- The CLV score is a historical index. It is not a forecast of future spend.
- Most customers in every segment have one delivered order, so frequency separates the bands only slightly.
- Review coverage is high. The customers without a review are excluded from the average review score and remain visible in the coverage percentage.
- No campaign result is available, so none of the recommended tests has a measured effect in this dataset.
