SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    a.account_id,
    a.account_type,
    a.status,
    ROUND(a.current_balance, 2) AS current_balance,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(SUM(CASE WHEN t.direction = 'debit' THEN t.amount ELSE 0 END), 2) AS debit_spend,
    ROUND(SUM(CASE WHEN t.direction = 'credit' THEN t.amount ELSE 0 END), 2) AS credit_inflow
FROM customers AS c
JOIN accounts AS a
    ON c.customer_id = a.customer_id
LEFT JOIN transactions AS t
    ON a.account_id = t.account_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    a.account_id,
    a.account_type,
    a.status,
    a.current_balance
ORDER BY customer_name, a.account_id;
