# Data Charter

## Project Overview

| Field | Value |
|---|---|
| **Project name** | Interactive Customer Lifetime Value and Segmentation Analytics System for E-Commerce |
| **Dataset name** | Brazilian E-Commerce Public Dataset by Olist |
| **Data source** | Kaggle (`olistbr/brazilian-ecommerce`), originally released by Olist |
| **Domain** | E-commerce / retail marketplace analytics |
| **Geographic scope** | Brazil — orders placed across multiple Brazilian states, 2016–2018 |
| **Dataset structure** | 9 relational CSV tables joined via `order_id`, `customer_id`, `customer_unique_id`, `product_id`, `seller_id`, `review_id`, and ZIP-code prefix fields (see `docs/data_dictionary/data_dictionary.md` and `docs/er_diagram/`) |
| **Number of tables** | 9 (`customers`, `geolocation`, `order_items`, `payments`, `reviews`, `orders`, `products`, `sellers`, `category_translation`) |

## Main Analytical Purpose

To build a Customer Lifetime Value (CLV) and segmentation analytics system for an e-commerce marketplace: understand purchasing behavior, delivery performance, and review sentiment at the order and customer level, then (in later weeks) derive RFM features, model CLV, segment customers, and surface results in an interactive dashboard.

## Intended Use

- Internal analytics / educational and portfolio project.
- Non-commercial use only, consistent with the dataset's license (see [Licensing](#dataset-licensing--source) below).
- Outputs (processed datasets, dashboards) are intended for demonstration and analysis, not resale or commercial redistribution of the underlying data.

## Data Granularity

- **Order-item level** (finest grain): `order_items`, one row per purchased line item.
- **Order level**: `orders`, `payments`, `reviews` — one or more rows per order (`payments` and `reviews` can have multiple rows per order).
- **Real-customer level**: only correctly represented via `customer_unique_id`, **not** `customer_id` (which is order-scoped — see the Data Dictionary's Customer Identifier section). A deduplicated one-row-per-real-customer view (`customers_unique_view`) is required for this grain.
- **Product / seller / category dimensions**: `products`, `sellers`, `category_translation`.
- **Geographic (ZIP-prefix) level**: `geolocation`, joined to `customers`/`sellers` many-to-many via ZIP-code prefix (not a unique key).

## Important Data-Quality Considerations

Findings from the Week 1 audit (`notebooks/01_week1_data_audit.ipynb`), to be respected by all downstream work:

1. **`reviews.review_id` is not unique** — 789 duplicated values, 1,603 affected rows, across 1,412 distinct orders. Flagged for audit; not deduplicated or explained, only documented.
2. **`geolocation` ZIP-code prefix is not unique** — 19,015 unique prefixes across 1,000,163 rows. Joins to `customers`/`sellers` are many-to-many; a representative coordinate must be chosen before spatial analysis.
3. **Missing delivery dates** — 2,965 orders (2.98%) have no `order_delivered_customer_date`; delivery delay cannot be computed for these and they must be excluded, not imputed.
4. **Minor referential-integrity warnings** — `products.product_category_name` → `category_translation` (0.04% unmatched), `customers`/`sellers` ZIP-prefix → `geolocation` (0.28% / 0.23% unmatched).
5. **Minor delivery-date sequence anomalies** — 166 rows (0.17%) where `order_delivered_carrier_date` precedes `order_purchase_timestamp`; 23 rows (0.02%) where `order_delivered_customer_date` precedes `order_delivered_carrier_date`.
6. **Extreme delivery delays** — 2,830 orders (2.93%) exceed the IQR-based upper bound (8.4 days); retained for review, not removed, since they may reflect genuine operational failures relevant to CLV.
7. **`customer_id` vs. `customer_unique_id`** — `customer_id` is order-scoped (verified 1:1 with `orders`); the real, repeatable customer identity is `customer_unique_id` (96,096 distinct customers; up to 17 orders per customer; 2,997 customers with more than 1 order). All customer-level work must key off `customer_unique_id`.

No missing-value imputation, deduplication, or anomaly removal has been performed on the raw data — Week 1 is audit and documentation only.

## Planned Downstream Use (RFM, CLV, Segmentation)

- **Not yet implemented.** Week 1 deliverables are limited to data understanding, the ER map, and this documentation.
- When implemented in later weeks:
  - RFM (Recency, Frequency, Monetary) features and CLV will be computed at the **`customer_unique_id`** grain, joining `orders`, `order_items`, and `payments` as needed.
  - Segmentation will be derived from those RFM/CLV features.
  - Results will be surfaced via a Tableau dashboard (planned, not yet built).
  - All of the data-quality considerations above (missing dates, duplicate `review_id`, ZIP-prefix ambiguity) will be explicitly handled at that stage, not silently ignored.

## Data-Processing Principles

1. **Raw data is preserved.** Files in `data/raw/` are treated as an immutable, read-only source of truth and are never modified, overwritten, or deduplicated in place.
2. **Transformations happen separately.** Any parsing (e.g. string dates to datetime), deduplication (e.g. `customers_unique_view`), or joins for analysis are performed on in-memory copies within notebooks/scripts, or written out as new files under `data/processed/` or `data/output/` — never back into `data/raw/`.
3. **Findings are evidence-based.** All audit results (uniqueness, referential integrity, anomaly counts) are computed directly from the actual loaded data, not assumed; findings are labeled **Verified**, **Inferred**, or **Flagged for audit** based on what the data actually shows.
4. **No silent data removal.** Anomalies, duplicates, and outliers are documented and flagged, not deleted, unless a future step explicitly decides otherwise for a stated analytical reason.
5. **Reproducibility.** All profiling and audit logic lives in version-controlled notebook code (`notebooks/01_week1_data_audit.ipynb`) rather than manual, one-off edits.

---

## Dataset Licensing & Source

| Field | Value |
|---|---|
| **Original dataset** | Brazilian E-Commerce Public Dataset by Olist |
| **Original data owner / publisher** | Olist (`www.olist.com`), published on Kaggle |
| **Source URL** | https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce |
| **License** | **CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International) |
| **License reference** | https://creativecommons.org/licenses/by-nc-sa/4.0/ |

**How this was verified:** the license was confirmed directly from Kaggle's own dataset metadata for `olistbr/brazilian-ecommerce` (the `licenseName` field returned by Kaggle's public dataset API), not inferred or guessed. This project's `docs/data_dictionary/data_charter.md` records that confirmation as of the date this document was written.

### License Terms (as documented by CC BY-NC-SA 4.0)

- **Attribution (BY):** Credit must be given to Olist as the original data source.
- **NonCommercial (NC):** The dataset may not be used for commercial purposes. This project is treated as non-commercial (educational/portfolio analytics).
- **ShareAlike (SA):** If the dataset (or a derivative of it) is redistributed, it must be shared under the same CC BY-NC-SA 4.0 license.
- **Anonymization note (per source documentation):** Olist anonymized the data; company and partner names referenced in review text were replaced with fictional (Game of Thrones house) names.

### Suggested Attribution / Citation

> Olist. *Brazilian E-Commerce Public Dataset by Olist.* Kaggle. https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

### Caveat

License terms on third-party platforms can change over time. Before any commercial use, public redistribution, or publication beyond internal/educational analysis, **re-verify the current license directly on the live Kaggle dataset listing** rather than relying solely on this document.
