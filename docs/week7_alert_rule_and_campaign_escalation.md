# Week 7 — Alert Rule and Campaign Escalation

**Project:** Customer Lifetime Value & Segmentation Engine
**Requirement:** R3
**Metric:** High-Value Segment Churn-Risk Pulse
**Snapshot:** 29 August 2018, 15:00:37
**Population:** 13,144 High Value customers in `data/tableau/week7_high_value_risk_pulse.csv`

The pulse is a classroom simulation on the historical Olist extract. It supports a weekly review of High Value customers whose last delivered purchase is old relative to that segment. It is not a production monitoring system, and it has not been checked against a verified churn outcome.

## 1. Purpose

High Value is the band with CLV score of 80 or above: 13,144 customers, 14.08% of the scored base, R$ 3,317,992.65 of delivered product revenue (25.10%). Week 5 records a median recency of 85 days and an average review score of 4.998 for this band. The median number of delivered orders is 1.

The pulse keeps a list of High Value customers who have been silent for longer than a stated multiple of that 85-day median. Marketing and support can review the list. The list does not say that a customer has churned, and it does not say that a campaign has already recovered revenue.

## 2. Risk threshold and rationale

Two controls are kept separate. One decides which customer is listed. The other decides whether that list is large enough to raise the indicator.

**Customer rule.** Flag the customer when:

```
recency_days > 170
```

`recency_days` is measured back to 2018-08-29 15:00:37. The threshold is `2 × 85`. The 85 is the High Value median recency published in Week 5 and confirmed on this extract (minimum 0, median 85, mean 98.29, 75th percentile 144, 90th percentile 201, 95th percentile 231, maximum 370).

On this snapshot the rule flags **2,051** customers, **15.60%** of High Value. **11,093** customers (84.40%) stay in the band. **47** customers have recency of exactly 170 days and are not flagged.

This multiple is a business assumption. It was chosen after looking at the distribution so that the list is the long-silence tail of High Value rather than half the segment. A cut at the median of 85 days would flag about half of High Value and would not work as a pulse. A cut at the 90th percentile of this same file would force the share to about 10% on this snapshot, so the share could not move independently of the cut. One hundred and seventy days can be reused on a later extract. The share can then rise or fall.

The assumption is recorded on every row as `risk_recency_threshold_days`. In Tableau the editable control is the parameter `Risk recency threshold (days)`, default 170. The stored `risk_flag` remains the audit result at 170.

**Alert rule.** Raise the indicator when the flagged share of High Value is greater than 10%. Escalate when that share is greater than 20%. Both cuts are operating assumptions for the simulation. They are not fitted to a churn rate. Ten percent of 13,144 customers is 1,314.4, so on this population the alert also means a flagged count of 1,315 or more. Twenty percent is a flagged count of 2,629 or more.

## 3. Conditions that trigger the alert

All of the following are true before the indicator is evaluated:

- The customer is in the Week 4 High Value band (CLV score ≥ 80).
- Recency uses the Week 3 reference date.
- The customer flag uses the current recency parameter, default 170 days, with a strict greater-than test.
- The share uses every High Value customer in the extract as the denominator.

The indicator then follows the share:

| Flagged share of High Value | Indicator | This snapshot |
| --- | --- | --- |
| At or below 10% | No alert | — |
| Above 10% and at or below 20% | Alert | 15.60% (2,051 customers) |
| Above 20% | Escalation | — |

At the default parameters this snapshot is **Alert**.

## 4. Severity

| Level | Rule | What the team does |
| --- | --- | --- |
| No alert | Flagged share ≤ 10% | Keep the watch list available. Do not start a campaign from the pulse alone. |
| Alert | Flagged share > 10% and ≤ 20% | Review the watch list in the same week. Prepare a re-engagement test. Do not launch it to the whole segment. |
| Escalation | Flagged share > 20% | The same review, plus a decision to run the test against a holdout, and a named owner for the follow-up. |

Severity describes the size of the watch list. It does not grade a customer's probability of leaving. Customer status stays binary: **Within band** or **Recency watch**.

## 5. Recommended actions

These are tests and review steps. None of them has a result in the Olist extract.

1. **Review the flagged list.** Sort by `recency_days` descending. Read `clv_score`, `monetary`, `frequency`, and `average_review_score` before any offer is written. On this file every High Value customer has a review, and the segment average is 4.998, so the watch list is a silence list rather than a low-score list.
2. **Prioritise support follow-up where a later operational source shows an open complaint or a delivery problem.** This extract does not contain complaint text. A low review is uncommon in High Value. Support effort follows evidence from service records, not the recency flag by itself.
3. **Test a personalised re-engagement message** on a sample of the watch list. The Week 5 High Value action was a second-purchase offer, early access, or a reward. The pulse only chooses who is silent. It does not choose the product.
4. **Monitor subsequent purchase activity** for the contacted customers and for a holdout that was flagged and not contacted. The outcome to record is a later delivered order, plus the review score on that order.
5. **Evaluate the test before extending it.** Compare the second-order rate in the contacted group with the holdout. Stop or redesign the message if the rates do not differ by a margin the team set before the test.

Do not apply a blanket discount to everyone with `risk_flag = 1`. The segment's median frequency is already one delivered order, so a long gap is being measured inside a base that rarely repeats.

## 6. Escalation workflow

1. Refresh the High Value extract with the unchanged CLV formula and the same reference-date definition. This project has one snapshot, dated 29 August 2018, so a refresh is a future step rather than a completed feed.
2. Recompute `recency_days > 170` and the flagged share. In the classroom workbook, confirm the parameter is still 170 before comparing the share with 10% and 20%.
3. If the indicator is **No alert**, file the count and the share. Leave the campaign unstarted.
4. If the indicator is **Alert**, the analyst opens the watch list, removes any duplicate `customer_unique_id` (the current file has none), and writes a one-page test brief: audience size, message, holdout, and the second-order rate that will be read afterwards.
5. If the indicator is **Escalation**, the same brief goes to the module lead or the marketing owner named in the brief. The owner approves a sample, not the entire High Value segment.
6. After the test window, report contacted customers, holdout customers, later delivered orders, and later review scores. A rise in orders is a test result only when the holdout was defined in advance.
7. Record the parameter values with the result. A comparison that used a different day threshold is a different test.

## 7. How the alert should be monitored

On each review, record:

- Reference date of the extract.
- Recency threshold in days, and confirmation that it is still `2 ×` the High Value median used when the rule was set. If a future extract's median moves, do not silently change 170. Record a decision to keep or revise the assumption.
- High Value customer count.
- Flagged count and flagged share.
- Indicator: No alert, Alert, or Escalation.
- Whether a test was started, and the holdout size if it was.

The Tableau workbook shows the first five items for this snapshot. It cannot schedule a weekly email, and it cannot see orders placed after 29 August 2018. Monitoring beyond that date needs a new scored extract built with the Week 4 formula.

## 8. Limitations and false positives

- The Olist files used here have no verified churn label. Matching the flag to the 170-day rule validates the rule. It does not validate a predictive model, and it does not estimate a false-positive rate against actual churn.
- A customer on the watch list may simply have had no reason to buy again inside the window. Week 5 shows that 94.61% of High Value customers have one delivered order. Silence after one order is the common pattern, including among customers who reviewed the order at 5.
- Recency is anchored at 29 August 2018. A flag is not "inactive as of today."
- Customers with recency of 170 days are inside the band. Moving the parameter by one day changes who is listed. The 47 customers on that exact day show the boundary.
- High Value requires a CLV score of at least 80. A long silence can still sit inside the band when the review score is high, which is why these customers were worth a watch list rather than a regrade of the segment.
- The alert share of 10% and the escalation share of 20% are management cuts for the simulation. Another team could set different cuts. The customer rule and the cuts should be written down with the result.
- No campaign has been sent to these customers as part of this project. The extract cannot show incremental revenue, a recovered customer, or a change in review score caused by an intervention.
