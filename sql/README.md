# SQL queries

Each file answers one business question.

| File | Business question | User story |
| --- | --- | --- |
| `01_weekly_monthly_sales.sql` | Weekly and monthly sales by product | US05 |
| `02_daily_stock_and_stockouts.sql` | Daily closing stock, stockout weeks and days | US01, US04 |
| `03_baseline_sales.sql` | Weekly baseline excluding promotion and stockout weeks | US01 |
| `04_promo_uplift.sql` | Promotion sales vs baseline | US02 |
| `05_discount_vs_gwp.sql` | Uplift by promotion type and gift item | US08 |
| `06_gwp_sellout.sql` | Gift run-out date, uplift before and after | US08 |
| `07_incremental_sales.sql` | Incremental sales per promotion | US02, US08 |
| `08_post_promo_dip.sql` | Sales in the 4 weeks after a promotion vs baseline | US02, US08 |
| `09_slow_movers.sql` | Products with more than 8 weeks of cover | US03 |
| `10_reorder_suggestion.sql` | Suggested order quantity for the next order | US01 |
| `11_shrinkage.sql` | Monthly shrinkage rate by product and reason | US06 |
| `12_open_claims.sql` | Claims open more than 30 days | US07 |
| `13_damage_claims_by_brand.sql` | Damaged-on-arrival claims by brand | US07 |
