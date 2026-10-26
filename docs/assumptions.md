# Assumptions and limitations

## Data

- All data is simulated. Brands and products are fictional. Uplift figures and back-test results show the method, not real store performance.
- One year of data, so each seasonal event appears only once. There is no year-on-year comparison.
- Demand lost during stockouts is not visible in the analysis tables. Stockout weeks are excluded from the baseline. True demand is used only in the back-test.
- The store is closed on Good Friday and Christmas Day.

## Ordering

- Orders are placed every two weeks and arrive 7 days later. Coverage period is 21 days. Urgent top-up orders also take 7 days.
- All products are ordered in full cases (`case_size`).
- Current (as-is) rule: last two weeks of sales plus 50% extra from experience, minus stock on hand and on order. No extra stock before promotions.
- Urgent orders use the same trigger under both rules, so the back-test compares only how quantities are calculated: closing stock at or below safety stock, nothing on order, next regular order more than 3 days away.
- Promotion dates are known at least 21 days ahead. When a promotion falls inside the coverage period, the reorder formula applies the uplift automatically, so no separate pre-promotion top-up is added.

## Promotions

- A product takes part in only one promotion at a time. All products of the brand take part.
- Promotion types are discount and GWP only. Spend-threshold gifts count as GWP. Bundles are out of scope.
- Gift stock is shared across all products in a promotion, so the gift run-out date is tracked by `promo_id`.
- Uplift samples are small, so uplift is averaged across all promotions of the same type (discount, GWP before run-out, GWP after run-out).
- The first promotion of each type uses a preset uplift, because there is no history yet.
- Stockout days during a promotion are excluded from the uplift calculation. Days after the product is restocked are still used.
- Uplift is measured against the baseline in the 4 weeks before the promotion. When a promotion falls in a peak season (Mother's Day, Christmas), the measured uplift also includes the seasonal increase.
- The post-promotion dip is not removed from the baseline.

## Stock and claims

- Testers are taken from saleable stock and counted as shrinkage. Gift cost is assumed to be paid by the brand.
- Customer returns are recorded only in `claims`, not as negative sales. Sales figures are gross.
- `quantity_received` includes damaged units. Damage is deducted through `claims`, submitted on the day the delivery arrives.
- All claims affect stock on `submit_date`.
