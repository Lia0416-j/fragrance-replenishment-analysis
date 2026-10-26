# Power Query Cleaning

The cleaning is done in Excel Power Query. The M code for every query is in [`powerquery/`](../powerquery/), one file per query, so each step is visible and repeatable.

## Steps in Excel

1. Open a new Excel workbook and save it as `powerbi/fragrance_cleaning.xlsx`.
2. **Data → Get Data → From Other Sources → Blank Query.** The Power Query editor opens.
3. For each file in `powerquery/`, in order from `00` to `10`:
   - **Home → Advanced Editor**, delete what is there, paste the code from the file, click **Done**.
   - In the **Query Settings** pane on the right, rename the query to the name on the first line of the file (for example `sales`).
   - Create the next one with **Home → New Source → Other Sources → Blank Query**.
4. In `DataFolder`, change the path to the `data\raw\` folder on your computer. Keep the backslash at the end.
5. **Home → Close & Load To...** Load `daily_stock`, `weekly_stock`, `gwp_daily_phase` and `sales` as tables. Load the other queries as **Only Create Connection**.
6. Compare the results with the checks below.

## What each query does

| Query | Cleaning and new columns |
| --- | --- |
| `DataFolder` | Folder path, so the workbook works on any computer |
| `fnLoadCsv` | Reads a CSV as UTF-8, promotes headers, turns blank cells into null |
| `products` | Sets data types |
| `promotions` | Sets data types, adds `promo_days` |
| `sales` | Trims and upper-cases `product_id`, removes duplicate rows, fills blank `discount_pct` with 0, adds `sales_amount`, `gross_profit`, `brand`, `category`, `promo_type`, `in_promotion` |
| `stock_receipts` | Sets data types, adds `in_transit` |
| `stock_adjustments` | Sets data types, adds `value_at_cost` |
| `claims` | Sets data types, adds `stock_change` (+/−/0), `days_open`, `overdue_30_days` |
| `gwp_daily_phase` | Per GWP promotion and day: gifts given, running total, `gift_phase` (gifts available or gifts gone at the start of the day) |
| `daily_stock` | One row per product per day: received, sold, shrinkage, claims change, opening and closing stock, `stockout_day`, `week_start` |
| `weekly_stock` | One row per product per week (Monday to Sunday): units sold, closing stock, `stockout_days`, `stockout_week` |

The order of the `sales` steps matters: `product_id` is cleaned **before** duplicates are removed, so a duplicate with a badly formatted ID is still caught.

## Checks

These numbers come from the same data processed in Python. If yours match, the cleaning is correct.

| Check | Expected |
| --- | --- |
| `sales` rows | 10,811 (raw file has 10,843, so 32 duplicates removed) |
| `sales` total quantity | 11,171 |
| `sales` total `sales_amount` | $1,979,141.00 |
| `sales` rows with `in_promotion` = TRUE | 1,581 |
| `daily_stock` rows | 14,600 (40 products × 365 days) |
| `daily_stock` lowest `closing_stock` | 0 (never negative) |
| `daily_stock` rows with `stockout_day` = TRUE | 1,495 |
| `weekly_stock` rows | 2,120 |
| `weekly_stock` rows with `stockout_week` = TRUE | 447 |
| `gwp_daily_phase` rows | 127 (94 gifts available, 33 gifts gone) |
| `claims` with status `pending` | 7 |

If the data is regenerated with different settings, these numbers will change. Run `python scripts/check_stock_balance.py` to get the new stockout count.
