# Assumptions and limitations

## Data

- All data is simulated. Uplift figures and back-test results show the method, not real store performance.
- One year of data, so each seasonal event appears only once.
- Demand lost during stockouts is not visible in the analysis tables. Stockout weeks are excluded from the baseline. True demand is used only in the back-test.

## Ordering

- Orders are placed every two weeks and arrive about 7 days later. Coverage period is 21 days. Urgent top-up orders also take 7 days.
- All products are ordered in full cases (`case_size`).
- Promotion dates are known at least 21 days ahead. When a promotion falls inside the coverage period, the reorder formula applies the uplift automatically, so no separate pre-promotion top-up is added.

## Promotions

- A product takes part in only one promotion at a time.
- Promotion types are discount and GWP only. Spend-threshold gifts count as GWP. Bundles are out of scope.
- Gift stock is shared across all products in a promotion, so the gift run-out date is tracked by `promo_id`.
- Uplift samples are small, so uplift is first calculated by brand or category.
- The first promotion of each type uses a preset uplift, because there is no history yet.
- The post-promotion dip is not removed from the baseline.

## Stock and claims

- Testers are taken from saleable stock and counted as shrinkage. Gift cost is assumed to be paid by the brand.
- Customer returns are recorded only in `claims`, not as negative sales. Sales figures are gross.
- `quantity_received` includes damaged units. Damage is deducted through `claims`.
- All claims affect stock on `submit_date`.
