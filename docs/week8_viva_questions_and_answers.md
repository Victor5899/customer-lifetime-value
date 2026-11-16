# Week 8 — Viva Questions and Answers

**Project:** Customer Lifetime Value and Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce Public Dataset
**Date:** 16 November 2026
**Numbered questions:** 45

Use the 60-second introduction to open. Use the 2-minute explanation if the examiner asks how the score is built. Use the 5-minute walkthrough if the slot is short. The slide file is paced at 8–10 minutes; speaker notes in `deliverables/submission/Final_Project_Presentation.pptx` carry that longer version. The answers below stay inside the published extracts and the Week 8 audits.

Figures to keep in your head: 99,441 orders; 96,478 delivered; 93,358 scored customers; R$ 13,221,498.11 delivered product revenue; segments 13,144 / 52,727 / 15,220 / 12,267; one delivered order 90,557 (97.0%); pulse 2,051 of 13,144 (15.60%), threshold 170 days, status Alert.

## 60-second project introduction

This project scores customers in the Olist Brazilian e-commerce public dataset. The business question is who carries the observed value, where the review experience is weak, and which High Value customers have gone quiet on the 29 August 2018 snapshot.

Nine raw tables were audited and left unchanged. The integration step produces one row for each of 99,441 orders. The customer step keeps people with at least one delivered order: 93,358 customers and R$ 13,221,498.11 of delivered product revenue. Freight is excluded.

The CLV score is a 0–100 index: half the RFM index and half the review index. If the review is missing, the score is the RFM index. It is a value-and-experience index of purchases already made. Bands at 80, 60, and 40 give 13,144 High Value customers, 52,727 Medium-High, 15,220 Medium, and 12,267 Low. Medium-High contributes 49.41% of delivered product revenue. High Value contributes 25.10% from 14.08% of customers. Low Value reviews average 1.352.

A Week 7 pulse flags High Value customers whose last delivered purchase is more than 170 days before the snapshot. That is 2,051 customers, 15.60%, and the indicator is Alert. The flag is a recency watch. The extract has no verified churn label. Ninety-seven percent of scored customers have exactly one delivered order, so the recommendations are tests of a second order and of service recovery, not measured campaign results.

## 2-minute technical explanation

Start from the grain. `customer_id` matches orders one to one. `customer_unique_id` is the person: 96,096 people, some with several orders, up to 17 order rows and up to 15 delivered orders. RFM groups delivered orders by `customer_unique_id`. That is why the customer file has 93,358 rows rather than 99,441 or 96,096. The 2,738-person gap is people with no delivered order.

Week 2 aggregates items and payments to `order_id` before joining, so the order extract stays at 99,441 rows. Seven hundred and seventy-five orders have no items and stay in the file with product value 0. One delivered order has no payment. Its R$ 134.97 stays in delivered revenue and stays out of funnel stage 3, which is why delivered orders are 96,478 and the paid-and-delivered stage is 96,477.

Recency is whole days back to 2018-08-29 15:00:37. Frequency is the count of delivered orders. Monetary value is delivered product value. Recency and monetary scores are five-bin quantiles. Frequency is not, because 90,557 customers ordered once. Score 1 covers frequency 1 and 2, which is 99.76% of customers. Quote 97.0% for the one-order share and 99.76% only for frequency score 1.

The RFM index is the sum of the three scores divided by 15, times 100. The review index rescales the average delivered-order review from 1–5 onto 0–100. Reviews are averaged at the order, then at the customer. `review_id` is not unique, so it is not the grain. The CLV score is 0.50 times each index. Six hundred and three customers have no review; their score equals the RFM index. A missing review is not a zero. The maximum absolute difference when the score was recomputed on all 93,358 rows was 0.

Tableau keeps separate grains: 93,358 customers, 99,441 orders, 112,650 shipments, 675 state-months, 4 funnel stages, and 4 segment rows. Relationships aggregate before they combine. A physical join of shipments to orders would repeat revenue. The Total Orders tile shows 96,683 because 2,758 orders have no segment. The funnel still starts at 99,441. Those are different metrics.

The pulse keeps the 13,144 High Value customers and flags `recency_days > 170`, twice the High Value median of 85. Forty-seven customers at exactly 170 days are not flagged. The share 15.60% sits above 10% and at or below 20%, so the status is Alert.

## 5-minute presentation walkthrough

**Opening.** The project is a customer value and experience index on the Olist public marketplace data, from September 2016 to 29 August 2018. I will cover the grain, the score, the four bands, the two dashboards, and the limits.

**Problem.** Leadership needs to know where delivered revenue sits and where the review experience fails. The score does not estimate future spend in reais, and the pulse does not predict churn.

**Data.** Nine tables. Orders and customers are both 99,441 rows because `customer_id` is order-scoped. The person key is `customer_unique_id`, with 96,096 people. Items are 112,650, payments 103,886, reviews 99,224. `review_id` repeats. The ZIP prefix is not a primary key: 19,015 prefixes across 1,000,163 geolocation rows. The ER diagram is the Week 1 audit map.

**Pipeline.** Items and payments are summed to the order before the join. The cleaned file has 99,441 orders. Delivered product revenue is R$ 13,221,498.11. The all-status price sum is R$ 13,591,643.70. Payment value, R$ 16,008,872.12, is a different quantity and is not the KPI.

**RFM and CLV.** Delivered orders only: 96,478 orders, 93,358 customers. Formula: half the RFM index, half the review index. Missing review: keep the RFM index. Bands at 80, 60, and 40.

**Findings.** Medium-High is the core: 52,727 customers and 49.41% of revenue. High Value is 14.08% of customers and 25.10% of revenue, with an average review of 4.998 and median recency of 85 days. Low Value averages a review of 1.352 and still spends R$ 144.56 on average, above the two middle bands. Exactly one delivered order: 90,557 customers, 97.0%.

**Place.** São Paulo is 41,746 orders, 41.98% of 99,441. Distance and delay are very weakly associated: Pearson −0.0783, Spearman −0.1823. That is association. CLV does not use the coordinate.

**Dashboards.** The intelligence dashboard shows the locked revenue, 93,358 customers, average CLV 62.58, and the funnel from 99,441 to 95,831. Say explicitly that the Total Orders tile reads 96,683. The pulse dashboard shows 2,051 flagged, 13,144 High Value, 15.60%, and Alert. Customer status text is Recency watch or Within band.

**Trust and close.** R1: 33 passed, 0 failed, 11 warnings, 2 not verified at audit time. The CLV difference was 0. Revenue reconciles. The workbook now embeds the extracts; a refresh still points at an absolute local path. Recommendations are tests with a holdout. I will not quote the quarter-specific High Value count of 12,905 in place of 13,144, and I will not call the forecast or the pulse an operating prediction.

## Question index

| Section | Questions |
| --- | --- |
| Business problem and dataset | Q1–Q5 |
| Nine-table schema and relationships | Q6–Q9 |
| ETL, joins, and grain | Q10–Q13 |
| RFM calculations | Q14–Q17 |
| CLV formula and missing reviews | Q18–Q22 |
| Segment profiling | Q23–Q26 |
| Tableau relationships and dashboards | Q27–Q31 |
| Week 7 pulse logic and parameters | Q32–Q36 |
| QA, performance, and limitations | Q37–Q40 |
| Difficult examiner questions | Q41–Q43 |
| Leadership recommendations and design trade-offs | Q44–Q45 |

---

## Business problem and dataset

### Q1. What business problem does the project address?

Olist’s public extract shows a marketplace in which almost every scored customer has a single delivered order, while delivered product revenue is uneven across a value-and-experience score. Leadership cannot see, from the raw tables alone, which band holds the revenue, which low scores are experience problems, or which High Value customers are silent relative to their own segment. The project answers those three descriptive questions on the historical file. It prepares tests. It does not report a campaign result.

### Q2. What decision can this score support, and what decision is outside it?

The score can rank observed customers into the published bands and show how delivered product revenue, reviews, recency, and repeat purchase differ across those bands. A pricing decision, a margin decision, or a forecast of next year’s revenue needs a monetary model with a horizon and a purchase rate. Those inputs were not estimated. The honest use is targeting and diagnosis on the observed extract.

### Q3. What is the dataset, the period, and the licence constraint?

The source is the Brazilian E-Commerce Public Dataset by Olist, published on Kaggle as `olistbr/brazilian-ecommerce`. Delivered purchases in the Week 4 extract run from 15 September 2016, 12:16:38, to 29 August 2018, 15:00:37. The data charter records the licence as CC BY-NC-SA 4.0, confirmed from Kaggle’s dataset metadata, and treats the project as non-commercial. Olist anonymised the file. Company names in review text were replaced at source. The charter also says to re-check the live Kaggle listing before any use beyond this analysis.

### Q4. Why do 99,441, 96,478, 96,096, and 93,358 all appear, and which one do you defend?

Each count has a grain. 99,441 is orders, and also customer rows, because `customer_id` is one row per order. 96,478 is orders with status delivered. 96,096 is distinct `customer_unique_id` values in the customers table. 93,358 is people with at least one delivered order, which is the RFM and CLV population. The difference between 96,096 and 93,358 is 2,738 people with no delivered order. I defend 93,358 as the scored customer base and 99,441 as the order base. I do not average them or pick one number for every slide.

### Q5. What would you say in one sentence if asked for the result?

Medium-High Value is 56.48% of 93,358 scored customers and 49.41% of R$ 13,221,498.11 delivered product revenue; High Value is 14.08% of customers and 25.10% of that revenue; Low Value reviews average 1.352; and 97.0% of scored customers have one delivered order.

---

## Nine-table schema and relationships

### Q6. Why are there two customer identifiers?

`customer_id` is the order-scoped surrogate. It is unique on 99,441 rows and matches `orders.customer_id` with no unmatched row in either direction. `customer_unique_id` is the persistent person. It is not a primary key of the customers table: 96,096 distinct values, 3,345 extra rows, 2,997 people with more than one row, maximum 17 rows. RFM and CLV group by `customer_unique_id`. Grouping by `customer_id` would split repeat buyers into several people and hide the little repeat behaviour the extract does contain.

### Q7. Which identifiers failed the uniqueness test, and what did you do?

`review_id` is not unique: 98,410 distinct values, 789 repeated identifiers, 1,603 affected rows, 1,412 orders, and no exact duplicate rows. Scores are all in 1–5, with no null score. The CLV path does not join on `review_id`. It averages scores at `order_id`, then averages those order means at `customer_unique_id`. The geolocation ZIP prefix is not unique: 19,015 prefixes across 1,000,163 rows, including 261,831 exact duplicate rows. Week 3 collapses each prefix to a median coordinate before the distance join. Product, seller, order, and `customer_id` keys were unique.

### Q8. Walk through the relationships that matter for revenue and for distance.

Orders join to customers one to one on `customer_id`. Items join to orders many to one: 112,650 items, 0 items pointing at a missing order, 775 orders with no item. Payments join many to one: 103,886 payments, 0 pointing at a missing order, 1 order with no payment, 2,961 orders with more than one payment. Reviews join many to one, and 768 orders have no review row. Products and sellers match every item. Category translation misses 13 product rows, and 610 products have a null category. CLV does not use category. Customer ZIP misses geolocation on 278 rows (0.28%). Seller ZIP misses it on 7 rows (0.23%). Those gaps, plus prefixes with no in-box coordinate, leave 555 shipments without a distance.

### Q9. How should the ER diagram be read in the room?

The diagram is the Week 1 referential-integrity map, not a physical data model that was loaded into a database. Solid lines are checks that matched. Dashed lines are the warnings: the derived person-to-order link, the category-name link, and the ZIP-prefix link. Geolocation has no verified primary key. Reviews are marked because `review_id` failed uniqueness. The later pipeline respects that map by aggregating children before the order join and by collapsing ZIP prefixes before the distance join.

---

## ETL, joins, and grain

### Q10. How did Week 2 keep the order grain at 99,441?

Item prices, freight, item counts, product counts, and seller counts were aggregated to `order_id` first. The item aggregate has 98,666 orders. Payments, including the primary type, were aggregated to 99,440 orders. Those aggregates were then joined to the order header. The identifier set equals the orders table. Rebuilt sums match the stored extract within about 2.3e-13, which is binary noise, not a missing order. There is no join fanout.

### Q11. What happened to incomplete orders, and why were they kept?

Week 1’s rule was to document anomalies and not delete them silently. Orders with no items remain, with product value and freight 0 and `has_order_items` false. The order with no payment remains, with payment value stored as 0 and the primary type blank. Its id is `bfbd0f9bdef84302105ad712db648a6c`, status delivered, product value R$ 134.97, and it has a valid review. Dropping it would have made delivered revenue and the delivered-order count agree with the funnel by construction, and would have hidden a real gap. The gap is reported instead: 96,478 delivered orders, 96,477 in funnel stage 3.

### Q12. Define the revenue KPI precisely.

The KPI is the sum of `order_items.price` on orders whose status is delivered: R$ 13,221,498.11. Freight is stored and excluded. Recorded payment value is stored and excluded. The all-status price sum is R$ 13,591,643.70, equal to the raw price sum. The raw payment sum is R$ 16,008,872.12. I do not describe the payment-minus-price gap as freight, because the project did not publish that identity. They are different quantities. The primary payment type is the type with the largest summed amount on the order. Nine payment rows have amount 0, and three have type `not_defined`. They do not enter the product-revenue KPI.

### Q13. What is the path from a review row to a customer score?

Keep scores from 1 to 5. Keep reviews on orders whose final status is delivered. Average at `order_id`, so an order with disagreeing scores keeps the mean. One hundred and eighty-nine orders are in that case. Then average those order means at `customer_unique_id`, with each reviewed order weighted equally. The rebuild matched the stored average, the review count, and the reviewed-order count for all 92,755 reviewed customers, with a maximum absolute difference of 0. Reviews on non-delivered orders are excluded from the score. Comment title and comment message are not inputs. Title is null on 87,656 rows and message on 58,247 rows.

---

## RFM calculations

### Q14. How are recency, frequency, and monetary value calculated?

Eligibility is `order_status = delivered`. Recency is the whole-day gap from the customer’s latest delivered `order_purchase_timestamp` to 2018-08-29 15:00:37. Frequency is the number of distinct delivered `order_id` values for that `customer_unique_id`. Monetary value is the sum of delivered `total_product_value`. A customer who bought on the reference date has recency 0, and every segment contains at least one such customer. The recomputation matched the stored file on recency, frequency, last purchase, freight, and monetary value.

### Q15. Why is frequency score 1 assigned to both one-order and two-order customers?

A five-bin quantile needs enough distinct values to cut. Here 90,557 of 93,358 customers have frequency 1, and only 2,801 have two or more. `qcut` cannot make five populated frequency bins. The distinct-value fallback puts frequency 1 and 2 in score 1 (93,130 customers, 99.76%), 3 and 4 in score 2, 5 in score 3, 6 and 7 in score 4, and 9 and 15 in score 5. Recency and monetary scores remain ordinary five-bin quantiles, with a higher score for more recent purchases and for higher spend. Week 4 does not refit these scores for the baseline table.

### Q16. An examiner quotes 99.76% as “almost nobody bought twice.” What do you say?

That sentence uses the wrong numerator. 99.76% is the share whose frequency score is 1. Score 1 contains both one-order and two-order customers: 2,573 of the two-order customers sit in that score. Counted directly, 90,557 customers, 97.0%, have exactly one delivered order, and 2,801, 3.0%, have two or more. Both figures support the same business point, and they are not the same statistic. The repeat shares by segment are 5.39%, 2.73%, 3.12%, and 1.46%. The median in every segment is 1.00.

### Q17. What does the reference date control?

Every recency, including the Week 7 flag, is anchored at 2018-08-29 15:00:37. A customer with recency 180 was 180 days before that timestamp, not 180 days before today. The quarterly snapshots use their own cutoffs and refit quintiles inside the quarter. The baseline customer table does not. Mixing the two is how the High Value count gets misquoted as 12,905 instead of 13,144.

---

## CLV formula and missing-review treatment

### Q18. State the formula and the range of each piece.

`rfm_index = (recency_score + frequency_score + monetary_score) / 15 × 100`, from 20 to 100. `review_index = (average_review_score − 1) / 4 × 100`, from 0 to 100. `clv_score = 0.50 × rfm_index + 0.50 × review_index` when a review exists. On this file the score runs from 10.00 to 100.00, mean 62.58, median 66.67. The weights are stored, checked to sum to 1, and the published baseline is 0.50 / 0.50. The score is not expressed in reais.

### Q19. What happens when the review is missing? Give the numerical contrast.

Six hundred and three customers, 0.65%, have no valid delivered-order review. `review_index` stays missing. The missing component is dropped and the result is divided by the remaining weight, which leaves `clv_score = rfm_index`. None of these 603 customers is in High Value. They sit in Medium-High (136), Medium (321), and Low (146). They are excluded from average review scores and remain visible in the coverage percentages.

The manual sample makes the alternative concrete. Customer `05530f12381a5556c040029ac0036a18` has scores 1, 1, and 4, so the RFM index is 40, and the review is missing. The stored score is 40, Medium Value. Inserting a review index of 0 would have produced `0.50 × 40 + 0.50 × 0 = 20` and a Low Value label. The project refuses that substitution. A review score of 1 is different: it is observed, and it does map to a review index of 0. Customer `00053a61a98854899e70ed204dd4bafe` has RFM index 60 and review 1, so the CLV score is 30 and the segment is Low Value, despite a monetary score of 5.

### Q20. Show that the boundaries go into the higher band.

Customer `0000366f3b9a7992bf8c76cfdf3221e2` has scores 4, 1, and 4 and a review of 5. The RFM index is 60, the review index is 100, and the CLV score is 80. The rule is score ≥ 80 for High Value, so the customer is High Value. Customer `00324c9f4d710e7bac5c5ba679714430` has scores 1, 1, and 1 and a review of 5. The score is 60, which enters Medium-High and does not enter High Value. A customer with no review and RFM index 40 enters Medium Value. Twelve of twelve hand-worked rows matched, and the same function then matched all 93,358 stored scores and segments. The maximum absolute difference was 0, inside a 1e-6 tolerance.

### Q21. Why 50/50, and what else was tried?

Equal weights are the published baseline because the project treats purchase behaviour and review experience as joint inputs to the index. They were not estimated from a regression. The notebook also computed 0.70 RFM / 0.30 review and 0.30 RFM / 0.70 review. Customers without a review stay on the RFM index under every pair, because renormalisation still has only one observed component. Quarterly history, the forecast, and the dashboards use 50/50. If an examiner prefers another pair, the correct response is that the alternative was scored, the published segments were not rebuilt from it, and changing the weight would be a new definition rather than a correction of this one.

### Q22. What do the other threshold scenarios show?

Scenario A, the published cut, is 80 / 60 / 40 and yields 13,144 High Value customers. Scenario B, 85 / 65 / 45, yields 2,326. Scenario C, 75 / 55 / 35, yields 21,783. The same customers and the same scores sit behind all three. The count moves because the cut moves. I report 13,144. I mention B and C only to show that the band is a threshold choice and that I did not hide the sensitivity.

---

## Segment profiling

### Q23. Define the four segments with the figures you would put on a slide.

High Value, score at least 80: 13,144 customers, 14.08%, R$ 3,317,992.65, 25.10% of revenue, average CLV 82.35, average monetary value R$ 252.43, average review 4.998, median recency 85 days. Medium-High, from 60 up to but not including 80: 52,727, 56.48%, R$ 6,532,268.84, 49.41%, average CLV 69.27. Medium, from 40 up to but not including 60: 15,220, 16.30%, R$ 1,597,899.78, 12.09%, average CLV 51.29, and the lowest average and median monetary value, R$ 104.99 and R$ 69.90. Low, below 40: 12,267, 13.14%, R$ 1,773,336.84, 13.41%, average CLV 26.63, average review 1.352. The currency amounts sum to R$ 13,221,498.11. The customer counts sum to 93,358.

### Q24. Who is the “best” segment?

There is no single best segment. Medium-High is the core revenue pool because of its size. High Value has the highest average spend, the strongest reviews, and the most recent purchases, and it contributes more of the revenue than of the customers. The two upper bands together are 65,871 customers, 70.56%, and R$ 9,850,261.49, 74.50% of delivered product revenue. Low Value is the experience problem. Medium Value is the lowest-spend band and was not given a separate persona beyond the published profile. Which segment matters depends on whether the question is revenue volume, revenue per customer, or review recovery.

### Q25. Why is Low Value not a churn segment?

The label is the score band below 40. Minimum recency in the band is 0 days, so at least one Low Value customer purchased on the reference date. Review coverage is 98.81%. The average review of 1.352 is the separation from Medium Value at 3.465, Medium-High at 4.784, and High Value at 4.998. Average monetary value, R$ 144.56, is above Medium-High and Medium. The lower score is pulled by the review term, which the manual example of a review-1 customer with monetary score 5 already shows. Treating the band as churned would send a win-back offer to customers who may have bought recently and who already left a poor review.

### Q26. How should the High Value repeat rate be said out loud?

Average frequency is 1.067. The median is 1.00. The share with two or more delivered orders is 5.39%, so 94.61% have one. High Value is the highest repeat share of the four bands, and it is still a small share. The relationship the band describes is recent, higher-spend, and well reviewed. For most of the band it is not yet a repeat-purchase relationship. A VIP offer is a test of a second delivered order.

---

## Tableau relationships and dashboards

### Q27. Why are there six Week 6 files instead of one flat table?

Each file has one grain: customer, order, shipment, state-month, funnel stage, or segment. A flat file would repeat customer monetary value once per order and order revenue once per item. The preparation script checked that attaching the segment to orders left the order count at 99,441, and that payment and review inputs were reduced to a 0/1 flag per order before they were written. State-month uses `nunique(order_id)`. The funnel uses sets of `order_id`, so a second review cannot increase stage 4. The Week 6 script passed 28 checks and did not change the Week 2–5 source hashes.

### Q28. What relationship is safe, and what join doubles revenue?

The safe model relates Shipments to Orders on `order_id`, and Orders to Customer CLV on `customer_unique_id`, with Customer CLV on the one side and Orders on the many side. There is no second line from Shipments to Customer CLV. Tableau relationships aggregate each table, then combine the aggregates. A physical join of one order to two shipment rows would store that order’s revenue twice if the revenue were summed afterwards. State-month, funnel, and segment profile stay off that relationship. Linking state-month to orders on state alone would match many months to many orders. Customer KPIs use Customer CLV fields. `AVG` is the aggregation for distance, delay, and the review score. `SUM` of distance is not a distance.

### Q29. The Total Orders tile shows 96,683 and the funnel shows 99,441. Which is wrong?

Neither count is a calculation error. 99,441 minus 2,758 orders with a blank segment is 96,683. The blank segment is exactly the undelivered orders: 0 delivered orders have a blank segment, and 2,758 orders have one. A quick filter that ticks only the four segment names drops those orders. The funnel worksheet counts orders placed and still starts at 99,441 on the same screenshot. I say both numbers and name the sets. The published order grain remains 99,441. Delivered orders on the KPI tile are 96,478, which is the status count, not the tile labelled Total Orders.

### Q30. Explain the funnel, including the one-order disagreements.

Stage 1 is 99,441 orders placed. Stage 2 is 99,440 orders with a payment record. Stage 3 is 96,477 orders that are delivered and have a payment record. Stage 4 is 95,831 of those with a review score from 1 to 5. The drop of 2,963 between stage 2 and stage 3 is 2.98% of orders with a payment record. The review drop is 646, 0.67% of stage 3. Delivered status alone is 96,478. Delivered orders with a review, before requiring payment, are 95,832. Both one-order gaps are the same unpaid delivered order. `has_valid_review` sums to 98,673 because it is any order with a valid review, including orders that were not delivered. The dictionary tells the dashboard not to use that raw flag as stage 4.

### Q31. What is in the packaged workbook, and what will fail on another computer?

The file is `deliverables/tableau/Customer_Lifetime_Value_and_Segmentation.twbx`, 11,260,865 bytes, a zip archive that passed `unzip -t`. The workbook XML is version 18.1. It names seven CSV sources and stores five Hyper extracts, including one shared extract for the customer, order, and shipment relationship. No CSV is stored loose inside the package. Two dashboards contain all 15 worksheets: Customer Intelligence Dashboard, and High-Value Segment Churn Risk Pulse. Opening the embedded extracts does not require the project folder. Five connection entries still record the absolute directory `/Users/victo/Documents/CODING/PythonProjects/customer-lifetime-value/data/tableau`. A refresh on another machine would look for that path. I have not claimed that refresh is portable. The screenshots are 2940 by 1912 Tableau Desktop captures, with the authoring sidebar visible.

---

## Week 7 pulse logic and parameters

### Q32. What does the pulse measure on this snapshot?

It measures the share of the 13,144 High Value customers whose `recency_days` is strictly greater than 170. The result is 2,051 customers, 15.6041%, reported as 15.60%. The other 11,093, 84.40%, are within the band. The population is exactly the Week 4 High Value set. The reference date on every row is 2018-08-29 15:00:37. The status values stored on the file are Recency watch and Within band. The dashboard title uses the classroom name High-Value Segment Churn Risk Pulse. The metric is the recency rule. Matching the flag to the rule validates the rule. It does not validate a predictive model.

### Q33. Why 170 days, and why is equality not flagged?

The published High Value median recency is 85 days. The assumption is twice that median. High Value recency on the file runs from 0 to 370, with mean 98.29, 75th percentile 144, 90th percentile 201, 95th percentile 231, and 99th percentile 263. A cut at 85 would flag about half the segment. A cut at the 90th percentile of this same file would put about 10% on the list by construction, so the share could not move independently of the cut. A fixed 170 can be applied to a later extract and the share can rise or fall. The test is strict greater-than. Forty-seven customers at exactly 170 days stay in Within band. Moving the parameter by one day changes who is listed. The stored column `risk_recency_threshold_days` is 170 on every row. The editable Tableau parameter defaults to 170 and can be moved; after it moves, the stored audit flag stays at the 170-day result, and the reconciliation check correctly becomes false.

### Q34. How do Alert and Escalation work, and what is this snapshot?

The customer rule and the indicator are separate. The indicator looks at the flagged share of all 13,144 High Value customers. At or below 10%, no alert. Above 10% and at or below 20%, Alert. Above 20%, Escalation. Both cuts are management assumptions for the simulation. They were not fitted to a churn rate. Ten percent of 13,144 is 1,314.4, so the alert also means a flagged count of 1,315 or more. Twenty percent means 2,629 or more. 15.60% is Alert. It is not Escalation. Severity describes the size of the watch list. It does not grade a customer’s probability of leaving. Customer status stays binary.

### Q35. What must stay unfiltered, and what may be filtered?

The KPI sheet and the alert sheet use every High Value customer as the denominator. An action filter from the alert onto the KPIs would shrink that denominator and change 15.60%. The customer table may be filtered to Recency watch, and it should use the parameter-driven status rather than the stored status, because the stored status does not move when the parameter moves. At the default, that table lists 2,051 customers. There is no join from the pulse file to Orders or Customer CLV. The file is already one row per High Value customer, with 13,144 distinct ids and no duplicates.

### Q36. What would you do next week if this were a live file, and what would you refuse to do?

I would confirm the parameter is still 170, sort the 2,051 rows by recency descending, and read score, monetary value, frequency, and review before writing any offer. I would prepare a one-page test: a sample, a holdout that was also flagged, and the second-order rate to be read afterwards. I would not launch to all 13,144 High Value customers, and I would not apply a blanket discount to `risk_flag = 1`. The segment’s median frequency is already one, and its average review is 4.998, so the list is a silence list inside a base that rarely repeats. Support effort follows a complaint or a delivery problem from an operational source. This extract does not contain complaint text. The workbook cannot schedule an email and cannot see orders after 29 August 2018. A later review needs a new extract scored with the same formula. If the median moves, 170 is not changed silently. The decision to keep or revise it is recorded.

---

## QA, performance, and limitations

### Q37. What did the end-to-end QA actually do?

It reloaded the nine raw tables and the processed extracts in full. A check passed when the recomputation matched the stored result. None of the 46 checks failed. Thirty-three passed. Eleven are warnings: source defects or definition boundaries that are already part of the method. Two were not run in that audit because the workbook was not in the repository and Tableau was not opened. Those two are presentation checks. They are not unanswered join or formula checks. The CLV recomputation on 93,358 rows had a maximum absolute difference of 0. Delivered product revenue matched at every layer that uses the delivered-product definition. The workbook and screenshots were inventoried afterwards. I leave the R1 scoreboard as 33, 0, 11, and 2, and I can show the later screenshots as evidence that the dashboards display the same locked figures.

### Q38. Which warnings would you rather disclose yourself than have an examiner find?

I would volunteer five. First, geolocation duplicates: dropping 261,831 exact duplicate rows would change 14,174 of 19,010 prefix coordinates and move 98,200 distances by more than 0.01 km, 57 by more than 10 km, and one by as much as 799.13 km. The stored file matches the median that keeps the duplicates. CLV does not use the coordinate. Second, the 2018 Q3 snapshot High Value count is 12,905 because quintiles were refit inside the quarter. The reporting count is 13,144. Third, the forecast holdout is off by about 2,131 customers per segment. It is exploratory. Fourth, frequency score 1 is 99.76%, while the one-order share is 97.0%. Fifth, the Total Orders tile is 96,683 and the funnel starts at 99,441. The remaining warnings are smaller: repeated `review_id`, 610 null categories plus 13 untranslated names, 278 unmatched customer ZIPs and 7 unmatched sellers, a small set of out-of-sequence timestamps, nine zero payment amounts, and seven non-delivered shipments that have a delay value stored.

### Q39. What performance changes were made, and how do you know the results did not move?

Two changes. The ZIP-prefix lookup no longer copies the unused city string, and the modal state uses the same tie break as `Series.mode()` without a Python callback inside the group-by. The median coordinates are unchanged. Across five runs the lookup went from 0.429 seconds and a 137.0 MB working frame to 0.050 seconds and 79.2 MB. Running the old mode on the narrower frame still took 0.427 seconds, so the time change is the mode and the memory change is the dropped city column. On all 19,010 prefixes, latitude, longitude, and modal state differed by 0. Rebuilt Haversine distances against the stored shipment file: 112,650 keys, 112,095 distances on both sides, maximum absolute difference 4.55e-13, and the same 555 missing. The distance file was not rewritten. The notebook cell was not re-executed inside Jupyter.

The Week 6 script reads only the columns it checks or writes. One run went from 2.336 seconds and peak RSS 445.8 MB to 2.151 seconds and 371.2 MB. All nine files in `data/tableau/`, including the pulse and the validation log, were byte-identical to the copies taken before the edit. The script passed 28 of 28 checks. Week 2–5 hashes were unchanged. After the edits, the locked counts were read again: 99,441 orders, 96,478 delivered, R$ 13,221,498.11, 93,358 customers, CLV difference 0, segments 13,144 / 52,727 / 15,220 / 12,267, pulse 2,051 at a threshold of 170.

Other ideas were timed and left alone. The Week 2 aggregations and joins are hundredths of a second. The nine quarterly snapshot cores are 0.494 seconds. A vectorised Week 1 delay label would save a few hundredths of a second inside an audit notebook. Parquet, a database, rounding the Tableau money columns, and deduplicating the Plotly library inside the HTML charts would each create a second copy or change a finished file. CSV reads of the large files are already under 0.3 seconds.

### Q40. What are the hard limits you will not talk past?

The score is an index of observed RFM and reviews. It ranges from 10 to 100 on this file and is not a forecast of future spend. The pulse is a recency watch on one snapshot and is not a churn model. The quarterly line is exploratory: six complete quarters, holdout MAE 2,131.225 customers per segment, MAPE 12.465%, naive MAE 4,741.5, and forward 2018 Q3 counts of 11,420.20, 52,934.73, 16,237.00, and 12,122.73. Segment lines are fit independently, so their sum need not match a separate forecast of the total. Geolocation duplicates move distances under a reasonable alternative rule. The Tableau Total Orders tile and the funnel are different sets. The workbook embeds extracts and still stores an absolute local path for refresh. No recommendation has a measured effect. `data/raw/`, `data/processed/`, and `data/output/` are gitignored, so a clone does not reproduce the results until those directories are restored.

---

## Difficult examiner questions

### Q41. If 97% of customers bought once, is this CLV at all?

It is CLV only in the narrow sense the project defined: a 0–100 value-and-experience index. It is a weak stand-in for a lifetime, because a lifetime of one order has little length to model. I agree with that criticism and I built the score anyway, with the limitation in the methodology rather than in a footnote. Frequency adds little separation. The index moves mainly with recency, monetary value, and the review. That is still useful. It shows that the revenue is concentrated, that the low band is a review problem sitting on R$ 1,773,336.84, and that a loyalty programme would be starting from a first purchase. A BG/NBD or monetary regression would be a different project. It would need a purchase-rate assumption this extract can barely identify, a margin the file does not contain, and a horizon. I did not invent those. The quarterly customer-count forecast is the only forward-looking piece, and it is labelled exploratory. It forecasts segment headcount, not reais.

### Q42. Is High Value just “people who left a 5-star review”?

The review is half the score, so a 5-star review is a powerful way into the band, and I should say that plainly. The manual sample includes High Value customers at exactly 80 whose RFM index is 60 and whose review index is 100. One of them, `0421e7a23f21e5d54efed456aedbc513`, has monetary value R$ 109.90, scores 5, 1, and 3, frequency 1, and recency 0. A monetary score of 3 is not the top spend quintile. High Value is therefore a joint band. It is not a pure spend ranking.

The band-level profile still has a spend difference. Average monetary value is R$ 252.43 and the median is R$ 170.30, both the highest of the four segments. Review coverage is 100% and the average is 4.998. Median recency is 85 days. When the question is “who spent more on average,” High Value did. When the question is “can a modest basket and a perfect review cross 80,” yes. I would use the monetary column, not the label alone, before offering a high-cost reward. A customer with a review of 1 and a monetary score of 5 lands at 30 and in Low Value, which is the mirror image: spend does not rescue a review of 1 under equal weights.

### Q43. The pulse looks like a tautology. You defined silence and then reported that some customers are silent. What did you learn?

The arithmetic is an identity once 170 is chosen: the flag matches `recency_days > 170` with zero disagreements, and the QA says so. The learning is not a discovered churn rate. The learning is whether that tail is large enough, under a rule fixed from the published median, to justify a review this week. On this file it is 15.60%, which the project’s own cuts call Alert and not Escalation. I also learned what the tail is not. It is not a low-review list. Every High Value customer has a review, and the segment average is 4.998. It is not evidence that these customers have left. 94.61% of High Value customers have one delivered order, so a long gap is being measured inside a base that rarely buys twice. A customer on the list may have had no reason to buy again. I cannot estimate a false-positive rate against actual churn, because the file has no churn label. If the examiner wants a model, the honest answer is that this screen is a monitoring rule for a classroom simulation, and the implementation note says the caption should say there is no verified churn label.

---

## Leadership recommendations and design trade-offs

### Q44. What would you recommend on Monday, and what evidence would you require before spending money?

I would brief four tests, in this order, and I would not brief them as findings about what already worked.

Protect the High Value relationship with a second-order test on a sample: early access or a reward, judged on a later delivered order. Do not buy a programme for a base whose median frequency is 1. Prioritise Medium-High for the repeat-purchase test, because a small change in a band that already holds R$ 6,532,268.84 matters more than the same change in a smaller band. Its current repeat share is 2.73%. On Low Value, start with service recovery. The average review is 1.352 and the average spend is R$ 144.56. A discount aimed at “low spenders” ignores the spend figure. The outcome to read first is the review on a later delivered order. Use São Paulo, 41.98% of orders, as the first regional test, with Rio de Janeiro and Minas Gerais as the comparison, and keep the CLV definition unchanged when the state filter is applied.

On the pulse, Alert means review the 2,051 names and design a holdout. It does not mean email all of them. No incremental revenue is in the extract. I would require, before scaling any of this, a pre-registered comparison of contacted customers and holdout customers on later delivered orders and later review scores. A rise in orders is a test result only when the holdout was defined in advance.

### Q45. Which design choices would you defend, and which would you change if the project were redone?

I would defend the grain, the revenue definition, the missing-review rule, and the refusal to call the score a currency forecast. Aggregating before the join is what keeps 99,441 orders. Excluding freight keeps the KPI equal to delivered product value at every layer. Leaving a missing review as missing, rather than as zero, avoids pushing 603 customers down a band for a survey they did not answer. Publishing 13,144 rather than the quarter-specific 12,905 keeps one segment definition in front of leadership.

I would change four things in a follow-on project, and I would label them as changes. I would report a simple monetary ranking beside the joint score, because Q42 shows the label can be entered without top-quintile spend. I would stop using a five-level frequency score when two levels would say the same thing, and I would keep publishing the 97.0% one-order rate as the business statistic. I would add an explicit geolocation sensitivity next to any distance chart, because the duplicate-row rule moves thousands of distances. I would not fit a fancier forecast on six quarters. If the question became future revenue, I would start a separate monetary model with a stated horizon, a margin assumption, and a purchase rate, and I would keep this index as the descriptive baseline rather than quietly renaming it.

The equal weights are the choice I would flag as a choice. A business that cares more about margin than about reviews would publish the 0.70 / 0.30 run and rebuild the bands. I did not do that here, because the question I accepted was the joint index, and the Low Value finding depends on the review having equal weight. Changing the weight would change that finding. That is a reason to disclose the weight, not a reason to pretend it was estimated.

---

## Short answers if time is cut off

| Question | Answer in one breath |
| --- | --- |
| Revenue? | R$ 13,221,498.11 delivered product value. Freight excluded. |
| Customers? | 93,358 scored, from 96,478 delivered orders. |
| Formula? | Half RFM index, half review index. Missing review keeps the RFM index. |
| Segments? | 13,144, 52,727, 15,220, 12,267 at 80, 60, and 40. |
| Biggest revenue band? | Medium-High, 49.41%. High Value is 25.10% from 14.08% of customers. |
| Low Value review? | 1.352. Average spend R$ 144.56, above the two middle bands. |
| Repeat rate? | 90,557 customers, 97.0%, have one delivered order. |
| Pulse? | 2,051 of 13,144, recency greater than 170 days, 15.60%, Alert. A recency watch, not verified churn. |
| QA? | 33 passed, 0 failed, 11 warnings, 2 not verified. CLV difference 0. |
| Tile versus funnel? | Total Orders shows 96,683. The funnel starts at 99,441. Different sets. |
| Forecast? | Exploratory. Holdout MAE 2,131.225 customers per segment. |
| Workbook? | Embedded extracts open without the folder. Refresh still has an absolute local path. |
