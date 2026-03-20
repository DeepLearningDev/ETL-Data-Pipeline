SELECT
    category,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount), 2) AS total_spend
FROM transactions
WHERE direction = 'debit'
GROUP BY category
ORDER BY total_spend DESC, category;

