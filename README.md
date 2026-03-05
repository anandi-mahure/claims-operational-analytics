# Claims Operational Analytics
**Author:** Anandi M | MSc Data Science, University of Bath  
**Tools:** Python · SQL · Pandas · Matplotlib  
**Domain:** Insurance Claims Operations · Operational MI · Data Quality

---

## What This Project Does
End-to-end operational analytics pipeline for insurance claims data — covering settlement performance, handler efficiency, regional exposure, fraud flagging and month-on-month trends. Built to replicate the kind of data work done inside a Claims Insight & Performance team.

---

## Business Questions Answered
| # | Question | Technique |
|---|---|---|
| 1 | Which claim types take longest to settle? | GROUP BY + AVG |
| 2 | Which regions carry the highest financial exposure? | GROUP BY + SUM |
| 3 | Which pending claims have breached SLA? | WHERE + CASE |
| 4 | Which handlers are most efficient? | GROUP BY + settlement rate |
| 5 | Is claims volume growing month on month? | DATE functions + trend |
| 6 | Where are dispute rates highest? | CTE + RANK window function |
| 7 | What is our cumulative financial exposure? | SUM OVER window function |
| 8 | Which claims represent outsized risk per type? | CTE + correlated subquery |

---

## Project Structure
```
claims-operational-analytics/
├── claims_data.csv          # 40-row operational claims dataset
├── analysis_queries.sql     # 8 SQL queries with business context
├── insights.py              # Python analytics + 5 visualisations
├── charts/                  # Output charts (auto-generated)
│   ├── 01_settlement_by_type.png
│   ├── 02_exposure_by_region.png
│   ├── 03_monthly_trend.png
│   ├── 04_handler_scorecard.png
│   └── 05_portfolio_overview.png
└── README.md
```

---

## How To Run
```bash
# Install dependencies
pip install pandas matplotlib numpy

# Run the analytics script
python insights.py

# Charts will be saved to /charts/
```

For SQL queries — run in SQLite, DBeaver, or any SQL client against claims_data.csv imported as a table.

---

## Key Findings
- **Health claims** take ~4.6x longer to settle than Motor claims on average
- **London** carries the highest total exposure but **Leeds** has the highest dispute rate
- **H01** handles the most volume; **H03** has the highest settlement rate
- **15% of claims** are fraud-flagged — all concentrated in Health and Home categories
- Claims volume grew consistently Jan–Apr 2024 with total exposure up ~35%

---

## Skills Demonstrated
`SQL` `CTEs` `Window Functions` `Python` `Pandas` `Matplotlib` `Operational MI` `Data Quality` `KPI Reporting` `Claims Analytics`
