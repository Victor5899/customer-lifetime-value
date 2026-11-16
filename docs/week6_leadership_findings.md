# Customer Lifetime Value & Segmentation Engine
## Week 6 — Leadership Findings & Campaign Recommendations

This note translates the Week 4 CLV segmentation and the Week 5 segment, geography, and funnel results into findings for leadership. The population is 93,358 scored customers from the Olist Brazilian E-Commerce Public Dataset. Every scored customer has at least one delivered order. Revenue is delivered product value and totals R$ 13,221,498.11. Freight and recorded payment value are excluded.

Segment labels and thresholds are unchanged from Week 4:

- High Value: CLV score of 80 or above.
- Medium-High Value: CLV score of 60 or above and below 80.
- Medium Value: CLV score of 40 or above and below 60.
- Low Value: CLV score below 40.

A score on a boundary stays in the higher band. The figures below are the published Week 5 segment profile, reconciled to the customer extract and to the state-month order grid.

### 1. Executive Summary

Four value bands describe the scored customer base. Medium-High Value is the core of the business: 52,727 customers, 56.48% of the base, contributing R$ 6,532,268.84, or 49.41% of delivered product revenue. High Value is smaller, at 13,144 customers (14.08%), but contributes R$ 3,317,992.65 (25.10%) and has the strongest observed experience. Medium Value and Low Value account for 16.30% and 13.14% of customers and 12.09% and 13.41% of delivered product revenue.

Customer value, experience, repeat purchase, and geography point to different actions.

- **Customer value.** Revenue is concentrated. The two upper bands together account for 70.56% of customers and 74.50% of delivered product revenue. Medium-High Value is the largest pool. High Value produces more revenue per customer.
- **Customer experience.** The CLV score gives equal weight to the RFM index and the review index. High Value reviews average 4.998. Low Value reviews average 1.352. The Low Value band is not explained by low spend alone: its average delivered product value, R$ 144.56, is above Medium-High Value (R$ 123.89) and Medium Value (R$ 104.99).
- **Repeat purchases.** The median number of delivered orders is 1.00 in every segment. Of 93,358 scored customers, 90,557 (97.0%) have exactly one delivered order and 2,801 (3.0%) have two or more. Retention work is a test of a second order, not a programme for an already loyal base.
- **Geographic concentration.** In the state-month grid of all 99,441 orders, São Paulo accounts for 41,746 orders (41.98%). Rio de Janeiro (12,852; 12.92%) and Minas Gerais (11,635; 11.70%) are the next largest states. São Paulo is the practical place to test a regional campaign before a wider rollout.

The recommendations in this note are experiments. No campaign has been run on this dataset, so none of them has a measured result.

### 2. Five Leadership Findings

#### Finding 1 — Medium-High Value customers are the core revenue segment

| Measure | Result |
| --- | ---: |
| Customers | 52,727 |
| Share of scored customers | 56.48% |
| Delivered product revenue | R$ 6,532,268.84 |
| Share of delivered product revenue | 49.41% |
| Average CLV score | 69.27 |

**Interpretation.** This is the largest segment and the largest revenue contributor. It holds more than half of scored customers and just under half of delivered product revenue. The average CLV score of 69.27 sits inside the 60-to-80 band. Average delivered product value is R$ 123.89, below High Value, so the segment's revenue rank comes from its size. The median delivered-order count is 1.00, and 2.73% of these customers have two or more delivered orders. The commercial question is how to earn a second order from the customers who already produce the most revenue, not how to find a hidden high-spend niche inside the band.

**Campaign recommendation.** Test loyalty campaigns, personalised product recommendations, and targeted repeat-purchase offers with Medium-High Value customers. Judge the test by the share who later place a second delivered order, and by delivered product revenue in the segment. A cross-sell claim would need a product-category analysis, which this project does not contain.

#### Finding 2 — High Value customers demonstrate the strongest customer experience

| Measure | Result |
| --- | ---: |
| Customers | 13,144 |
| Share of scored customers | 14.08% |
| Delivered product revenue | R$ 3,317,992.65 |
| Share of delivered product revenue | 25.10% |
| Average CLV score | 82.35 |
| Average review score | 4.998 (approximately 5.00) |
| Median recency | 85 days |

**Interpretation.** High Value has the highest average CLV score of the four bands. Review coverage is 100.00%, and the average review score of 4.998 is effectively a top-box score. Recency is measured back from 29 August 2018, the latest delivered purchase in the extract. The median of 85 days and the average of 98.3 days are the most recent figures of the four bands. The other medians are 244 days (Medium-High Value), 269 days (Medium Value), and 242 days (Low Value). Spend is also the highest: average delivered product value is R$ 252.43 and the median is R$ 170.30. These customers are 14.08% of the base and 25.10% of revenue. Repeat purchasing is still limited: average frequency is 1.067, the median is 1.00, and 5.39% have two or more delivered orders. The relationship to protect is recent, high-spend, and well reviewed. It is not yet a repeat-purchase relationship for most of the segment.

**Campaign recommendation.** Test VIP loyalty benefits, early access to selected products, and exclusive customer rewards. The offer should be framed as a test of whether more of these customers place a second delivered order. Monitor the share with a later delivered order and the median recency of the segment.

#### Finding 3 — Low Value customers have a significant review-experience problem

| Measure | Result |
| --- | ---: |
| Customers | 12,267 |
| Share of scored customers | 13.14% |
| Delivered product revenue | R$ 1,773,336.84 |
| Share of delivered product revenue | 13.41% |
| Average CLV score | 26.63 |
| Average review score | 1.352 (approximately 1.35) |

**Interpretation.** Low Value is the Week 4 score band below 40. It is not a churn label and it is not an inactivity label. Minimum recency in this band is 0 days, so at least one customer purchased on the analysis reference date. The average review score of 1.352, with 98.81% review coverage, is the clearest separation from the other bands. Medium Value averages 3.465, Medium-High Value averages 4.784, and High Value averages 4.998. Spend does not explain the low score. Average delivered product value is R$ 144.56 and the median is R$ 80.00, both above Medium Value (R$ 104.99 and R$ 69.90). The average is also above Medium-High Value. The lower CLV score is strongly influenced by poor review experience. A discount aimed only at "low spenders" would miss that evidence. The band still contributes R$ 1,773,336.84, so the experience problem sits on a material revenue pool.

**Campaign recommendation.** Prioritise service recovery. Investigate product and delivery complaints, and test a customer-support follow-up after a low review score before offering discounts. A separate second-purchase offer can be tested afterwards. The metrics to watch are the review score on a later delivered order and the share of Low Value customers who place a second delivered order.

#### Finding 4 — The customer base has limited repeat-purchase behaviour

| Measure | Result |
| --- | ---: |
| Scored customers | 93,358 |
| Customers with exactly one delivered order | 90,557 (97.0%) |
| Customers with two or more delivered orders | 2,801 (3.0%) |
| Median delivered orders, every segment | 1.00 |
| Week 3 frequency score of 1 | 93,130 customers (99.76%) |

**Interpretation.** Repeat purchasing is limited across the observed customer base. The median is one delivered order in High Value, Medium-High Value, Medium Value, and Low Value. The repeat shares are small even where they are highest: 5.39% in High Value, 3.12% in Medium Value, 2.73% in Medium-High Value, and 1.46% in Low Value. Frequency therefore adds little separation to the CLV score. The score depends mainly on recency, monetary value, and reviews.

The 99.76% figure needs a precise reading. It is the share of customers given a Week 3 frequency score of 1, not the share with one order. Because almost everyone ordered once, a standard five-bin split was not possible, and the distinct-value fallback placed both one-order and two-order customers in score 1. Counted directly from the customer extract, 97.0% have exactly one delivered order. Both figures support the same business point: a second purchase is uncommon. They should not be quoted as the same statistic.

**Campaign recommendation.** Test post-purchase engagement, relevant replenishment reminders, and personalised recommendations to encourage a second purchase. Run the test inside a defined segment so the result can be read against that segment's current second-order rate. This analysis does not show which products are replenished, so a reminder is a test design rather than a finding about a product cycle.

#### Finding 5 — São Paulo is the dominant customer market

| Measure | Result |
| --- | ---: |
| Orders from São Paulo (SP) | 41,746 |
| Share of orders in the state-month grid | 41.98% |
| Orders in the state-month grid | 99,441 |
| Next largest states | Rio de Janeiro 12,852 (12.92%); Minas Gerais 11,635 (11.70%) |

**Interpretation.** São Paulo represents a substantial share of order activity: 41,746 of 99,441 orders, or 41.98%. The state-month grid counts orders of every status, by customer state and purchase month. It is an order geography, not a map of the four personas, and the 41.98% is a share of orders rather than a share of scored customers. November 2017 is the largest month in the same grid, with 7,544 orders. September 2018 (16 orders) and October 2018 (4 orders) appear in the order counts and contribute no delivered revenue, because purchases in those months were not delivered inside the extract. São Paulo is large enough to support a focused test. It is not evidence that a São Paulo offer will outperform the same offer elsewhere.

**Campaign recommendation.** Test region-specific promotions and targeted marketing campaigns in São Paulo. Compare campaign performance with other states, starting with Rio de Janeiro and Minas Gerais, before expanding. Keep the CLV segment definition unchanged when the geography filter is applied.

### 3. Consolidated Marketing Campaign Strategy

Each row is a hypothesis. The objective names what the test would be judged on. It does not state an effect that has already been observed.

| Customer segment or market | Observed business insight | Recommended campaign | Primary business objective |
| --- | --- | --- | --- |
| High Value | Highest average CLV score (82.35), review score near 5, and the most recent purchases (median recency 85 days). Contributes 25.10% of delivered product revenue from 14.08% of customers. Median frequency is still 1.00. | Test VIP loyalty benefits, early access to selected products, and exclusive rewards aimed at a second delivered order. | Retain the recent high-spend relationship and learn whether more of these customers place a second delivered order. |
| Medium-High Value | Largest segment and largest revenue pool: 52,727 customers (56.48%) and R$ 6,532,268.84 (49.41%). Average CLV score 69.27. Repeat rate 2.73%. | Test loyalty campaigns, personalised product recommendations, and targeted repeat-purchase offers. | Increase the second-order rate in the segment that already contributes the most delivered revenue. |
| Medium Value | Mid-score band between the core revenue segment and Low Value. Week 5 places its average and median monetary value lowest of the four bands. Median frequency is 1.00, as in the other bands. | Test targeted engagement and personalised recommendations. Do not scale the offer until the test shows a later delivered order. | Increase engagement and test whether a relevant recommendation produces a second delivered order. |
| Low Value | Average CLV score 26.63 with an average review score of 1.352. Average spend is higher than Medium Value and Medium-High Value, so the band is an experience problem on R$ 1,773,336.84 of delivered revenue. The label is not a churn label. | Prioritise service recovery. Investigate product and delivery complaints, and test a support follow-up before a discount. | Learn whether a follow-up after a low review changes the next observed review score, before spending on discounts. |
| São Paulo market | 41,746 orders, 41.98% of the 99,441 orders in the state-month analysis. The next two states are materially smaller. | Test region-specific promotions and targeted campaigns in São Paulo, with a comparison group in other states. | Learn whether a regional offer changes orders or delivered revenue in São Paulo relative to states that do not receive it. |

### 4. Leadership Conclusion

Five priorities follow from the evidence.

1. **Retain High Value customers.** They combine the highest CLV score, the strongest reviews, the most recent purchases, and a disproportionate share of revenue. The retention offer should be tested against a second delivered order, because 94.61% of this segment have only one.
2. **Encourage repeat purchases among Medium-High Value customers.** This is the core revenue segment. A small change in its second-order rate matters more than the same change in a smaller band, because the band already holds 49.41% of delivered product revenue.
3. **Improve the experience of Low Value customers.** The score band reflects reviews near 1.35 more than it reflects low spend. Service recovery and a support follow-up come before a discount test.
4. **Increase engagement among Medium Value customers.** Treat targeted engagement and personalised recommendations as a test. This note does not assign Medium Value a separate numerical finding beyond the published Week 5 profile.
5. **Use geographic concentration to guide regional marketing tests.** Start with São Paulo, where 41.98% of orders are concentrated, and compare the result with other states before expanding.

The practical sequence is to protect the customers who already review well and spend more, earn a second order from the large middle of the revenue base, repair the review experience where it is weak, and use São Paulo as the first geographic test. None of those actions should be reported as a completed result.

### 5. Methodological Notes and Limitations

- The CLV score is a 0–100 composite customer value and experience index. In this run it ranges from 10.00 to 100.00, with a mean of 62.58 and a median of 66.67.
- It combines RFM and review scores. The baseline formula, for a customer with a valid review, is `CLV score = (0.50 × RFM index) + (0.50 × review index)`. The RFM index rescales the Week 3 recency, frequency, and monetary scores from 1–5 onto 20–100. The review index rescales the average review from 1–5 onto 0–100.
- Customers with no valid delivered-order review (603 customers, 0.65%) keep the RFM index. Their missing review is not treated as zero and is excluded from average review scores.
- The CLV score is not a prediction of future monetary customer lifetime revenue. It is not expressed as a forecast in Brazilian reais. A financial lifetime-value model would estimate purchases the customer has not yet made. This project does not calculate that quantity.
- Low Value does not automatically mean churned or at-risk. It is the score band below 40. Every segment includes at least one customer whose latest delivered purchase falls on the analysis reference date.
- Campaign recommendations are hypotheses to test, not proven causal outcomes. No campaign experiment has been conducted, so this note does not claim that any recommendation has generated revenue, retention, or a change in review score.
- The analysis is based on historical Olist dataset observations. Delivered purchases in the Week 4 extract run from 15 September 2016 to 29 August 2018. Recency is days from the latest delivered purchase back to 29 August 2018.
- Customer segmentation and revenue figures use the existing Week 4 and Week 5 definitions. Week 5 monetary value and delivered product revenue reconcile for every segment. The state-month share uses all 99,441 orders, not only delivered orders. Funnel stage 3, delivered orders with a payment record, is 96,477. Orders with status delivered number 96,478. The difference is one delivered order with no payment record.
- Most customers placed one delivered order, so frequency adds little separation. The Week 3 frequency score of 1 (99.76% of customers) groups one-order and two-order customers together. The direct count is 90,557 customers (97.0%) with exactly one delivered order.
- Segment results describe association in the historical extract. They do not identify the cause of a review score, a delivery outcome, or a second purchase.
