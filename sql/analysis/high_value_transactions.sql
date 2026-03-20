SELECT
    transaction_id,
    transaction_date,
    account_id,
    customer_id,
    merchant_id,
    category,
    amount,
    direction,
    description
FROM transactions
WHERE amount >= 250
ORDER BY amount DESC, transaction_date;
