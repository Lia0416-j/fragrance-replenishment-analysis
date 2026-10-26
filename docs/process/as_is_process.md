# As-Is Replenishment Process

The editable swimlane diagram is in [`as_is_process.drawio`](as_is_process.drawio). Open it at [app.diagrams.net](https://app.diagrams.net) (File → Open from → Device).

## Regular order cycle

```mermaid
flowchart LR
    subgraph SA[Sales Advisor]
        A1[Count shelf and stockroom weekly]
        A5[Receive delivery, check and shelve]
        D{Damaged on arrival?}
    end
    subgraph MGR[Counter Manager]
        S((Order day, every 2 weeks))
        M2[Check last 2 weeks of sales]
        M3[Decide quantity from experience]:::pain
        M4[Place order]
        M7[Submit claim to brand]
    end
    subgraph BR[Brand / Warehouse]
        B1[Receive order and ship, about 7 days]
        B3[Process claim]
    end
    S --> A1 --> M2 --> M3 --> M4 --> B1 --> A5 --> D
    D -- Yes --> M7 --> B3
    D -- No --> E((Done))
    classDef pain fill:#f8cecc,stroke:#b85450
```

## Promotion

```mermaid
flowchart LR
    P1[Brand notifies upcoming promotion] --> P2[No extra stock ordered before promotion]:::pain
    P2 --> P3[Promotion starts, sales spike] --> P4[Best sellers run out]:::pain
    P4 --> P5[Manager places urgent top-up order] --> P6[Brand ships, about 7 days]
    P6 --> P7[Stock arrives after the peak, gifts already gone, overstock]:::pain
    classDef pain fill:#f8cecc,stroke:#b85450
```

## Pain points

| # | Step | Problem | Effect |
| --- | --- | --- | --- |
| 1 | Decide quantity from experience | Uses last 2 weeks of sales. Stockout weeks look like low demand. | Best sellers get smaller orders and run out again |
| 2 | Decide quantity from experience | The order must cover 21 days (14 until next order plus 7 days delivery), but only 14 days of sales are used | Stock is short before the next delivery |
| 3 | No extra stock before promotion | Promotions are known in advance but not planned into orders | Stockouts in the first days of a promotion, when demand is highest |
| 4 | Urgent top-up order | Takes about 7 days to arrive | Stock arrives after the peak. For GWP, gifts are often gone, so the extra stock sits on the shelf |
| 5 | Weekly stock count | Shrinkage and claims are not linked to ordering | System stock and shelf stock drift apart |

## Open questions and assumptions

| Question | Assumption used in this project |
| --- | --- |
| How often are orders placed? | Every two weeks |
| How long does delivery take? | About 7 days, including urgent orders |
| How far ahead are promotions announced? | At least 21 days |
| Is promotion stock allocated by the brand or ordered with regular stock? | Ordered with regular stock |
| How many gifts per promotion, and who pays for them? | Fixed quantity per promotion, shared across products. Paid by the brand. |
| Are products ordered in full cases? | Yes, case size recorded in `products.case_size` |
