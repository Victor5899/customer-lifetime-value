# Data Dictionary — Olist Brazilian E-Commerce Public Dataset

**Project:** Interactive Customer Lifetime Value and Segmentation Analytics System for E-Commerce
**Source notebook:** `notebooks/01_week1_data_audit.ipynb` (Week 1 — Olist Data Understanding, ER Mapping and Audit)
**Status:** Reflects the actual, executed Week 1 audit results (referential-integrity audit, review-score audit, delivery-delay audit, and the customer-grain cardinality investigation). Row counts and statistics below are taken directly from the loaded raw data in `data/raw/`, which was never modified.

## Legend

| Label | Meaning |
|---|---|
| **Verified PK** | Confirmed unique per row via an explicit uniqueness check on the actual data |
| **Verified FK** | Foreign key confirmed via a referential-integrity check (0% or a small, documented % of unmatched child rows) |
| **Inferred key / join field** | Structurally plausible join field (matching name/semantics) whose parent side is **not** a unique key — treat joins on it as many-to-many |
| **Non-unique identifier** | A column that looks like an identifier but is verified **not** unique per row — must not be relied on as a standalone key |
| **Flagged (data-quality)** | A nominal identifier expected to be unique that was found to have duplicates — requires care in downstream joins |
| **Attribute** | Ordinary descriptive/measure column, not part of the key structure |

---

## 1. `customers` — 99,441 rows, 5 columns

**Business purpose:** One row per order-level customer record: who placed a given order and where they are located. See the [Customer Identifier](#customer-identifier-customer_id-vs-customer_unique_id) section below for the critical distinction between `customer_id` and `customer_unique_id`.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `customer_id` | string | Order-scoped surrogate identifier for the customer record tied to one order | **Verified PK** (99,441 / 99,441 unique) | Do **not** treat as a persistent customer identifier — see below |
| `customer_unique_id` | string | Persistent real-world customer/account identifier | **Non-unique identifier** (96,096 distinct values across 99,441 rows) — **NOT a primary key of this table** | The real customer grain; use this (not `customer_id`) for any customer-level analysis (RFM/CLV, planned for later weeks) |
| `customer_zip_code_prefix` | int64 | First digits of the customer's Brazilian ZIP code | **Inferred FK** → `geolocation.geolocation_zip_code_prefix` (many-to-many; 278 rows / 0.28% unmatched — WARNING) | Not a formal key join; multiple geolocation rows can share a prefix |
| `customer_city` | string | Customer's city name | Attribute | — |
| `customer_state` | string | Customer's state abbreviation (e.g. SP, RJ) | Attribute | — |

---

## 2. `geolocation` — 1,000,163 rows, 5 columns

**Business purpose:** Lookup table mapping Brazilian ZIP-code prefixes to approximate coordinates and city/state, used to geo-locate customers and sellers.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `geolocation_zip_code_prefix` | int64 | First digits of a Brazilian ZIP code | **Inferred key / join field only** — verified **not** unique (19,015 unique values across 1,000,163 rows) | Never treat as a primary key; multiple lat/lng rows exist per prefix |
| `geolocation_lat` | float64 | Approximate latitude | Attribute | — |
| `geolocation_lng` | float64 | Approximate longitude | Attribute | — |
| `geolocation_city` | string | City name for the coordinate | Attribute | — |
| `geolocation_state` | string | State abbreviation for the coordinate | Attribute | — |

**Note:** because this table has no unique key, joining `customers` or `sellers` to it is many-to-many. A representative coordinate per prefix (e.g. mean or first) should be chosen before any spatial analysis — this has not been done in Week 1.

---

## 3. `orders` — 99,441 rows, 8 columns

**Business purpose:** Order header table — one row per order — with status and the full order timeline, used for the delivery-delay and anomaly audits.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `order_id` | string | Unique order identifier | **Verified PK** (99,441 / 99,441 unique) | — |
| `customer_id` | string | Customer record tied to this order | **Verified FK** → `customers.customer_id` (1:1, 0% unmatched) | Genuinely 1:1 because `customer_id` is order-scoped — see [Customer Identifier](#customer-identifier-customer_id-vs-customer_unique_id) |
| `order_status` | string | Order lifecycle status (e.g. delivered, shipped, canceled) | Attribute | — |
| `order_purchase_timestamp` | string (parses to datetime) | Timestamp the order was placed | Attribute | Loaded as text; parsed to datetime only in an in-memory working copy for analysis, raw column untouched |
| `order_approved_at` | string (parses to datetime) | Timestamp the order was approved | Attribute | Some nulls present |
| `order_delivered_carrier_date` | string (parses to datetime) | Timestamp handed to the logistics carrier | Attribute | 166 rows (0.17%) found earlier than `order_purchase_timestamp` — flagged WARNING |
| `order_delivered_customer_date` | string (parses to datetime) | Timestamp delivered to the customer | Attribute | **2,965 orders (2.98%) missing** — delivery delay cannot be calculated for these; 23 rows (0.024%) found earlier than `order_delivered_carrier_date` — flagged WARNING |
| `order_estimated_delivery_date` | string (parses to datetime) | Estimated delivery date shown to the customer | Attribute | Used as the baseline for `delivery_delay_days` |

---

## 4. `order_items` — 112,650 rows, 7 columns

**Business purpose:** Line-item detail — one row per item purchased within an order.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `order_id` | string | Order this item belongs to | Part of **Verified composite PK** `(order_id, order_item_id)`; also **Verified FK** → `orders.order_id` (1:many, 0% unmatched) | — |
| `order_item_id` | int64 | Sequence number of the item within the order | Part of **Verified composite PK** | — |
| `product_id` | string | Product purchased | **Verified FK** → `products.product_id` (1:many, 0% unmatched) | — |
| `seller_id` | string | Seller fulfilling this item | **Verified FK** → `sellers.seller_id` (1:many, 0% unmatched) | — |
| `shipping_limit_date` | string (parses to datetime) | Seller's shipping deadline | Attribute | — |
| `price` | float64 | Item price | Attribute | — |
| `freight_value` | float64 | Shipping cost for this item | Attribute | — |

---

## 5. `payments` — 103,886 rows, 5 columns

**Business purpose:** Payment transaction detail per order; an order can have multiple payment rows (e.g. split or installment payments).

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `order_id` | string | Order this payment belongs to | Part of **Verified composite PK** `(order_id, payment_sequential)`; also **Verified FK** → `orders.order_id` (1:many, 0% unmatched) | — |
| `payment_sequential` | int64 | Sequence number of the payment within the order | Part of **Verified composite PK** | — |
| `payment_type` | string | Payment method (e.g. credit_card, boleto, voucher) | Attribute | — |
| `payment_installments` | int64 | Number of installments | Attribute | — |
| `payment_value` | float64 | Amount paid | Attribute | — |

---

## 6. `reviews` — 99,224 rows, 7 columns

**Business purpose:** Post-purchase customer satisfaction survey responses.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `review_id` | string | Nominal review identifier | **Flagged (data-quality)** — verified **NOT unique**: 789 duplicated values, 1,603 affected rows, across 1,412 distinct orders | Do not use as a standalone join key; cause of duplication not assumed, only documented |
| `order_id` | string | Order being reviewed | **Verified FK** → `orders.order_id` (1:many, 0% unmatched) | Some orders have more than one review row |
| `review_score` | int64 | Customer satisfaction score | Attribute | Verified: 0 missing, 0 values outside the expected 1–5 range; mean 4.09, median 5.0, std 1.35 |
| `review_comment_title` | string | Optional short review title | Attribute | High null rate (optional field) |
| `review_comment_message` | string | Optional free-text review comment | Attribute | High null rate (optional field) |
| `review_creation_date` | string (parses to datetime) | Date the review request was sent | Attribute | — |
| `review_answer_timestamp` | string (parses to datetime) | Timestamp the customer submitted the review | Attribute | — |

---

## 7. `products` — 32,951 rows, 9 columns

**Business purpose:** Product catalog — category and physical dimensions.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `product_id` | string | Unique product identifier | **Verified PK** (32,951 / 32,951 unique) | — |
| `product_category_name` | string | Product category, in Portuguese | **Verified FK** → `category_translation.product_category_name` (text-based join, not a surrogate id; 13 rows / 0.04% unmatched — WARNING) | A small number of products reference a category name absent from the translation table |
| `product_name_lenght` | float64 | Character length of the product name | Attribute | Column name retained exactly as spelled in the original Olist source ("lenght") |
| `product_description_lenght` | float64 | Character length of the product description | Attribute | Same spelling note as above |
| `product_photos_qty` | float64 | Number of product photos | Attribute | — |
| `product_weight_g` | float64 | Product weight in grams | Attribute | — |
| `product_length_cm` | float64 | Product length in cm | Attribute | — |
| `product_height_cm` | float64 | Product height in cm | Attribute | — |
| `product_width_cm` | float64 | Product width in cm | Attribute | — |

---

## 8. `sellers` — 3,095 rows, 4 columns

**Business purpose:** Seller / marketplace-partner master data.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `seller_id` | string | Unique seller identifier | **Verified PK** (3,095 / 3,095 unique) | — |
| `seller_zip_code_prefix` | int64 | First digits of the seller's Brazilian ZIP code | **Inferred FK** → `geolocation.geolocation_zip_code_prefix` (many-to-many; 7 rows / 0.23% unmatched — WARNING) | Same ZIP-prefix caveat as `customers` |
| `seller_city` | string | Seller's city name | Attribute | — |
| `seller_state` | string | Seller's state abbreviation | Attribute | — |

---

## 9. `category_translation` — 71 rows, 2 columns

**Business purpose:** Bridge/lookup table translating Portuguese product category names into English.

| Column | Data type | Description | Key role | Analytical notes |
|---|---|---|---|---|
| `product_category_name` | string | Product category name, in Portuguese | **Verified PK** (71 / 71 unique) | Referenced by `products.product_category_name` |
| `product_category_name_english` | string | English translation of the category name | Attribute | — |

---

## Customer Identifier: `customer_id` vs. `customer_unique_id`

This distinction is central to the dataset and must not be confused in any downstream analysis:

| | `customers.customer_id` | `customers.customer_unique_id` |
|---|---|---|
| **Role** | Order-scoped surrogate key | Persistent real-world customer identifier |
| **Uniqueness in `customers`** | **Verified unique** — 99,441 / 99,441 rows | **NOT unique** — 96,096 distinct values across 99,441 rows |
| **Uniqueness in `orders.customer_id`** | Verified unique (99,441 / 99,441) — genuinely **1:1** with `orders` | N/A directly (not a column in `orders`) |
| **Relationship to orders when deduplicated** | 1:1 (each `customer_id` maps to exactly one order) | **1:many** — up to **17 orders** for a single real customer; **2,997 customers** placed more than 1 order |
| **Is it a primary key of `customers`?** | Yes — verified | **No.** It is explicitly **not** the primary key of the raw `customers` table; it is a non-unique attribute that identifies the same real person across multiple `customer_id`/order rows |
| **Correct usage** | Join key for order-level relationships (`orders`, and transitively `order_items`, `payments`, `reviews`) | The correct grain for any customer-level analysis (RFM, CLV, segmentation — planned for later weeks). A deduplicated view (one row per `customer_unique_id`, referred to as `customers_unique_view` in the notebook) must be used to avoid double-counting real customers |

**Why this matters:** each time the same real person places a new order, Olist's schema generates a brand-new `customer_id` (and a new row in `customers`). This is why `customer_id` → `orders.customer_id` audits as a clean 1:1 relationship — that is factually correct for those exact columns, not a data-quality defect. It does **not** mean each customer only orders once; that real-world fact is only visible through `customer_unique_id`.
