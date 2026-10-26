# Requirements: User Stories and Acceptance Criteria

Priorities use MoSCoW (Must, Should, Could, Won't). Key terms are defined in the [glossary](#glossary) at the end.

## Summary

| ID | Stakeholder | Story | Priority |
| --- | --- | --- | --- |
| US01 | Counter manager | Suggested order list before each order | Must |
| US02 | Brand representative | Promotion sales vs baseline | Must |
| US08 | Brand representative | Discount vs GWP comparison | Must |
| US03 | Inventory management | Slow-moving products | Should |
| US04 | Sales advisor | Low-stock alert | Should |
| US06 | Loss prevention | Shrinkage by reason and product | Should |
| US07 | Counter manager | Claims tracking | Should |
| US10 | Counter manager | Back-test of the new reorder process | Should |
| US05 | Counter manager | Brand sales ranking | Could |
| US09 | Counter manager | Automatic ordering to brands | Won't |

## Must

### US01 Suggested order list

**As a** counter manager, **I want** a suggested order list before each order (every two weeks), **so that** I can reduce stockouts.

**Acceptance criteria**

- **Given** it is an order day, **when** I open the order list, **then** each product shows current stock, stock on order, weekly baseline sales, forecast sales for the next 21 days and the suggested order quantity.
- **Given** a promotion falls within the next 21 days, **when** the forecast is calculated, **then** promotion days use the uplift for that promotion type, and GWP days are split into before and after the gifts run out.
- **Given** current stock plus stock on order already covers the forecast and safety stock, **when** the order quantity is calculated, **then** it shows 0, not a negative number.
- **Given** the order quantity is above 0, **when** it is shown, **then** it is rounded up to a full case.

### US02 Promotion sales vs baseline

**As a** brand representative, **I want** to compare promotion sales with normal sales, **so that** I can see whether a promotion worked.

**Acceptance criteria**

- **Given** I select a promotion, **when** the page loads, **then** it shows promotion sales, the baseline before the promotion and uplift (promotion weekly average ÷ baseline).
- **Then** it also shows sales in the 4 weeks after the promotion compared with the baseline.
- **Given** a product ran out of stock during the promotion, **when** uplift is calculated, **then** stockout days are excluded, and the result shows how many stockout days were excluded.

### US08 Discount vs GWP comparison

**As a** brand representative, **I want** to compare discount and GWP promotions, **so that** I can decide which type to run next time.

**Acceptance criteria**

- **Given** I filter by promotion type or gift item, **when** the page loads, **then** it shows uplift and incremental sales for each promotion.
- **Given** a GWP promotion, **when** it is shown, **then** it also shows the gift run-out date and uplift before and after run-out.
- **Then** each promotion shows sales in the 4 weeks after it ended compared with the baseline.
- **Given** a discount promotion, **when** incremental sales are calculated, **then** the discounted price is used, not the full price.

## Should

### US03 Slow-moving products

**As** inventory management, **I want** to see slow-moving products, **so that** less cash is tied up in stock.

- Lists products where current stock covers more than 8 weeks of baseline sales.
- Shows weeks of cover and stock value at cost.

### US04 Low-stock alert

**As a** sales advisor, **I want** to know which products are about to run out, **so that** I can tell the manager early.

- Products with stock below safety stock are highlighted in red.
- Products with stock at 0 are shown separately at the top.

### US06 Shrinkage

**As** loss prevention, **I want** to see monthly shrinkage by reason and product, **so that** I can find high-risk products.

- Shows shrinkage units, value at cost and shrinkage rate (shrinkage units ÷ units sold) by month.
- Can be filtered by reason: theft, damage, testers, count difference.
- Ranks the top 10 products by shrinkage value.

### US07 Claims tracking

**As a** counter manager, **I want** to track the status of each claim, **so that** money owed by brands is not missed.

- Lists each claim with product, quantity, value, submit date and status.
- Claims open more than 30 days are highlighted in red.
- Shows total value of open claims.

### US10 Back-test of the new reorder process

**As a** counter manager, **I want** to see how the new reorder process would have performed compared with the current one, **so that** I can decide whether to adopt it.

- Both processes run on the same simulated demand, with only the reorder rule changed.
- Shows stockout days, lost sales (units and value), average stock, overstock after promotions and number of urgent orders for each process.
- The new process only uses data available on each order day.

## Could

### US05 Brand sales ranking

**As a** counter manager, **I want** to see sales ranked by brand, **so that** I can decide display space and which brands to push.

- Can be filtered by month and category.

## Won't (this phase)

### US09 Automatic ordering to brands

**As a** counter manager, **I want** the system to place orders with brands automatically.

Not in this phase. It needs integration with external systems, and a wrong automatic order is costly. The manager keeps reviewing and placing orders.

## Why these priorities

- **US01 and US02** are the foundation: reordering and promotion evaluation.
- **US08** answers the core question of the project: should discount and GWP promotions be planned differently? So it is also a Must.
- **US10** proves the new process is better. It is a Should because the order list (US01) is still useful without it.
- **US05** is useful but does not address stockouts or overstock, so it is a Could.
- **US09** is out of scope because of integration cost and risk.

## Traceability

| ID | Pain point ([as-is process](process/as_is_process.md)) | SQL ([list](../sql/README.md)) | Dashboard page |
| --- | --- | --- | --- |
| US01 | 1, 2, 3 | 02, 03, 10 | Stock and reorder |
| US02 | 3 | 04, 07, 08 | Promotion analysis |
| US03 | 4 | 09 | Stock and reorder |
| US04 | 1 | 02 | Stock and reorder |
| US05 | | 01 | Sales overview |
| US06 | 5 | 11 | Shrinkage and claims |
| US07 | 5 | 12, 13 | Shrinkage and claims |
| US08 | 3, 4 | 05, 06, 07, 08 | Promotion analysis |
| US10 | 1 to 4 | | Stock and reorder |

## Glossary

| Term | Definition |
| --- | --- |
| Baseline sales | Normal weekly sales without promotion or stockout. Average of the last 4 weeks after removing promotion weeks and stockout weeks. If fewer than 2 weeks are left, extend to 8 weeks. If still fewer than 2, use the average for the same brand and category. |
| Stockout week | A week with at least one day where closing stock is 0 |
| Uplift | Promotion weekly average sales ÷ baseline |
| Coverage period | Days an order must last: 14 days until the next order plus 7 days delivery = 21 days |
| Forecast sales | Sum over the coverage period of (daily baseline × uplift for that day). Uplift is 1 on normal days. |
| Suggested order quantity | Forecast sales + safety stock − current stock − stock on order, minimum 0, rounded up to full cases |
| Incremental sales | (Promotion sales − baseline × promotion weeks) × actual selling price |
| Gift run-out | The day the total gifts for a promotion have all been given out, across all products in that promotion |
