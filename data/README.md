# Data Dictionary

> All data is simulated by [`scripts/generate_data.py`](../scripts/generate_data.py). Brands and products are fictional. Nothing here comes from a real store.

12 months (1 Jan to 31 Dec 2025), one counter, 40 products from 8 brands. The store is closed on Good Friday and Christmas Day.

## How the data is generated

- The simulation runs **day by day, product by product**. Each day: deliveries arrive, claims are applied, shrinkage happens, then customers buy.
- **Sales can never exceed stock on hand.** When demand is higher than stock, the extra demand is lost and does not appear in `sales`. This is how stockouts happen naturally.
- **Deliveries come from the current (as-is) reorder rule**: every two weeks, order the last two weeks of sales plus 50% extra from experience, minus stock on hand and on order, rounded up to full cases. No extra stock before promotions.
- **Urgent top-up orders** are placed when closing stock is at or below safety stock, nothing is on order and the next regular order is more than 3 days away. Delivery takes 7 days for all orders.
- Demand includes seasonality (Valentine's Day, Mother's Day, Father's Day, Black Friday, Christmas, Boxing Day), weekday patterns and promotion uplift. GWP uplift drops once the gifts for that promotion run out.

Run `python scripts/check_stock_balance.py` to rebuild daily stock from these tables and confirm it never goes negative.

## raw/products.csv

| Field | Type | Description |
| --- | --- | --- |
| product_id | text | P001 to P040 |
| brand | text | One of 8 fictional brands |
| product_name | text | Scent name, concentration and size |
| category | text | Women, Men or Unisex |
| size_ml | integer | 30, 50 or 100 |
| price | number | Full retail price (AUD) |
| cost | number | Cost price (AUD), 55% of price |
| safety_stock | integer | Minimum stock to hold, about 4 days of normal sales |
| opening_stock | integer | Stock on hand at the start of 1 Jan 2025 |
| case_size | integer | Units per case. Orders are in full cases. |

## raw/sales.csv

One row per transaction.

| Field | Type | Description |
| --- | --- | --- |
| sale_id | text | Unique transaction ID |
| date | date | Sale date |
| product_id | text | Product sold |
| quantity | integer | Units in this transaction (1 or 2) |
| unit_price | number | Price paid per unit, **after** discount |
| discount_pct | number | Discount applied, e.g. 0.2 = 20% |
| promo_id | text | Promotion this sale belongs to. Blank if none. |
| gift_given | 0/1 | 1 if a gift with purchase was given |

Customer returns are not recorded here. They are in `claims`. Sales figures are gross.

## raw/stock_receipts.csv

One row per order line.

| Field | Type | Description |
| --- | --- | --- |
| receipt_id | text | Unique ID |
| order_date | date | Date the order was placed |
| received_date | date | Date it arrived. **Blank = still in transit.** |
| product_id | text | Product ordered |
| order_type | text | `regular` (every two weeks) or `urgent` (top-up) |
| quantity_ordered | integer | Units ordered |
| quantity_received | integer | Units received, **including** any damaged units. Damage is deducted through `claims`. |

## raw/promotions.csv

| Field | Type | Description |
| --- | --- | --- |
| promo_id | text | PR01 to PR19 |
| name | text | Promotion name |
| promo_type | text | `discount` or `gwp` (gift with purchase) |
| start_date, end_date | date | Promotion period, inclusive |
| discount_pct | number | Discount for discount promotions, 0 for GWP |
| brand | text | All products of this brand take part |
| gift_item | text | Gift for GWP promotions |
| gift_qty | integer | Total gifts for this promotion, **shared across all products** in it |
| qualifying_rule | text | `Any purchase`, `50ml or larger` or `Spend $150 or more` |

A product is in at most one promotion at a time.

## raw/stock_adjustments.csv

Shrinkage: stock lost that cannot be recovered.

| Field | Type | Description |
| --- | --- | --- |
| adj_id | text | Unique ID |
| date | date | Date of the loss |
| product_id | text | Product |
| quantity | integer | Units lost (positive number) |
| reason | text | `theft`, `damage`, `tester` or `count_difference` |

## raw/claims.csv

| Field | Type | Description |
| --- | --- | --- |
| claim_id | text | Unique ID |
| submit_date | date | Date submitted. **Stock changes on this date.** |
| product_id | text | Product |
| quantity | integer | Units (positive number) |
| claim_value | number | Cost value for brand claims, price paid for customer returns |
| claim_type | text | `damaged_on_arrival`, `quality_issue` or `customer_return` |
| stock_impact | text | `decrease`, `increase` (return put back on shelf) or `none` |
| status | text | `pending`, `approved`, `refunded` or `rejected` |
| resolved_date | date | Blank if still pending |

## validation/true_demand.csv

**For the back-test only.** Daily demand per product, including demand that could not be met because of stockouts. The analysis and SQL must not use this file, because a real counter cannot see lost demand.

| Field | Type | Description |
| --- | --- | --- |
| date | date | Day |
| product_id | text | Product |
| true_demand | integer | Units customers wanted to buy |

`validation/metrics_as_is.json` holds the back-test metrics for the current reorder rule.

## Daily stock formula

```
closing stock = previous closing stock
              + quantity_received (by received_date)
              - sales quantity
              - shrinkage quantity
              + claims with stock_impact = increase (by submit_date)
              - claims with stock_impact = decrease (by submit_date)
```

Day 1 starts from `products.opening_stock`. A stockout day is a day with closing stock 0.

## Intentional data quality issues

`sales.csv` contains a few problems on purpose, to practise cleaning in Power Query:

| Issue | About how many rows | Fix |
| --- | --- | --- |
| Exact duplicate rows | 0.3% | Remove duplicates |
| `product_id` in lower case or with a leading space | 1% | Trim and convert to upper case |
| `discount_pct` blank instead of 0 | 2% of non-discounted rows | Replace blank with 0 |

All other files are clean. Run the generator with `--clean` to get a file without these issues.
