"""Prepare separate Tableau Public extracts for Week 6.

The script reads the Week 2–5 outputs, writes one CSV per grain under
data/tableau/, and checks those files against the published totals.
It does not modify raw data, processed data, notebooks, or Week 4 scores.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TABLEAU_DIR = PROJECT_ROOT / "data" / "tableau"

SEGMENT_ORDER = [
    "High Value",
    "Medium-High Value",
    "Medium Value",
    "Low Value",
]
SEGMENT_SORT = {name: index + 1 for index, name in enumerate(SEGMENT_ORDER)}
FUNNEL_STAGES = [
    "Orders Placed",
    "Orders with Payment Records",
    "Delivered Orders",
    "Orders with Valid Reviews",
]
REVENUE_TOLERANCE = 0.05

PROTECTED_FILES = [
    PROCESSED_DIR / "olist_order_level_cleaned.csv",
    PROCESSED_DIR / "olist_customer_rfm.csv",
    PROCESSED_DIR / "olist_customer_clv.csv",
    PROCESSED_DIR / "olist_order_distance_analysis.csv",
    PROCESSED_DIR / "olist_quarterly_customer_segments.csv",
    OUTPUT_DIR / "week5_segment_revenue_summary.csv",
    OUTPUT_DIR / "week5_state_month_summary.csv",
    OUTPUT_DIR / "week5_funnel_summary.csv",
    OUTPUT_DIR / "week4_clv_summary.csv",
]


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_bool(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    mapping = {
        True: True,
        False: False,
        "True": True,
        "False": False,
        "true": True,
        "false": False,
        1: True,
        0: False,
    }
    converted = series.map(mapping)
    if converted.isna().any():
        unexpected = series.loc[converted.isna()].unique()[:5]
        raise ValueError(f"Unexpected boolean values: {unexpected}")
    return converted.astype(bool)


def require_unique(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    if frame.duplicated(columns).any():
        duplicates = int(frame.duplicated(columns).sum())
        raise AssertionError(f"{label} has {duplicates:,} duplicate keys on {columns}.")
    if frame[columns].isna().any().any():
        raise AssertionError(f"{label} has a missing key on {columns}.")


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, lineterminator="\n")


def main() -> None:
    source_hashes = {str(path): md5_file(path) for path in PROTECTED_FILES}
    TABLEAU_DIR.mkdir(parents=True, exist_ok=True)

    orders = pd.read_csv(
        PROCESSED_DIR / "olist_order_level_cleaned.csv",
        dtype={"order_id": "string", "customer_unique_id": "string", "customer_state": "string"},
    )
    customers = pd.read_csv(
        PROCESSED_DIR / "olist_customer_clv.csv",
        dtype={"customer_unique_id": "string", "customer_segment": "string"},
    )
    shipments = pd.read_csv(
        PROCESSED_DIR / "olist_order_distance_analysis.csv",
        dtype={
            "order_id": "string",
            "customer_unique_id": "string",
            "customer_state": "string",
            "seller_state": "string",
        },
    )
    payments = pd.read_csv(RAW_DIR / "olist_order_payments_dataset.csv", usecols=["order_id"])
    reviews = pd.read_csv(
        RAW_DIR / "olist_order_reviews_dataset.csv",
        usecols=["order_id", "review_score"],
    )
    week5_segments = pd.read_csv(OUTPUT_DIR / "week5_segment_revenue_summary.csv")
    week5_states = pd.read_csv(
        OUTPUT_DIR / "week5_state_month_summary.csv",
        dtype={"customer_state": "string", "purchase_month": "string"},
    )
    week5_funnel = pd.read_csv(OUTPUT_DIR / "week5_funnel_summary.csv")

    orders["order_id"] = orders["order_id"].str.strip()
    orders["customer_unique_id"] = orders["customer_unique_id"].str.strip()
    orders["customer_state"] = orders["customer_state"].str.strip()
    orders["has_payment_records"] = as_bool(orders["has_payment_records"])
    orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
    customers["customer_unique_id"] = customers["customer_unique_id"].str.strip()
    shipments["order_id"] = shipments["order_id"].str.strip()
    shipments["customer_state"] = shipments["customer_state"].str.strip()
    shipments["seller_state"] = shipments["seller_state"].str.strip()
    shipments["is_delivered_order"] = as_bool(shipments["is_delivered_order"])
    payments["order_id"] = payments["order_id"].astype("string").str.strip()
    reviews["order_id"] = reviews["order_id"].astype("string").str.strip()

    require_unique(orders, ["order_id"], "Week 2 orders")
    require_unique(customers, ["customer_unique_id"], "Week 4 customers")
    require_unique(shipments, ["order_id", "order_item_id"], "Week 3 shipments")

    if set(customers["customer_segment"]) != set(SEGMENT_ORDER):
        raise AssertionError(f"Unexpected segments: {sorted(customers['customer_segment'].dropna().unique())}")
    if customers["clv_score"].isna().any() or customers["customer_segment"].isna().any():
        raise AssertionError("A Week 4 customer is missing a CLV score or segment.")
    if not (
        ((customers["clv_score"] >= 80) & (customers["customer_segment"] == "High Value"))
        | ((customers["clv_score"] >= 60) & (customers["clv_score"] < 80) & (customers["customer_segment"] == "Medium-High Value"))
        | ((customers["clv_score"] >= 40) & (customers["clv_score"] < 60) & (customers["customer_segment"] == "Medium Value"))
        | ((customers["clv_score"] < 40) & (customers["customer_segment"] == "Low Value"))
    ).all():
        raise AssertionError("A customer_segment value does not match the Week 4 thresholds.")

    payment_order_ids = set(payments["order_id"].dropna())
    valid_review_ids = set(
        reviews.loc[reviews["review_score"].between(1, 5), "order_id"].dropna()
    )
    order_ids = set(orders["order_id"])
    payment_flag_ids = set(orders.loc[orders["has_payment_records"], "order_id"])
    stage2_ids = order_ids & payment_order_ids
    if payment_flag_ids != stage2_ids:
        raise AssertionError(
            "Week 2 has_payment_records does not match the distinct payment order_id set."
        )

    delivered_ids = set(orders.loc[orders["order_status"] == "delivered", "order_id"])
    stage3_ids = stage2_ids & delivered_ids
    stage4_ids = stage3_ids & valid_review_ids
    stage_sets = [order_ids, stage2_ids, stage3_ids, stage4_ids]
    if not (stage4_ids <= stage3_ids <= stage2_ids <= order_ids):
        raise AssertionError("Funnel stages are not nested.")

    # Customer extract. One row per scored customer. The Week 4 score is copied.
    customer_extract = customers[
        [
            "customer_unique_id",
            "recency_days",
            "frequency",
            "monetary",
            "average_review_score",
            "rfm_index",
            "clv_score",
            "customer_segment",
        ]
    ].copy()
    customer_extract["review_data_available"] = (
        customer_extract["average_review_score"].notna().astype(int)
    )
    customer_extract["segment_sort"] = customer_extract["customer_segment"].map(SEGMENT_SORT).astype(int)
    customer_extract = customer_extract.sort_values("customer_unique_id").reset_index(drop=True)

    # Order extract. Segment is attached many-to-one and does not add rows.
    segment_lookup = customers[["customer_unique_id", "customer_segment"]].drop_duplicates()
    require_unique(segment_lookup, ["customer_unique_id"], "Segment lookup")
    order_extract = orders[
        [
            "order_id",
            "customer_unique_id",
            "order_purchase_timestamp",
            "order_status",
            "total_product_value",
            "total_freight_value",
            "total_payment_value",
            "primary_payment_type",
            "customer_state",
        ]
    ].merge(segment_lookup, on="customer_unique_id", how="left", validate="m:1")
    if len(order_extract) != len(orders):
        raise AssertionError("Attaching customer_segment changed the order row count.")
    order_extract["segment_sort"] = order_extract["customer_segment"].map(SEGMENT_SORT)
    order_extract["has_payment_record"] = order_extract["order_id"].isin(stage2_ids).astype(int)
    order_extract["is_delivered"] = (order_extract["order_status"] == "delivered").astype(int)
    order_extract["has_valid_review"] = order_extract["order_id"].isin(valid_review_ids).astype(int)
    order_extract["order_purchase_timestamp"] = order_extract["order_purchase_timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    order_extract["segment_sort"] = order_extract["segment_sort"].astype("Int64")
    order_extract = order_extract.sort_values(
        ["order_purchase_timestamp", "order_id"]
    ).reset_index(drop=True)

    delivered_orders = order_extract.loc[order_extract["is_delivered"] == 1].copy()
    delivered_revenue = float(delivered_orders["total_product_value"].sum())
    monetary_by_customer = (
        delivered_orders.groupby("customer_unique_id", as_index=False)["total_product_value"]
        .sum()
        .rename(columns={"total_product_value": "delivered_product_value"})
    )
    monetary_check = customer_extract.merge(
        monetary_by_customer, on="customer_unique_id", how="left", validate="1:1"
    )
    monetary_gap = (
        monetary_check["monetary"] - monetary_check["delivered_product_value"]
    ).abs()
    if monetary_check["delivered_product_value"].isna().any():
        raise AssertionError("A CLV customer has no delivered order in the Week 2 extract.")
    max_monetary_gap = float(monetary_gap.max())

    # State-month grid. Same observed states and months as the Week 5 heat map.
    purchase = order_extract[
        ["order_id", "customer_state", "order_purchase_timestamp", "order_status", "total_product_value", "is_delivered"]
    ].copy()
    missing_state = purchase["customer_state"].isna() | purchase["customer_state"].eq("")
    purchase_mapped = purchase.loc[~missing_state].copy()
    purchase_mapped["purchase_month"] = purchase_mapped["order_purchase_timestamp"].str.slice(0, 7)
    observed_months = sorted(purchase_mapped["purchase_month"].unique())
    states = sorted(purchase_mapped["customer_state"].unique())
    state_month = pd.MultiIndex.from_product(
        [states, observed_months], names=["customer_state", "purchase_month"]
    ).to_frame(index=False)
    volume = purchase_mapped.groupby(["customer_state", "purchase_month"], as_index=False).agg(
        distinct_order_count=("order_id", "nunique"),
        order_rows=("order_id", "size"),
    )
    if not volume["distinct_order_count"].equals(volume["order_rows"]):
        raise AssertionError("A state-month cell is not already one row per order.")
    delivered_volume = (
        purchase_mapped.loc[purchase_mapped["is_delivered"] == 1]
        .groupby(["customer_state", "purchase_month"], as_index=False)
        .agg(
            delivered_order_count=("order_id", "nunique"),
            total_product_revenue=("total_product_value", "sum"),
        )
    )
    state_month = state_month.merge(
        volume[["customer_state", "purchase_month", "distinct_order_count"]],
        on=["customer_state", "purchase_month"],
        how="left",
        validate="1:1",
    )
    state_month = state_month.merge(
        delivered_volume,
        on=["customer_state", "purchase_month"],
        how="left",
        validate="1:1",
    )
    state_month["distinct_order_count"] = state_month["distinct_order_count"].fillna(0).astype(int)
    state_month["delivered_order_count"] = state_month["delivered_order_count"].fillna(0).astype(int)
    state_month["total_product_revenue"] = state_month["total_product_revenue"].fillna(0.0)
    state_month["purchase_month_date"] = pd.to_datetime(
        state_month["purchase_month"] + "-01"
    ).dt.strftime("%Y-%m-%d")
    state_month = state_month[
        [
            "customer_state",
            "purchase_month",
            "purchase_month_date",
            "distinct_order_count",
            "delivered_order_count",
            "total_product_revenue",
        ]
    ].sort_values(["customer_state", "purchase_month"]).reset_index(drop=True)

    # Published funnel. Stage 3 is payment and delivered, not every delivered status.
    funnel_rows = []
    initial_count = len(stage_sets[0])
    for index, (stage_name, stage_ids) in enumerate(zip(FUNNEL_STAGES, stage_sets)):
        order_count = len(stage_ids)
        if index == 0:
            conversion = 100.0
            drop_off = 0
        else:
            previous_count = len(stage_sets[index - 1])
            conversion = 100.0 * order_count / previous_count
            drop_off = previous_count - order_count
        funnel_rows.append(
            {
                "stage_order": index + 1,
                "stage_name": stage_name,
                "order_count": order_count,
                "conversion_percentage": conversion,
                "drop_off_count": drop_off,
                "percentage_of_initial_orders": 100.0 * order_count / initial_count,
            }
        )
    funnel = pd.DataFrame(funnel_rows)

    # Segment profile. Review average excludes customers with no review score.
    total_customers = len(customer_extract)
    profile_rows = []
    for segment in SEGMENT_ORDER:
        segment_customers = customer_extract.loc[customer_extract["customer_segment"] == segment]
        reviewed = segment_customers.loc[
            segment_customers["review_data_available"] == 1, "average_review_score"
        ]
        segment_orders = delivered_orders.loc[delivered_orders["customer_segment"] == segment]
        profile_rows.append(
            {
                "customer_segment": segment,
                "segment_sort": SEGMENT_SORT[segment],
                "customer_count": int(len(segment_customers)),
                "customer_percentage": 100.0 * len(segment_customers) / total_customers,
                "average_clv_score": float(segment_customers["clv_score"].mean()),
                "average_monetary": round(float(segment_customers["monetary"].mean()), 2),
                "total_product_revenue": round(float(segment_orders["total_product_value"].sum()), 2),
                "average_frequency": float(segment_customers["frequency"].mean()),
                "average_recency": float(segment_customers["recency_days"].mean()),
                "average_review_score": float(reviewed.mean()),
            }
        )
    segment_profile = pd.DataFrame(profile_rows)
    segment_profile["revenue_share"] = (
        100.0
        * segment_profile["total_product_revenue"]
        / segment_profile["total_product_revenue"].sum()
    )

    shipment_extract = shipments[
        [
            "order_id",
            "order_item_id",
            "customer_state",
            "seller_state",
            "distance_km",
            "delivery_delay_days",
        ]
    ].copy()
    shipment_extract["is_delivered_order"] = shipments["is_delivered_order"].astype(int)
    shipment_extract["order_item_id"] = shipment_extract["order_item_id"].astype(int)
    shipment_extract = shipment_extract.sort_values(["order_id", "order_item_id"]).reset_index(drop=True)

    customer_path = TABLEAU_DIR / "tableau_customer_clv.csv"
    order_path = TABLEAU_DIR / "tableau_orders.csv"
    state_path = TABLEAU_DIR / "tableau_state_month.csv"
    funnel_path = TABLEAU_DIR / "tableau_funnel.csv"
    segment_path = TABLEAU_DIR / "tableau_segment_profile.csv"
    shipment_path = TABLEAU_DIR / "tableau_shipments.csv"
    for path, frame in [
        (customer_path, customer_extract),
        (order_path, order_extract),
        (state_path, state_month),
        (funnel_path, funnel),
        (segment_path, segment_profile),
        (shipment_path, shipment_extract),
    ]:
        write_csv(frame, path)

    checks: list[dict[str, object]] = []

    def add_check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    reloaded = {
        "customers": pd.read_csv(customer_path),
        "orders": pd.read_csv(order_path),
        "state_month": pd.read_csv(state_path),
        "funnel": pd.read_csv(funnel_path),
        "segment_profile": pd.read_csv(segment_path),
        "shipments": pd.read_csv(shipment_path),
    }
    customers_out = reloaded["customers"]
    orders_out = reloaded["orders"]
    state_out = reloaded["state_month"]
    funnel_out = reloaded["funnel"]
    segment_out = reloaded["segment_profile"]
    shipments_out = reloaded["shipments"]

    add_check(
        "Customer row count matches Week 4",
        len(customers_out) == len(customers) == customers_out["customer_unique_id"].nunique(),
        f"{len(customers_out):,} rows; Week 4 customers {len(customers):,}",
    )
    add_check(
        "Customer primary key has no duplicates or missing values",
        customers_out["customer_unique_id"].is_unique and customers_out["customer_unique_id"].notna().all(),
        f"duplicate rows {int(customers_out['customer_unique_id'].duplicated().sum()):,}; "
        f"missing keys {int(customers_out['customer_unique_id'].isna().sum()):,}",
    )
    add_check(
        "Order row count matches Week 2",
        len(orders_out) == len(orders) == orders_out["order_id"].nunique(),
        f"{len(orders_out):,} rows; Week 2 orders {len(orders):,}",
    )
    add_check(
        "Order primary key has no duplicates or missing values",
        orders_out["order_id"].is_unique and orders_out["order_id"].notna().all(),
        f"duplicate rows {int(orders_out['order_id'].duplicated().sum()):,}; "
        f"missing keys {int(orders_out['order_id'].isna().sum()):,}",
    )
    add_check(
        "Shipment composite key has no duplicates or missing values",
        not shipments_out.duplicated(["order_id", "order_item_id"]).any()
        and shipments_out[["order_id", "order_item_id"]].notna().all().all(),
        f"{len(shipments_out):,} rows; duplicate keys "
        f"{int(shipments_out.duplicated(['order_id', 'order_item_id']).sum()):,}",
    )
    add_check(
        "State-month composite key has no duplicates",
        not state_out.duplicated(["customer_state", "purchase_month"]).any()
        and state_out[["customer_state", "purchase_month"]].notna().all().all(),
        f"{len(state_out):,} rows; duplicate keys "
        f"{int(state_out.duplicated(['customer_state', 'purchase_month']).sum()):,}",
    )
    add_check(
        "Funnel has one row per stage and a unique stage order",
        list(funnel_out["stage_order"]) == [1, 2, 3, 4]
        and funnel_out["stage_name"].is_unique,
        f"stages {funnel_out['stage_name'].tolist()}",
    )
    add_check(
        "Segment profile has one row per baseline segment",
        segment_out["customer_segment"].tolist() == SEGMENT_ORDER
        and segment_out["customer_segment"].is_unique,
        f"segments {segment_out['customer_segment'].tolist()}",
    )

    saved_delivered_revenue = float(
        orders_out.loc[orders_out["order_status"] == "delivered", "total_product_value"].sum()
    )
    add_check(
        "Delivered product revenue reconciles to the Week 2 delivered orders",
        abs(saved_delivered_revenue - delivered_revenue) <= REVENUE_TOLERANCE,
        f"extract R$ {saved_delivered_revenue:,.2f}; Week 2 delivered R$ {delivered_revenue:,.2f}",
    )
    add_check(
        "Customer monetary sums to delivered product revenue",
        abs(float(customers_out["monetary"].sum()) - delivered_revenue) <= REVENUE_TOLERANCE,
        f"monetary sum R$ {float(customers_out['monetary'].sum()):,.2f}; "
        f"max customer gap R$ {max_monetary_gap:,.6f}",
    )
    add_check(
        "Segment revenue sums to delivered product revenue",
        abs(float(segment_out["total_product_revenue"].sum()) - delivered_revenue) <= REVENUE_TOLERANCE,
        f"segment revenue R$ {float(segment_out['total_product_revenue'].sum()):,.2f}",
    )
    add_check(
        "State-month revenue sums to delivered product revenue",
        abs(float(state_out["total_product_revenue"].sum()) - delivered_revenue) <= REVENUE_TOLERANCE,
        f"state-month revenue R$ {float(state_out['total_product_revenue'].sum()):,.2f}",
    )
    share_total = float(segment_out["revenue_share"].sum())
    add_check(
        "Revenue shares sum to 100",
        abs(share_total - 100) <= 0.01,
        f"sum of revenue_share = {share_total:.6f}",
    )
    customer_share_total = float(segment_out["customer_percentage"].sum())
    add_check(
        "Customer percentages sum to 100",
        abs(customer_share_total - 100) <= 0.01,
        f"sum of customer_percentage = {customer_share_total:.6f}",
    )
    add_check(
        "Segment customer counts sum to the Week 4 population",
        int(segment_out["customer_count"].sum()) == len(customers),
        f"profile customers {int(segment_out['customer_count'].sum()):,}",
    )

    state_compare = state_out.merge(
        week5_states,
        on=["customer_state", "purchase_month"],
        how="outer",
        indicator=True,
        validate="1:1",
    )
    left_count = "distinct_order_count_x"
    right_count = "distinct_order_count_y"
    if right_count not in state_compare.columns:
        raise AssertionError(f"State-month comparison columns: {list(state_compare.columns)}")
    count_mismatch = int((state_compare[left_count].fillna(-1) != state_compare[right_count].fillna(-2)).sum())
    revenue_mismatch = int(
        (
            (
                state_compare["total_product_revenue"].fillna(0)
                - state_compare["delivered_product_revenue"].fillna(0)
            ).abs()
            > 0.01
        ).sum()
    )
    add_check(
        "State-month distinct orders match the Week 5 heat map",
        (state_compare["_merge"] == "both").all()
        and count_mismatch == 0
        and int(state_out["distinct_order_count"].sum()) == len(orders_out) - int(missing_state.sum()),
        f"cells {len(state_out):,}; count mismatches {count_mismatch:,}; "
        f"order total {int(state_out['distinct_order_count'].sum()):,}; "
        f"orders without a state {int(missing_state.sum()):,}",
    )
    add_check(
        "State-month delivered revenue matches the Week 5 cell values",
        revenue_mismatch == 0
        and int(state_out["delivered_order_count"].sum()) == int((orders_out["order_status"] == "delivered").sum()),
        f"revenue cell mismatches {revenue_mismatch:,}; "
        f"delivered orders {int(state_out['delivered_order_count'].sum()):,}",
    )

    funnel_compare = funnel_out.merge(
        week5_funnel,
        left_on="stage_order",
        right_on="stage_number",
        how="outer",
        validate="1:1",
    )
    funnel_count_mismatch = int((funnel_compare["order_count_x"] != funnel_compare["order_count_y"]).sum())
    funnel_drop_mismatch = int(
        (funnel_compare["drop_off_count"] != funnel_compare["drop_off_from_previous_stage"]).sum()
    )
    funnel_conversion_mismatch = int(
        (
            (funnel_compare["conversion_percentage"] - funnel_compare["conversion_from_previous_stage"]).abs()
            > 1e-9
        ).sum()
    )
    add_check(
        "Funnel counts, conversion, and drop-off match Week 5",
        funnel_count_mismatch == 0 and funnel_drop_mismatch == 0 and funnel_conversion_mismatch == 0,
        "stage counts "
        + " > ".join(f"{int(value):,}" for value in funnel_out["order_count"])
        + f"; count mismatches {funnel_count_mismatch}",
    )
    funnel_counts = funnel_out["order_count"].tolist()
    add_check(
        "Funnel stage counts are non-increasing",
        all(funnel_counts[index] >= funnel_counts[index + 1] for index in range(len(funnel_counts) - 1)),
        " >= ".join(f"{int(value):,}" for value in funnel_counts),
    )

    week5_segment_compare = segment_out.merge(
        week5_segments,
        on="customer_segment",
        how="outer",
        validate="1:1",
    )
    customer_count_mismatch = int(
        (week5_segment_compare["customer_count_x"] != week5_segment_compare["customer_count_y"]).sum()
    )
    revenue_profile_mismatch = int(
        (
            (
                week5_segment_compare["total_product_revenue"]
                - week5_segment_compare["delivered_product_revenue"]
            ).abs()
            > 0.01
        ).sum()
    )
    add_check(
        "Segment profile matches the Week 5 customer counts and revenue",
        customer_count_mismatch == 0 and revenue_profile_mismatch == 0,
        f"customer-count mismatches {customer_count_mismatch}; revenue mismatches {revenue_profile_mismatch}",
    )

    timestamp_pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
    month_pattern = r"^\d{4}-\d{2}$"
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    add_check(
        "Order timestamps use YYYY-MM-DD HH:MM:SS",
        orders_out["order_purchase_timestamp"].str.match(timestamp_pattern).all()
        and orders_out["order_purchase_timestamp"].notna().all(),
        f"unparsed timestamps {int((~orders_out['order_purchase_timestamp'].str.match(timestamp_pattern)).sum()):,}",
    )
    add_check(
        "State-month dates use YYYY-MM and YYYY-MM-DD",
        state_out["purchase_month"].str.match(month_pattern).all()
        and state_out["purchase_month_date"].str.match(date_pattern).all(),
        f"months {state_out['purchase_month'].nunique()}; first {state_out['purchase_month'].min()}; "
        f"last {state_out['purchase_month'].max()}",
    )

    numeric_customer = ["recency_days", "frequency", "monetary", "rfm_index", "clv_score", "segment_sort"]
    numeric_orders = [
        "total_product_value",
        "total_freight_value",
        "total_payment_value",
        "has_payment_record",
        "is_delivered",
        "has_valid_review",
    ]
    numeric_state = ["distinct_order_count", "delivered_order_count", "total_product_revenue"]
    numeric_shipments = ["order_item_id", "distance_km", "delivery_delay_days", "is_delivered_order"]
    numeric_ok = (
        all(pd.api.types.is_numeric_dtype(customers_out[column]) for column in numeric_customer)
        and all(pd.api.types.is_numeric_dtype(orders_out[column]) for column in numeric_orders)
        and all(pd.api.types.is_numeric_dtype(state_out[column]) for column in numeric_state)
        and all(pd.api.types.is_numeric_dtype(shipments_out[column]) for column in numeric_shipments)
        and pd.api.types.is_numeric_dtype(funnel_out["order_count"])
        and pd.api.types.is_numeric_dtype(segment_out["average_clv_score"])
    )
    add_check(
        "Measure columns reload as numeric values",
        numeric_ok,
        "customer, order, state-month, shipment, funnel, and segment measures are numeric",
    )
    add_check(
        "Missing reviews remain null on the customer extract",
        int(customers_out["average_review_score"].isna().sum())
        == int((customers_out["review_data_available"] == 0).sum())
        == int(customers["average_review_score"].isna().sum()),
        f"customers without a review score {int(customers_out['average_review_score'].isna().sum()):,}",
    )
    orders_without_segment = int(orders_out["customer_segment"].isna().sum())
    delivered_without_segment = int(
        ((orders_out["order_status"] == "delivered") & orders_out["customer_segment"].isna()).sum()
    )
    add_check(
        "Every delivered order has a Week 4 segment",
        delivered_without_segment == 0,
        f"delivered orders without a segment {delivered_without_segment:,}; "
        f"all orders without a segment {orders_without_segment:,}",
    )
    shipment_orders = set(shipments_out["order_id"])
    orders_without_items = order_ids - shipment_orders
    shipments_without_orders = shipment_orders - order_ids
    add_check(
        "Shipment orders are a subset of the order extract",
        len(shipments_without_orders) == 0,
        f"shipment rows {len(shipments_out):,}; distinct shipment orders {len(shipment_orders):,}; "
        f"orders with no shipment row {len(orders_without_items):,}",
    )
    state_on_shipments = (
        shipments_out.groupby("order_id", as_index=False)["customer_state"].nunique(dropna=False)
    )
    conflicting_shipment_states = int((state_on_shipments["customer_state"] != 1).sum())
    add_check(
        "Each shipment order has one customer state",
        conflicting_shipment_states == 0 and shipments_out["customer_state"].notna().all(),
        f"orders with conflicting customer_state {conflicting_shipment_states:,}",
    )

    changed = [path.name for path in PROTECTED_FILES if md5_file(path) != source_hashes[str(path)]]
    add_check(
        "Week 2–5 source files were not modified",
        not changed,
        "protected files unchanged" if not changed else "changed: " + ", ".join(changed),
    )

    top_states = (
        state_out.groupby("customer_state", as_index=False)["distinct_order_count"]
        .sum()
        .sort_values(["distinct_order_count", "customer_state"], ascending=[False, True])
        .head(5)
    )
    top_months = (
        state_out.groupby("purchase_month", as_index=False)["distinct_order_count"]
        .sum()
        .sort_values(["distinct_order_count", "purchase_month"], ascending=[False, True])
        .head(5)
    )
    summary = {
        "delivered_product_revenue": round(saved_delivered_revenue, 2),
        "customers": int(len(customers_out)),
        "orders": int(len(orders_out)),
        "delivered_orders": int((orders_out["order_status"] == "delivered").sum()),
        "orders_without_segment": orders_without_segment,
        "customers_without_review": int(customers_out["average_review_score"].isna().sum()),
        "shipment_rows": int(len(shipments_out)),
        "shipment_orders": int(len(shipment_orders)),
        "orders_without_shipment": int(len(orders_without_items)),
        "state_month_rows": int(len(state_out)),
        "states": int(state_out["customer_state"].nunique()),
        "months": int(state_out["purchase_month"].nunique()),
        "missing_customer_state_orders": int(missing_state.sum()),
        "delivered_without_payment": int(len(delivered_ids - stage2_ids)),
        "max_customer_monetary_gap": max_monetary_gap,
        "null_counts": {
            "orders_primary_payment_type": int(orders_out["primary_payment_type"].isna().sum()),
            "orders_total_payment_value": int(orders_out["total_payment_value"].isna().sum()),
            "orders_customer_state": int(orders_out["customer_state"].isna().sum()),
            "shipments_seller_state": int(shipments_out["seller_state"].isna().sum()),
            "shipments_distance_km": int(shipments_out["distance_km"].isna().sum()),
            "shipments_delivery_delay_days": int(shipments_out["delivery_delay_days"].isna().sum()),
            "shipments_delay_on_delivered": int(
                shipments_out.loc[shipments_out["is_delivered_order"] == 1, "delivery_delay_days"].isna().sum()
            ),
            "shipments_delay_on_non_delivered": int(
                shipments_out.loc[shipments_out["is_delivered_order"] == 0, "delivery_delay_days"].notna().sum()
            ),
        },
        "top_states": top_states.to_dict(orient="records"),
        "top_months": top_months.to_dict(orient="records"),
        "segments": segment_out.to_dict(orient="records"),
        "funnel": funnel_out.to_dict(orient="records"),
        "status_counts": orders_out["order_status"].value_counts(dropna=False).astype(int).to_dict(),
    }
    checks_frame = pd.DataFrame(checks)
    write_csv(checks_frame, TABLEAU_DIR / "validation_checks.csv")
    (TABLEAU_DIR / "validation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    failed = checks_frame.loc[~checks_frame["passed"]]
    print(checks_frame.to_string(index=False))
    print(json.dumps(summary, indent=2))
    if len(failed):
        raise SystemExit(f"{len(failed)} validation checks failed.")
    print(f"All {len(checks_frame)} validation checks passed.")


if __name__ == "__main__":
    main()
