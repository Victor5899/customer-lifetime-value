# Week 6 Tableau Public Implementation Guide

**Workbook name:** Olist Customer Lifetime Value
**Data folder:** `data/tableau/`
**Field definitions:** `docs/week6_tableau_data_dictionary.md`
**Totals to hit before publishing:** `docs/week6_tableau_validation.md`

Build the workbook in Tableau Public. The CSVs are already one grain each. Connect them, create the calculations below, and build the named worksheets. Do not reshape the files in Python into a single table, and do not rebuild this dashboard in Streamlit, Dash, or another Python framework.

Unfiltered targets, after every filter is cleared:

| Check | Value |
| --- | ---: |
| Customers | 93,358 |
| Average CLV | 62.58 |
| Repeat customers | 2,801 (3.00%) |
| Delivered product revenue | R$ 13,221,498.11 |
| Delivered orders | 96,478 |
| Funnel | 99,441 → 99,440 → 96,477 → 95,831 |
| State-month order total | 99,441 |

## 1. Connect each CSV

Open Tableau Public. For each file: **Connect > To a File > Text file**, then choose the CSV.

Turn the Data Interpreter off. These files already have one header row. Leave the field names as they are in the header. The calculations in this guide use those names. If a field is renamed, use the new name inside the brackets.

Connect these four data sources:

| Data source name | File | What to do on the canvas |
| --- | --- | --- |
| Customer Orders | `tableau_orders.csv` | This is the first table. Add the other two tables with relationships |
| State Month | `tableau_state_month.csv` | New data source. One table only |
| Funnel Stages | `tableau_funnel.csv` | New data source. One table only |
| Segment Profile | `tableau_segment_profile.csv` | New data source. One table only |

**Customer Orders** is the only source with more than one table. After Orders is on the canvas:

1. Drag `tableau_customer_clv.csv` onto the relationship area (the orange noodle). Do not drop it on the join area, and do not click Open to edit a join.
2. Relate on `customer_unique_id`.
3. Set Customer CLV to **One** and Orders to **Many**.
4. Set referential integrity to **Some records match**. 2,758 orders have no CLV customer.
5. Drag `tableau_shipments.csv` and relate it to **Orders** on `order_id`.
6. Set Orders to **One** and Shipments to **Many**. **Some records match.** 775 orders have no shipment.
7. Do not draw a second line from Shipments to Customer CLV. The only path is Shipments → Orders → Customer CLV.

Rename the tables in the relationship canvas to **Orders**, **Customer CLV**, and **Shipments**.

State Month, Funnel Stages, and Segment Profile stay alone. Do not add them to Customer Orders. A relationship from State Month to Orders on `customer_state` is many months to many orders.

### Relationships, physical joins, and blends

| Method | What Tableau does | Use it here |
| --- | --- | --- |
| Relationship | Aggregates each table, then combines the aggregates. Row counts stay at the native grain | Customer CLV, Orders, and Shipments |
| Physical join | Stitches rows before aggregating. An order with two items becomes two copies of that order's revenue | Do not use |
| Blend | Legacy primary/secondary link. The secondary table is aggregated, then attached on shared fields. A link that is not unique in the secondary source shows an asterisk | Do not use. Give each summary file its own worksheet |

A physical join of one R$ 100 order to two shipment rows stores R$ 200 if the revenue is summed afterwards. The relationship never builds that doubled row.

## 2. Set types, roles, and formats

On **Customer Orders > Orders**:

| Field | Type |
| --- | --- |
| `order_id`, `customer_unique_id`, `order_status`, `primary_payment_type`, `customer_state`, `customer_segment` | String |
| `order_purchase_timestamp` | Date & time |
| `total_product_value`, `total_freight_value`, `total_payment_value` | Number (decimal) |
| `has_payment_record`, `is_delivered`, `has_valid_review` | Number (whole) |
| `segment_sort` | Number. Blanks are the 2,758 unscored orders |

On **Customer CLV**: all measures are numbers. `customer_unique_id` and `customer_segment` are strings. `average_review_score` must stay nullable.

On **Shipments**: `distance_km` and `delivery_delay_days` are numbers. `order_id` is a string.

On **State Month**: set `purchase_month_date` to Date. Leave `purchase_month` as a string. Both order-count fields are whole numbers.

Geographic role, created once on each table that has `customer_state`:

1. Create `Customer Country` with the formula `"Brazil"`.
2. Right-click `Customer Country` > Geographic Role > Country/Region.
3. Right-click `customer_state` > Geographic Role > State/Province.

Default number formats:

| Fields | Format |
| --- | --- |
| Money measures and Delivered Product Revenue | `R$ #,##0.00` |
| Counts | `#,##0` |
| CLV score and review score | `#,##0.00` |
| Shares calculated with `TOTAL()` | Percentage, 2 decimals |
| `customer_percentage` and `revenue_share` on Segment Profile | `#,##0.00"%"` |

The profile percentages are already on a 0–100 scale. Tableau's percent format would multiply them by 100 again.

Sort `customer_segment` by the field `segment_sort`, aggregation Minimum, ascending. Do this on Orders and on Customer CLV. The order is High Value, Medium-High Value, Medium Value, Low Value.

Assign these colours to `customer_segment` on both tables. They are the Week 5 colours.

| Segment | Colour |
| --- | --- |
| High Value | `#1B4F72` |
| Medium-High Value | `#148F77` |
| Medium Value | `#8C6A12` |
| Low Value | `#922B21` |

## 3. Parameters and calculated fields

Create the parameters on the Customer Orders data source.

**Segment Selector** — string parameter:

- All segments
- High Value
- Medium-High Value
- Medium Value
- Low Value

Current value: All segments.

**Order Segment Filter**, built from the Orders table:

```tableau
[Segment Selector] = "All segments"
OR [customer_segment] = [Segment Selector]
```

**Customer Segment Filter**, built from the Customer CLV table. Open the Customer CLV field when you pick `customer_segment`, so the calculation does not point at the Orders copy:

```tableau
[Segment Selector] = "All segments"
OR [customer_segment] = [Segment Selector]
```

"All segments" keeps the 2,758 orders with a blank segment. Choosing one band hides them, which is the right behaviour for that band. A quick filter with the four names ticked and Null unticked also hides them when the intent was to show everything. Use the parameter for that reason.

### Orders calculations

**Delivered Product Revenue**

```tableau
IF [order_status] = "delivered" THEN [total_product_value] END
```

`SUM` of this field is the revenue KPI. Cleared filters: R$ 13,221,498.11.

**Delivered Order Count**

```tableau
COUNTD(IF [order_status] = "delivered" THEN [order_id] END)
```

Cleared filters: 96,478.

**Purchase Month**

```tableau
DATETRUNC('month', [order_purchase_timestamp])
```

**Revenue Share**

```tableau
SUM([Delivered Product Revenue]) / TOTAL(SUM([Delivered Product Revenue]))
```

This is a table calculation. On the treemap, edit it and compute using **customer_segment**. If every tile shows 100%, the calculation is running at the cell level. Compute using the segment dimension.

`TOTAL()` respects the filters on the worksheet, so the share is the share of the revenue still in view. A fixed level-of-detail total would ignore the segment parameter unless that filter is a context filter. Use `TOTAL()`.

**Orders Placed**

```tableau
COUNTD([order_id])
```

**Orders with Payment Records**

```tableau
COUNTD(IF [has_payment_record] = 1 THEN [order_id] END)
```

**Funnel Delivered Orders**

```tableau
COUNTD(
  IF [has_payment_record] = 1 AND [is_delivered] = 1
  THEN [order_id] END
)
```

**Funnel Reviewed Orders**

```tableau
COUNTD(
  IF [has_payment_record] = 1
     AND [is_delivered] = 1
     AND [has_valid_review] = 1
  THEN [order_id] END
)
```

Cleared filters: 99,441, 99,440, 96,477, and 95,831. `is_delivered` alone is 96,478 and is the wrong stage-3 definition. `has_valid_review` alone is not stage 4.

**Payment Drop Off**, **Delivery Drop Off**, and **Review Drop Off**

```tableau
[Orders Placed] - [Orders with Payment Records]
```

```tableau
[Orders with Payment Records] - [Funnel Delivered Orders]
```

```tableau
[Funnel Delivered Orders] - [Funnel Reviewed Orders]
```

### Customer CLV calculations

**Average CLV**

```tableau
AVG([clv_score])
```

Cleared filters: 62.58. This is an ordinary aggregate. It does not need a table calculation.

**Customer Percentage**

```tableau
COUNTD([customer_unique_id]) / TOTAL(COUNTD([customer_unique_id]))
```

Compute using **customer_segment**. Format as a percent.

**Repeat Customer**

```tableau
IF [frequency] >= 2 THEN 1 ELSE 0 END
```

**Repeat Customer Share**

```tableau
SUM([Repeat Customer]) / COUNTD([customer_unique_id])
```

Cleared filters: 3.00% (2,801 customers).

### Shipments calculations

**Average Distance (km)**

```tableau
AVG([distance_km])
```

Null distances stay out of the mean. Do not sum distance.

**Average Delivery Delay (days)**

```tableau
AVG(IF [is_delivered_order] = 1 THEN [delivery_delay_days] END)
```

Negative means the delivery was before the estimate. The delivered test drops the 7 non-delivered shipments that happen to have a delay.

**Shipment Rows**

```tableau
COUNT([order_item_id])
```

**Orders with a Shipment**

```tableau
COUNTD([order_id])
```

### Where each calculation is allowed

| Calculation | Worksheet dimensions | Do not place it on |
| --- | --- | --- |
| Delivered Product Revenue, order counts, funnel counts | Fields from Orders | A marks card that also sums `monetary` or `distance_km` |
| `AVG(clv_score)`, `AVG(monetary)`, `AVG(recency_days)`, `AVG(average_review_score)`, customer `COUNTD` | Fields from Customer CLV | A view whose detail is `order_id` |
| Average distance and average delay | Fields from Shipments | The revenue treemap |

`COUNTD(customer_unique_id)` on Orders answers "customers who have an order in this view." On delivered orders, with filters cleared, that distinct count equals 93,358 because every scored customer has a delivered order. It is still an order-table count. Lifetime CLV, recency, frequency, and the review average stay on Customer CLV.

The purchase-date filter belongs on order worksheets only. Customer CLV is a lifetime score. Filtering those sheets by purchase date would keep the lifetime score and only change which customers remain. The KPI captions say so.

## 4. KPI cards

Each card is a worksheet. Marks: Text. Put the measure on Text. Fit: Entire view. Hide the axis, grid lines, and row dividers. Centre the text. Title the sheet with the name below.

Put `Order Segment Filter` = True on the filter shelf of the revenue card. Put `Customer Segment Filter` = True on the other three. Do not put `order_purchase_timestamp` on the customer cards.

| Worksheet | Table | Text mark | Cleared result | Caption |
| --- | --- | --- | --- | --- |
| KPI — Customers | Customer CLV | `COUNTD(customer_unique_id)` | 93,358 | Scored customers. Responds to the segment parameter |
| KPI — Delivered Revenue | Orders | `SUM(Delivered Product Revenue)` | R$ 13,221,498.11 | Delivered product value. Excludes freight. Responds to date, state, and segment |
| KPI — Average CLV | Customer CLV | `AVG(clv_score)` | 62.58 | Week 4 score, 0–100. Lifetime index, not a reais forecast |
| KPI — Repeat Customers | Customer CLV | `Repeat Customer Share` | 3.00% | Customers with two or more delivered orders |

## 5. Revenue treemap

**Worksheet:** Revenue Treemap
**Table:** Orders

| Shelf | Field |
| --- | --- |
| Marks | Treemap, square or automatic |
| Detail / Label dimension | `customer_segment` |
| Size | `SUM(Delivered Product Revenue)` |
| Colour | `customer_segment`, using the palette above |
| Label | `customer_segment`, `SUM(Delivered Product Revenue)`, Revenue Share |
| Filters | `Order Segment Filter` = True. Purchase date, if the dashboard date filter should narrow the tiles. State, if the state filter should narrow the tiles |

Sort the segment by `segment_sort`. Edit Revenue Share and compute using `customer_segment`.

Cleared filters, in segment order: R$ 3,317,992.65 (25.10%), R$ 6,532,268.84 (49.41%), R$ 1,597,899.78 (12.09%), R$ 1,773,336.84 (13.41%).

Tooltip, in this order:

- Customer segment
- Delivered product revenue
- Revenue share
- Delivered Order Count
- `COUNTD(customer_unique_id)` with the label "Customers with a delivered order"

Do not add `SUM(monetary)`, `AVG(clv_score)`, or `AVG(distance_km)` to this tooltip.

## 6. State-month heat map

Build the dashboard heat map from Orders so the segment parameter and the date filter apply. The State Month file is the rectangular benchmark, including cells that are explicitly zero.

**Worksheet:** State-Month Orders
**Table:** Orders

| Shelf | Field |
| --- | --- |
| Columns | `Purchase Month`, discrete month (the blue date part, not the green continuous axis) |
| Rows | `customer_state` |
| Colour | `COUNTD(order_id)` |
| Filters | `Order Segment Filter` = True |
| Marks | Square |

Colour: sequential gold to red, starting at 0. Show the mark label off. Sort states by `COUNTD(order_id)` descending.

Use **Analysis > Table Layout > Show Empty Rows** and **Show Empty Columns** so a state that has orders in other months still shows a gap. Those gaps are combinations absent from the filtered orders. The State Month file is the version that stores the zeros as rows.

**Worksheet:** State-Month Revenue
Same layout. Colour is `SUM(Delivered Product Revenue)`, sequential blue, starting at 0. September and October 2018 can show orders on the first sheet and no revenue on the second. That matches Week 5: those months have placed orders and no delivered orders.

Tooltip for the order heat map:

- Customer state
- Purchase month
- Distinct orders, `COUNTD(order_id)`
- Delivered orders, Delivered Order Count
- Delivered product revenue

Cleared filters: SP 41,746 orders, then RJ 12,852 and MG 11,635. The largest month is 2017-11 with 7,544 orders. The sum of the unfiltered order heat map is 99,441.

**Worksheet:** QA — State Month Totals
**Data source:** State Month

Put `SUM(distinct_order_count)`, `SUM(delivered_order_count)`, and `SUM(total_product_revenue)` on Text. Expected: 99,441, 96,478, and R$ 13,221,498.11. This sheet is not on the leadership dashboard and has no segment filter. `SUM` is correct because each cell is already a count or a revenue total.

## 7. Conversion funnel

**Worksheet:** Conversion Funnel
**Table:** Orders

Tableau Public draws this reliably as a sorted bar. A funnel extension is unnecessary.

| Shelf | Field |
| --- | --- |
| Rows | Measure Names |
| Columns | Measure Values |
| Filters | Measure Names kept to the four stage measures, in the order below. `Order Segment Filter` = True |
| Marks | Bar |
| Label | Measure Values |
| Colour | A single teal, `#148F77`, so colour is not confused with the segment palette |

Measure Names order, top to bottom:

1. Orders Placed
2. Orders with Payment Records
3. Funnel Delivered Orders
4. Funnel Reviewed Orders

Rename the measure aliases on this sheet to the Week 5 stage names: Orders Placed, Orders with Payment Records, Delivered Orders, Orders with Valid Reviews.

Sort the bars descending by the measure value, which follows that order when nothing is filtered. Hide the "Measure Names" axis title and use the sheet title **Order, payment, delivery, review**.

Tooltip:

- Stage name
- Distinct orders
- Delivery Drop Off or the matching drop-off calculation
- A sentence in the tooltip editor: "Stage 3 counts a delivered order only when it also has a payment record."

Cleared filters: 99,441, 99,440, 96,477, 95,831. Drop-offs: 1, then 2,963, then 646.

**Worksheet:** QA — Published Funnel
**Data source:** Funnel Stages

| Shelf | Field |
| --- | --- |
| Rows | `stage_name`, sorted by `stage_order` ascending |
| Columns | `order_count` |
| Label | `order_count`, `conversion_percentage`, `drop_off_count` |

Format `conversion_percentage` as `#,##0.00"%"` because it is already 0–100. This sheet is the Week 5 benchmark. Do not put the segment parameter on it. Leave it off the leadership dashboard, or place it on a small QA dashboard.

## 8. Segment profile

**Worksheet:** Segment Profile
**Table:** Customer CLV

| Shelf | Field |
| --- | --- |
| Rows | `customer_segment`, sorted by `segment_sort` |
| Columns | Measure Values |
| Filters | Measure Names limited to the measures below. `Customer Segment Filter` = True |
| Marks | Bar |
| Colour | `customer_segment` |

Measures, each on its own row:

| Alias on the sheet | Field |
| --- | --- |
| Customers | `COUNTD(customer_unique_id)` |
| Customer share | Customer Percentage, compute using `customer_segment` |
| Average CLV | `AVG(clv_score)` |
| Average monetary value | `AVG(monetary)` |
| Average frequency | `AVG(frequency)` |
| Average recency (days) | `AVG(recency_days)` |
| Average review score | `AVG(average_review_score)` |

`AVG(average_review_score)` skips the 603 nulls. That is the Week 5 definition. Do not wrap the field in `ZN`.

With the parameter on All segments, the four rows match the Segment Profile file: customer counts 13,144, 52,727, 15,220, and 12,267; average CLV 82.35, 69.27, 51.29, and 26.63; average monetary value R$ 252.43, R$ 123.89, R$ 104.99, and R$ 144.56.

Tooltip: segment, the measure name, the value, and `AVG(review_data_available)` labelled "Review coverage."

**Worksheet:** QA — Segment Baseline
**Data source:** Segment Profile

A text table of `customer_segment`, `customer_count`, `total_product_revenue`, `revenue_share`, and `average_review_score`. Use the stored numbers directly. `SUM(customer_count)` and `SUM(total_product_revenue)` are the right aggregations. `AVG(average_clv_score)` is safe only because there is one row per segment. This sheet is the benchmark, not the interactive profile.

## 9. Monthly trend

**Worksheet:** Monthly Revenue Trend
**Table:** Orders

| Shelf | Field |
| --- | --- |
| Columns | `Purchase Month` as a continuous month (green pill) |
| Rows | `SUM(Delivered Product Revenue)` |
| Colour | `customer_segment` |
| Detail | `customer_segment` |
| Filters | `Order Segment Filter` = True |
| Marks | Line |

The colour legend uses the same four colours. Missing segment stays out of the coloured lines because those 2,758 orders are not delivered, so they add nothing to this measure.

Add a second worksheet only if a volume line is wanted:

**Worksheet:** Monthly Order Trend
Same columns. Rows: `COUNTD(order_id)`. This one includes every status, so it will show the 16 orders in 2018-09 and the 4 orders in 2018-10 that have no delivered revenue.

Tooltip: month, segment, delivered product revenue, Revenue Share computed using `customer_segment`, and Delivered Order Count.

## 10. Delivery distance and delay

**Worksheet:** Delivery Distance
**Table:** Shipments, inside Customer Orders

| Shelf | Field |
| --- | --- |
| Rows | Shipments.`customer_state` |
| Columns | Average Distance (km) |
| Filters | `Order Segment Filter` = True, so the relationship keeps shipments whose order is in the selected segment |
| Marks | Bar |
| Label | Average Distance (km), Orders with a Shipment |

Sort states by average distance descending. Do not put Delivered Product Revenue on this sheet.

Tooltip:

- Customer state
- Average distance (km)
- Average delivery delay (days)
- Orders with a Shipment, labelled "Distinct orders"
- Shipment Rows, labelled "Shipment rows"

The delay in that tooltip uses the delivered-only average. Say in the tooltip: "Delay is delivered date minus estimated date, in days. A negative value is early. The average uses delivered shipments only."

This sheet does not respond to the purchase-date filter. The shipment file has no purchase timestamp, and adding the order date to this marks card is unnecessary for the distance question. The segment parameter does apply, through `Order Segment Filter`.

Cleared distance average uses every shipment with a non-null `distance_km` (555 distances are missing and stay missing). There is no single "correct" distance total to sum.

## 11. Filters and dashboard actions

**Dashboard:** Customer Intelligence
**Size:** Fixed, 1,400 × 1,200.

Tiled layout, top to bottom:

1. Title: **Customer intelligence** and a one-line subtitle: "Delivered product revenue and Week 4 CLV segments. Olist public orders."
2. Horizontal container: Segment Selector parameter, purchase-date filter, customer-state filter.
3. Horizontal container: the four KPI worksheets.
4. Horizontal container: Revenue Treemap (about 55% width) and Segment Profile.
5. Monthly Revenue Trend, full width.
6. Horizontal container: State-Month Orders (or State-Month Revenue, with a sheet selector) and Conversion Funnel.
7. A text box with the three campaign tests from the story, so the recommendation sits on the same page as the charts.

Show the Segment Selector from any sheet that uses it. One parameter controls every sheet.

**Purchase date.** On Monthly Revenue Trend, show the filter for `order_purchase_timestamp`, range. Apply it to the worksheets that use Orders fields: KPI — Delivered Revenue, Revenue Treemap, State-Month Orders, State-Month Revenue, Conversion Funnel, Monthly Revenue Trend, Monthly Order Trend. Do not apply it to KPI — Customers, KPI — Average CLV, KPI — Repeat Customers, or Segment Profile.

**Customer state.** Show `customer_state` from Orders. Apply it to the same order worksheets. All is the default. Do not apply it to the customer-lifetime KPIs.

**Dashboard:** Delivery Geography
**Size:** Fixed, 1,200 × 800.

Delivery Distance, full width, with the Segment Selector. Title the dashboard **Shipment distance and delay**. Caption: "One row per order item. Distance is an average. Delay uses delivered shipments only and can be negative."

### Filter action

Dashboard > Actions > Add Action > Filter.

| Setting | Value |
| --- | --- |
| Name | Segment filters the order views |
| Source sheet | Revenue Treemap |
| Run on | Select |
| Target sheets | KPI — Delivered Revenue, State-Month Orders, State-Month Revenue, Conversion Funnel, Monthly Revenue Trend |
| Clearing the selection | Show all values |

Exclude Revenue Treemap from its own targets, so one click does not collapse the treemap to a single tile. The customer KPIs stay on the parameter. A click then narrows revenue, the map, the funnel, and the trend, and a second click restores them.

Add a second filter action if the distance dashboard should follow a state click:

| Setting | Value |
| --- | --- |
| Name | State filters delivery distance |
| Source | State-Month Orders, on the Customer Intelligence dashboard |
| Target | Delivery Distance |
| Field mapping | Orders.`customer_state` → Shipments.`customer_state` |
| Clearing the selection | Show all values |

### Highlight action

Dashboard > Actions > Add Action > Highlight.

| Setting | Value |
| --- | --- |
| Name | Highlight segment |
| Source | Revenue Treemap |
| Run on | Hover |
| Target sheets | Segment Profile, Monthly Revenue Trend |
| Target highlighting | Selected fields: `customer_segment` |

Hovering a tile highlights that segment on the profile and the trend. The other segments stay visible. Highlight does not change any total. The filter action is the one that changes totals.

## 12. Tooltip design

Keep tooltips to the grain of the sheet. Format money as R$ and shares as percents. Suggested wording:

**Treemap**

```
<customer_segment>
Delivered product revenue: <SUM(Delivered Product Revenue)>
Share of delivered revenue: <AGG(Revenue Share)>
Delivered orders: <AGG(Delivered Order Count)>
Customers: <COUNTD(customer_unique_id)>
```

**Heat map**

```
<customer_state>  ·  <MONTH(Purchase Month)>
Orders placed: <COUNTD(order_id)>
Delivered orders: <AGG(Delivered Order Count)>
Delivered product revenue: <SUM(Delivered Product Revenue)>
```

**Funnel**

```
<Measure Names>
Distinct orders: <Measure Values>
Drop from the previous stage uses the nested rule:
payment, then delivered, then a review score from 1 to 5.
```

**Segment profile**

```
<customer_segment>
<Measure Names>: <Measure Values>
Review coverage: <AVG(review_data_available)>
```

**Distance**

```
<customer_state>
Average distance: <AVG(Average Distance (km))> km
Average delay, delivered shipments: <AVG(Average Delivery Delay (days))> days
Distinct orders: <AGG(Orders with a Shipment)>
Shipment rows: <AGG(Shipment Rows)>
```

Turn off the default command buttons if they crowd the tooltip. Do not paste `customer_unique_id` into a dashboard tooltip. The id is on the extract for relationships and is not a leadership field.

## 13. Leadership story

**Story:** Leadership Briefing
**Size:** the same fixed size as the dashboard, or 1,400 × 900 if the caption needs less height.
**Navigator:** captions only.

Each story point uses a captured view of Customer Intelligence or Delivery Geography. Duplicate the dashboard as a story point, then set the parameter and filters for that point. Write the caption in the story navigator. The numbers below are the cleared-filter results from the extracts and they match Week 5.

### Point 1 — Two segments hold most of the revenue

Show the treemap and the revenue KPI.

Medium-High Value is 52,727 customers, 56.48% of the scored base, and R$ 6,532,268.84 of delivered product revenue, 49.41%. High Value is 13,144 customers, 14.08%, and R$ 3,317,992.65, 25.10%. Together those bands are R$ 9,850,261.49, 74.50% of delivered product revenue. The treemap is sized by revenue, so Medium-High is the largest area and High Value is the second.

### Point 2 — High Value is recent and higher spend

Show Segment Profile, with the parameter still on All segments, and point at High Value.

Average monetary value is R$ 252.43, the highest of the four bands. Average recency is 98.3 days, against 253.8, 278.5, and 261.3 days. The median recency published in Week 5 is 85 days. Average frequency is 1.067. Median frequency is 1 in every band. 5.39% of High Value customers have two or more delivered orders, the highest repeat share, and still a small one. The band describes recent, higher-spend, higher-rated customers. It does not describe customers who already buy repeatedly.

### Point 3 — Low Value is a review band

Show Segment Profile again.

Low Value average review score is 1.352, against 4.998 in High Value. Average monetary value is R$ 144.56, above Medium-High (R$ 123.89) and Medium (R$ 104.99). The CLV order and the spend order are different. Minimum recency is 0 days in every band, so the band is not defined by a completed lapse. Call it Low Value. Do not call it churned or at risk.

### Point 4 — Volume sits in a few states and in November 2017

Show State-Month Orders.

SP has 41,746 orders, 41.98% of orders placed. RJ has 12,852 and MG has 11,635. November 2017 is the largest month, with 7,544 orders. The heat map is a geographic and calendar view of orders. It is not a map of the personas. September 2018 (16 orders) and October 2018 (4 orders) appear in the order counts and contribute no delivered revenue. November 2016 has no orders and is not in the grid.

### Point 5 — The funnel drops between payment and delivery

Show Conversion Funnel, filters cleared.

99,441 orders were placed. 99,440 have a payment record. 96,477 reach the delivered stage. 95,831 of those have a review score from 1 to 5. The drop of 2,963 orders is 2.98% of orders with a payment record. The later review drop is 646 orders, 0.67% of the delivered stage. One delivered order has no payment record, so the nested rule excludes it from the delivered stage. Its R$ 134.97 remains inside the revenue KPI, which is why delivered status (96,478) and funnel stage 3 (96,477) differ by one order.

### Point 6 — Three tests, with a metric for each

Show the full dashboard. These are tests. The dataset does not contain a campaign result, and nothing here estimates a causal effect.

| Segment | Test | What would show that it moved |
| --- | --- | --- |
| High Value | A second-purchase offer, early access, or a reward | The share of this segment with a later delivered order, and median recency |
| Medium-High Value | A repeat-purchase incentive on the largest revenue pool | The second-order share, and delivered product revenue in the segment |
| Low Value | A follow-up after a low review, and a separate first-to-second-order offer | The review score on a later delivered order, and the second-order share |

Medium Value has the lowest average monetary value, R$ 104.99. It stays in the profile and does not get a fourth campaign. A cross-sell claim for Medium-High would need a product-category analysis. This workbook does not contain one, so the recommendation stays a repeat-purchase test.

### Caption for the limits

Put this on the last story point, under the tests.

The CLV score is a historical index of observed RFM and reviews. It is not a forecast of future spend in reais. Most customers have one delivered order, so frequency separates the bands only slightly. 603 customers have no review score; they stay in the customer count and out of the review average. Customer KPIs are lifetime figures and do not follow the purchase-date filter. Order KPIs do.

## 14. Publish to Tableau Public

1. Confirm the QA sheets, with the parameter on All segments and the date and state filters cleared, show R$ 13,221,498.11, 93,358 customers, and the funnel 99,441 → 99,440 → 96,477 → 95,831.
2. Click a High Value tile. Revenue, the heat map, the funnel, and the trend narrow. The treemap still shows all four tiles. Hover highlights the profile. Clear the selection and the order sheets return to the totals above.
3. Set the date filter to September 2018. Delivered revenue for that month is R$ 0, while the order heat map can still show 16 placed orders. Clear the date filter afterwards.
4. **File > Save to Tableau Public As**. Sign in with the Tableau Public account. Workbook title: `Olist Customer Lifetime Value`.
5. Tableau Public publishes the workbook and the data inside it. Anyone with the link can open it. That is acceptable for this course: the extracts are derived from the public Olist dataset, and they contain no review text, customer name, email, tax id, or zip code. Do not add `data/raw/` to the workbook before saving.
6. Open the public URL. Repeat the tile click and the date filter. Story points and actions sometimes need the sheets to be in the published layout before the target list is stored, so check the live page rather than only the desktop preview.
7. Submit the public URL with the workbook file if the course asks for both.

## 15. Build checklist

| Step | Done when |
| --- | --- |
| Four data sources connected | Customer Orders has three related tables. The other sources have one table each |
| No physical joins and no blends | The relationship canvas shows noodles, not a join venn diagram |
| Types and the Brazil geographic role set | Purchase timestamp is a date & time. States map as Brazilian states |
| Parameter and both segment filters | All segments returns 99,441 orders and 93,358 customers |
| Revenue calculation | Cleared sum is R$ 13,221,498.11 |
| Funnel calculations | Cleared counts are 99,441, 99,440, 96,477, 95,831 |
| Treemap, profile, trend, heat map, funnel | Worksheet names match this guide |
| QA sheets | State Month, Funnel Stages, and Segment Profile match the validation note |
| Date filter scope | Customer KPI sheets do not move when the date changes |
| Highlight and filter actions | Hover highlights. Select filters the order sheets and restores them on clear |
| Story | Six captions, including the three tests and the limit |
| Public URL | Actions checked on the published page |
