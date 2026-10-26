# Fragrance Counter Stock Replenishment Analysis

A business analysis portfolio project based on a department store fragrance counter. It goes from a business problem to requirements, data analysis and a back-tested recommendation for a data-driven reorder process.

> **All data in this repository is simulated. It does not represent any real store, brand or company.**

## Business problem

Replenishment at the counter is based on experience. Best sellers often run out, slow sellers pile up, and both get worse during promotions. Discount and gift with purchase (GWP) promotions affect sales very differently, and sales drop once the gifts run out, but ordering does not tell them apart. Shrinkage and claims also make system stock differ from actual stock.

## Goals

- Find patterns in stockouts and overstock
- Measure promotion uplift by type (discount vs GWP)
- Design a data-driven reorder process
- Back-test the new process against the current approach on the same simulated demand

## Tools

Excel, Power Query, SQL (SQLite), Power BI, Python (data simulation), draw.io

## Repository structure

| Folder | Contents |
| --- | --- |
| `docs/` | Problem statement, stakeholders, user stories, assumptions |
| `docs/process/` | As-is and to-be process maps (draw.io) |
| `scripts/` | Data simulation script with a switchable reorder rule |
| `data/raw/` | Six simulated tables |
| `data/processed/` | Cleaned data and the daily stock table |
| `data/validation/` | True demand file, used only for back-testing |
| `sql/` | Analysis queries, one file per business question |
| `powerbi/` | Dashboard file and screenshots |
| `reports/` | Back-test results and recommendation report |

## Status

- [x] Week 1: [Problem statement](docs/01_problem_statement.md), [stakeholders](docs/02_stakeholders.md), [as-is process](docs/process/as_is_process.md)
- [x] Week 2: [User stories and acceptance criteria](docs/03_requirements.md)
- [ ] Week 3: Data simulation and Power Query cleaning
- [ ] Week 4: SQL part 1 (sales, stock, baseline, reorder, shrinkage, claims)
- [ ] Week 5: SQL part 2 (promotion uplift, GWP analysis, incremental sales)
- [ ] Week 6: Power BI dashboard
- [ ] Week 7: Back-test, to-be process, recommendation report
