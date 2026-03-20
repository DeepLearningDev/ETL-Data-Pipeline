SELECT
    transaction_month,
    ROUND(SUM(CASE WHEN direction = 'debit' THEN amount ELSE 0 END), 2) AS debit_total,
    ROUND(SUM(CASE WHEN direction = 'credit' THEN amount ELSE 0 END), 2) AS credit_total,
    ROUND(SUM(signed_amount), 2) AS net_amount
FROM transactions
GROUP BY transaction_month
ORDER BY transaction_month;

