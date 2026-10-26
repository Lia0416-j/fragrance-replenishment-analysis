# Problem Statement

## Summary

The fragrance counter reorders stock every two weeks based on the last two weeks of sales and the manager's experience. Best sellers run out during promotions, especially gift with purchase (GWP) events, while slow sellers sit on the shelf for months. This causes lost sales, cash tied up in stock, and system stock that does not match what is on the shelf.

## Who is affected

| Group | How they are affected |
| --- | --- |
| Sales advisors | Customers leave without buying when a product is out of stock |
| Counter manager | Misses sales targets and spends time on urgent top-up orders |
| Brand representatives | Promotions underperform when stock runs out early |
| Inventory management | Cash is tied up in slow-moving stock |
| Loss prevention | Shrinkage and claims make stock records unreliable |

## Root causes

1. **Ordering looks backwards.** Orders are based on the last two weeks of sales. If a product was out of stock, its sales look low, so the next order is smaller and the stockout repeats.
2. **Promotions are not planned into orders.** Stock is not increased before a promotion. Extra stock is only ordered once sales spike, and it takes about 7 days to arrive.
3. **Promotion types are treated the same.** Discount and GWP promotions have very different uplift. GWP sales drop sharply once the gifts run out, but ordering does not account for this, which leads to overstock after the event.
4. **Stock records drift.** Shrinkage (theft, damage, testers, count differences) and claims are not tracked in a way that feeds into ordering.

## Impact

To be measured from the simulated data and filled in after the analysis:

- Average stockout days per best seller during promotions: **X days**
- Lost sales from stockouts: **$X per year**
- Products with more than 8 weeks of cover: **X products, $X in stock**
- Monthly shrinkage rate: **X%**

## Scope

**In scope**

- One fragrance counter, about 40 products, 12 months of simulated data
- Reorder process every two weeks
- Discount and GWP promotions
- Shrinkage and claims tracking

**Out of scope**

- Automatic ordering to brands (see US09)
- Bundle promotions
- Multiple stores

## Success measures

The new reorder process will be compared with the current one on the same simulated demand. It is considered better if it:

- Reduces stockout days and lost sales
- Does not increase average stock by more than it saves in lost sales
- Reduces overstock after promotions
- Reduces urgent top-up orders
