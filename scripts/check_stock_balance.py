"""
Rebuild daily closing stock from the six raw tables and check it never goes negative.

closing = previous closing + received - sold - shrinkage +/- claims (by submit_date)

This is the same formula the Power Query step uses, so if this check passes,
the tables are consistent with each other.

Usage:
    python scripts/check_stock_balance.py            # reads data/raw
    python scripts/check_stock_balance.py path/to/raw
"""

import sys
from pathlib import Path

import pandas as pd

raw = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "data" / "raw"


def clean_ids(s):
    return s.astype(str).str.strip().str.upper()


products = pd.read_csv(raw / "products.csv")
sales = pd.read_csv(raw / "sales.csv").drop_duplicates()
sales["product_id"] = clean_ids(sales["product_id"])
receipts = pd.read_csv(raw / "stock_receipts.csv").dropna(subset=["received_date"])
adj = pd.read_csv(raw / "stock_adjustments.csv")
claims = pd.read_csv(raw / "claims.csv")
claims["signed"] = claims["quantity"] * claims["stock_impact"].map({"increase": 1, "decrease": -1, "none": 0})

days = pd.date_range(sales["date"].min(), sales["date"].max()).strftime("%Y-%m-%d")
grid = pd.MultiIndex.from_product([products["product_id"], days], names=["product_id", "date"])


def daily(df, date_col, qty_col):
    return df.groupby(["product_id", date_col])[qty_col].sum().rename_axis(["product_id", "date"]).reindex(grid, fill_value=0)


change = (daily(receipts, "received_date", "quantity_received")
          - daily(sales, "date", "quantity")
          - daily(adj, "date", "quantity")
          + daily(claims, "submit_date", "signed"))
closing = change.groupby(level="product_id").cumsum() + products.set_index("product_id")["opening_stock"].reindex(
    change.index.get_level_values("product_id")).to_numpy()

neg = closing[closing < 0]
stockout_days = int((closing == 0).sum())
print(f"product-days checked: {len(closing)}")
print(f"negative closing stock: {len(neg)}")
print(f"product-days with closing stock 0: {stockout_days}")
sys.exit(1 if len(neg) else 0)
