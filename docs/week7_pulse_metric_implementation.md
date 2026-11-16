# Week 7 — High-Value Segment Churn-Risk Pulse in Tableau Public

**Project:** Customer Lifetime Value & Segmentation Engine
**Requirement:** R2, a simulated pulse metric and alert UI
**Extract:** `data/tableau/week7_high_value_risk_pulse.csv`
**Dashboard tool:** Tableau Public. This guide does not use Streamlit and it does not automate Tableau Desktop.

The pulse is a historical snapshot. It flags High Value customers whose last delivered purchase is older than a stated recency threshold. The screen can be titled **High-Value Segment Churn Risk Pulse**. The status text on the screen is **Recency watch** or **Within band**. Those words are the metric. The extract does not contain a verified churn label, and the view should say so in a caption.

## What the extract contains

One row per `customer_unique_id`. Every row is High Value. The file is sorted by `customer_unique_id`.

| Column | Tableau type | Meaning |
| --- | --- | --- |
| `customer_unique_id` | String dimension | Customer key. Do not aggregate it with `COUNT`. Use `COUNTD` |
| `clv_score` | Number | Week 4 CLV score, 0–100 |
| `customer_segment` | String | `High Value` on every row |
| `recency_days` | Whole number | Days from the latest delivered purchase to 2018-08-29 |
| `frequency` | Whole number | Delivered orders |
| `monetary` | Number | Delivered product value, Brazilian reais |
| `average_review_score` | Number | Review score from 1 to 5. No blanks in this file |
| `risk_recency_threshold_days` | Whole number | 170 on every row. The assumption used to fill `risk_flag` |
| `risk_flag` | Whole number | 1 when `recency_days > 170`, else 0. Audit column |
| `risk_status` | String | `Recency watch` or `Within band`, at the 170-day rule |
| `days_beyond_threshold` | Whole number | `recency_days - 170` when the flag is 1, else 0 |
| `reference_date` | Datetime | `2018-08-29 15:00:37` on every row |

On this file: 13,144 customers, 2,051 with `risk_flag = 1` (15.60%), 11,093 within the band. Forty-seven customers have recency of exactly 170 days and stay in **Within band**, because the rule is strict inequality.

`risk_flag` and `risk_status` are the audited result at 170 days. The dashboard controls are Tableau parameters. Calculated fields apply those parameters to `recency_days`. Changing a parameter recalculates the view on this fixed extract. It does not load new orders.

## Why the default threshold is 170 days

High Value recency on the customer extract:

| Statistic | Days |
| --- | ---: |
| Minimum | 0 |
| Median | 85 |
| Mean | 98.29 |
| 75th percentile | 144 |
| 90th percentile | 201 |
| 95th percentile | 231 |
| 99th percentile | 263 |
| Maximum | 370 |

The published Week 5 median for this segment is 85 days. The pulse uses twice that median:

```
risk_recency_threshold_days = 2 * 85 = 170
```

A High Value customer is placed on the watch list when the last delivered purchase is more than 170 days before 29 August 2018. That is an operating assumption for the simulation. It is not an estimated churn boundary. The full rationale, severity bands, and escalation steps are in `docs/week7_alert_rule_and_campaign_escalation.md`.

The 90th percentile is 201 days. Using that percentile as the rule would put about one tenth of this same snapshot on the list by construction. A fixed multiple of the published median can be applied again to a later extract, and the share on the list can move. That is the quantity the alert watches.

## Build the data source

1. Open Tableau Public and choose **Connect > Text file**.
2. Select `data/tableau/week7_high_value_risk_pulse.csv`.
3. Name the data source **High Value Risk Pulse**. Leave it as its own source. Do not join it to Orders or to Customer CLV. A join on `customer_unique_id` would be valid but is unnecessary, because this file is already one row per High Value customer.
4. Confirm the row count is 13,144 and that `customer_unique_id` has 13,144 distinct values.
5. Set `customer_unique_id` and `customer_segment` to String dimensions if Tableau treats them as measures.
6. Set `reference_date` to a date-time. Every row should show 29 August 2018, 15:00:37.
7. Leave `risk_flag` as a number. The sheets below add a separate calculated flag so the threshold stays editable.

## Parameters

Create three parameters. The ranges are editing limits for the classroom file, not statistical confidence bounds.

| Parameter | Data type | Current value | Allowed range | Display |
| --- | --- | --- | --- | --- |
| `Risk recency threshold (days)` | Integer | 170 | 0 to 400 | Integer |
| `Alert share threshold` | Float | 0.10 | 0 to 1 | Percentage |
| `Escalation share threshold` | Float | 0.20 | 0 to 1 | Percentage |

Show each parameter on the dashboard. At the current values the snapshot is in **Alert**: 2,051 / 13,144 = 15.60%, which is above 10% and at or below 20%.

## Calculated fields

Create these on **High Value Risk Pulse**. Names below the formula are the field names to type into Tableau.

**Risk flag (parameter)**

```
IF [recency_days] > [Risk recency threshold (days)] THEN 1 ELSE 0 END
```

**Risk status (parameter)**

```
IF [recency_days] > [Risk recency threshold (days)]
THEN "Recency watch"
ELSE "Within band"
END
```

**High Value customers**

```
COUNTD([customer_unique_id])
```

**Flagged customers**

```
SUM([Risk flag (parameter)])
```

**Risk percentage**

```
SUM([Risk flag (parameter)]) / COUNTD([customer_unique_id])
```

Format this field as a percentage with two decimal places.

**Alert status**

```
IF SUM([Risk flag (parameter)]) / COUNTD([customer_unique_id])
     > [Escalation share threshold]
THEN "Escalation"
ELSEIF SUM([Risk flag (parameter)]) / COUNTD([customer_unique_id])
     > [Alert share threshold]
THEN "Alert"
ELSE "No alert"
END
```

**Flag matches extract**

```
SUM([Risk flag (parameter)]) = SUM([risk_flag])
```

With `Risk recency threshold (days)` left at 170, this field is True and both sides equal 2,051. After the parameter moves, the stored `risk_flag` stays at the 170-day audit result, so this check becomes False. That is expected. The view then follows **Risk flag (parameter)**.

## Sheet 1 — Pulse KPIs

Build one sheet named **Pulse KPIs**. Do not put a filter on it. The denominator has to remain all 13,144 High Value customers.

1. Place `Measure Names` on Columns and `Measure Values` on Text. Keep only **High Value customers**, **Flagged customers**, and **Risk percentage**. You can instead place the three fields side by side in three text tiles.
2. Expected values at the default parameter: **13,144**, **2,051**, **15.60%**.
3. Add `reference_date` as `MAX([reference_date])` in the title or the tooltip: `Snapshot 29 August 2018`.
4. Title the sheet **High Value recency pulse**.

## Sheet 2 — Alert indicator

Build a sheet named **Alert indicator**. No row filter.

1. Put **Alert status** on Text and on Color.
2. Set the colours: No alert as a neutral grey, Alert as amber, Escalation as a dark red.
3. At the default parameters the text reads **Alert**.
4. Add a caption under the mark:

```
Recency watch when recency_days is greater than the threshold parameter.
This snapshot has no verified churn label.
```

5. Set `Alert share threshold` to 0.16. The flagged share on this file is 2,051 / 13,144 = 0.1560, which is not greater than 0.16, so the indicator changes to **No alert**. Set `Escalation share threshold` to 0.15 while the alert threshold is back at 0.10. The share is greater than 0.15, so the indicator changes to **Escalation**. Set both parameters back to 0.10 and 0.20. The indicator returns to **Alert**.

## Sheet 3 — Flagged customers

Build a sheet named **Flagged customers**.

1. Rows: `customer_unique_id`.
2. Columns, or additional measures on the row as text: `clv_score`, `recency_days`, `days_beyond_threshold`, `monetary`, `average_review_score`, `frequency`.
3. Because each customer is one row, `AVG` and `SUM` of `clv_score` and `monetary` are the same on this sheet. Use `AVG` so a later relationship cannot silently add the score twice. Format `monetary` as currency with the Brazilian real symbol if the workbook locale allows it, otherwise as a number with two decimals and the axis title **Delivered product value (R$)**.
4. Filter the sheet with **Risk status (parameter)** set to `Recency watch`. Use the calculated field, not the stored `risk_status`. The stored value does not move when the parameter moves.
5. Sort `recency_days` descending so the longest silences are at the top.
6. At the default threshold the sheet lists 2,051 customers. The first single-order example in the QA sample, `0064a1b5f5cddd047c987b988a90c8c1`, has recency 180 and appears on this list. `0000366f3b9a7992bf8c76cfdf3221e2` has recency 111 and does not.

Optional check sheet **Flag reconciliation**: put **Flag matches extract** on Text. It reads True only while the recency parameter is 170.

## Dashboard

1. New dashboard named **High-Value Segment Churn Risk Pulse**.
2. Size: a fixed laptop width is enough for marking. Place **Alert indicator** across the top, **Pulse KPIs** under it, and **Flagged customers** across the bottom.
3. Show the three parameters on the right.
4. Add a text box:

```
Simulated pulse on the 29 August 2018 snapshot.
High Value customers with recency_days above the threshold are on recency watch.
The indicator turns to Alert above 10% of the segment and to Escalation above 20%.
Recency watch is not a churn label. No campaign result is measured here.
```

5. Do not add an action filter from the alert sheet onto the KPI sheet. A filter on the KPIs would shrink the denominator and change the percentage.
6. The customer table may be filtered. The KPI sheet and the alert sheet stay unfiltered.

## How to read a change

| Action | What should happen |
| --- | --- |
| Leave all parameters at the defaults | 13,144 customers, 2,051 flagged, 15.60%, status **Alert**, reconciliation True |
| Set the recency parameter to 201 | The flagged count falls to the customers with recency above 201 days. Reconciliation becomes False because `risk_flag` is still the 170-day column |
| Set the recency parameter back to 170 | Reconciliation returns to True |
| Raise `Alert share threshold` above the displayed risk percentage | Status becomes **No alert** |
| Lower `Escalation share threshold` below the displayed risk percentage | Status becomes **Escalation** |

Publish to Tableau Public from the Server menu when the four checks in the table behave as written. The published view is still this snapshot. Publishing it does not connect the workbook to a live order stream.
