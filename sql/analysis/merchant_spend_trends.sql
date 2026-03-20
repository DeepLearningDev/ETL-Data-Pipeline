SELECT
    t.transaction_month,
    m.merchant_name,
    m.merchant_category,
    COUNT(*) AS transaction_count,
    ROUND(SUM(t.amount), 2) AS total_amount
FROM transactions AS t
JOIN merchants AS m
    ON t.merchant_id = m.merchant_id
WHERE t.direction = 'debit'
GROUP BY t.transaction_month, m.merchant_name, m.merchant_category
ORDER BY t.transaction_month, total_amount DESC, m.merchant_name;

