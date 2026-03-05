-- ============================================================
-- CLAIMS OPERATIONAL ANALYTICS
-- Author: Anandi M | MSc Data Science, University of Bath
-- Description: SQL analysis of insurance claims operations
--              covering settlement performance, handler efficiency,
--              regional trends and fraud indicators
-- ============================================================


-- ── QUERY 1 ──────────────────────────────────────────────────
-- Average settlement time by claim type
-- Business question: Which claim types take longest to settle?
-- Technique: GROUP BY + AVG + ORDER BY
-- ──────────────────────────────────────────────────────────────
SELECT
    claim_type,
    COUNT(claim_id)                          AS total_claims,
    ROUND(AVG(settlement_days), 1)           AS avg_settlement_days,
    ROUND(MIN(settlement_days), 1)           AS fastest_days,
    ROUND(MAX(settlement_days), 1)           AS slowest_days
FROM claims_data
WHERE status = 'Settled'
GROUP BY claim_type
ORDER BY avg_settlement_days DESC;


-- ── QUERY 2 ──────────────────────────────────────────────────
-- Total and average claim value by region
-- Business question: Which regions carry the highest financial exposure?
-- Technique: GROUP BY + SUM + AVG + ROUND
-- ──────────────────────────────────────────────────────────────
SELECT
    region,
    COUNT(claim_id)                          AS total_claims,
    SUM(claim_amount)                        AS total_exposure,
    ROUND(AVG(claim_amount), 0)              AS avg_claim_value,
    MAX(claim_amount)                        AS largest_claim
FROM claims_data
GROUP BY region
ORDER BY total_exposure DESC;


-- ── QUERY 3 ──────────────────────────────────────────────────
-- Claims pending over 30 days — operational backlog alert
-- Business question: Which claims need urgent intervention?
-- Technique: WHERE + multiple conditions + CASE statement
-- ──────────────────────────────────────────────────────────────
SELECT
    claim_id,
    customer_id,
    claim_type,
    claim_date,
    settlement_days,
    claim_amount,
    handler_id,
    CASE
        WHEN settlement_days > 60 THEN 'Critical — Over 60 Days'
        WHEN settlement_days > 30 THEN 'Warning — Over 30 Days'
        ELSE 'Within SLA'
    END                                      AS sla_status
FROM claims_data
WHERE status = 'Pending'
  AND settlement_days > 30
ORDER BY settlement_days DESC;


-- ── QUERY 4 ──────────────────────────────────────────────────
-- Handler performance scorecard
-- Business question: Which handlers are most/least efficient?
-- Technique: GROUP BY + AVG + COUNT + HAVING
-- ──────────────────────────────────────────────────────────────
SELECT
    handler_id,
    COUNT(claim_id)                          AS claims_handled,
    ROUND(AVG(settlement_days), 1)           AS avg_days_to_settle,
    SUM(CASE WHEN status = 'Disputed' THEN 1 ELSE 0 END)  AS disputed_claims,
    SUM(CASE WHEN status = 'Pending'  THEN 1 ELSE 0 END)  AS pending_claims,
    ROUND(
        SUM(CASE WHEN status = 'Settled' THEN 1.0 ELSE 0 END)
        / COUNT(claim_id) * 100, 1
    )                                        AS settlement_rate_pct
FROM claims_data
GROUP BY handler_id
ORDER BY avg_days_to_settle ASC;


-- ── QUERY 5 ──────────────────────────────────────────────────
-- Month-on-month claim volume and value trend
-- Business question: Is claims volume growing or shrinking over time?
-- Technique: DATE functions + GROUP BY + trend analysis
-- ──────────────────────────────────────────────────────────────
SELECT
    strftime('%Y-%m', claim_date)            AS claim_month,
    COUNT(claim_id)                          AS claims_volume,
    SUM(claim_amount)                        AS total_value,
    ROUND(AVG(claim_amount), 0)              AS avg_value,
    SUM(CASE WHEN fraud_flag = 1 THEN 1 ELSE 0 END) AS flagged_claims
FROM claims_data
GROUP BY strftime('%Y-%m', claim_date)
ORDER BY claim_month ASC;


-- ── QUERY 6 ──────────────────────────────────────────────────
-- Top regions by disputed claim rate — using CTE + RANK window function
-- Business question: Where are dispute rates highest and why?
-- Technique: CTE + window function RANK() OVER
-- ──────────────────────────────────────────────────────────────
WITH regional_disputes AS (
    SELECT
        region,
        COUNT(claim_id)                      AS total_claims,
        SUM(CASE WHEN status = 'Disputed' THEN 1 ELSE 0 END) AS disputed,
        ROUND(
            SUM(CASE WHEN status = 'Disputed' THEN 1.0 ELSE 0 END)
            / COUNT(claim_id) * 100, 1
        )                                    AS dispute_rate_pct
    FROM claims_data
    GROUP BY region
)
SELECT
    region,
    total_claims,
    disputed,
    dispute_rate_pct,
    RANK() OVER (ORDER BY dispute_rate_pct DESC) AS dispute_rank
FROM regional_disputes
ORDER BY dispute_rank;


-- ── QUERY 7 ──────────────────────────────────────────────────
-- Running total of claim amounts over time — window function
-- Business question: What is our cumulative financial exposure trend?
-- Technique: SUM() OVER (ORDER BY) window function
-- ──────────────────────────────────────────────────────────────
SELECT
    claim_date,
    claim_id,
    claim_type,
    claim_amount,
    SUM(claim_amount) OVER (
        ORDER BY claim_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                        AS running_total_exposure,
    AVG(claim_amount) OVER (
        ORDER BY claim_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )                                        AS rolling_7_avg
FROM claims_data
ORDER BY claim_date;


-- ── QUERY 8 ──────────────────────────────────────────────────
-- Claims above average amount per claim type — CTE + subquery
-- Business question: Which claims represent outsized financial risk per type?
-- Technique: CTE + correlated subquery + comparison
-- ──────────────────────────────────────────────────────────────
WITH type_averages AS (
    SELECT
        claim_type,
        ROUND(AVG(claim_amount), 0)          AS avg_amount_for_type
    FROM claims_data
    GROUP BY claim_type
)
SELECT
    c.claim_id,
    c.claim_type,
    c.claim_amount,
    t.avg_amount_for_type,
    ROUND(c.claim_amount - t.avg_amount_for_type, 0) AS above_average_by,
    ROUND(c.claim_amount / t.avg_amount_for_type * 100, 1) AS pct_of_type_avg,
    c.status,
    c.fraud_flag
FROM claims_data c
JOIN type_averages t ON c.claim_type = t.claim_type
WHERE c.claim_amount > t.avg_amount_for_type
ORDER BY above_average_by DESC;
