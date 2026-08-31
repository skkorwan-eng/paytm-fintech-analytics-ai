-- Paytm Payments & Fraud Analytics — SQL Queries

-- 1. Chargeback impact
SELECT COUNT(*) AS total_transactions,
       COUNT(DISTINCT user_id) AS unique_users,
       SUM(amount_inr) AS total_amount
FROM transactions
WHERE status = 'chargeback';

-- 2. Burner accounts: chargebacks where account age is 0–29 days
SELECT t.transaction_id, t.user_id, u.signup_date,
       t.transaction_time, t.amount_inr, t.status
FROM transactions t
JOIN users u ON t.user_id = u.user_id
WHERE t.status = 'chargeback'
  AND julianday(t.transaction_time) - julianday(u.signup_date) >= 0
  AND julianday(t.transaction_time) - julianday(u.signup_date) < 30
ORDER BY t.transaction_time;

-- 3. Velocity attacks: 3+ transactions within a 10-minute window
SELECT t1.user_id,
       t1.transaction_time AS first_transaction,
       COUNT(*) AS transactions_in_10_minutes
FROM transactions t1
JOIN transactions t2
  ON t1.user_id = t2.user_id
 AND t2.transaction_time >= t1.transaction_time
 AND t2.transaction_time <= datetime(t1.transaction_time, '+10 minutes')
GROUP BY t1.user_id, t1.transaction_time
HAVING COUNT(*) >= 3
ORDER BY transactions_in_10_minutes DESC;

-- 4. Top 10 merchants by transaction amount
SELECT m.merchant_id, m.merchant_name, m.category, m.region,
       COUNT(t.transaction_id) AS transaction_count,
       SUM(t.amount_inr) AS total_amount
FROM merchants m
LEFT JOIN transactions t ON m.merchant_id = t.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.category, m.region
ORDER BY total_amount DESC
LIMIT 10;

-- 5. Status summary
SELECT status,
       COUNT(*) AS transaction_count,
       SUM(amount_inr) AS total_amount,
       COUNT(DISTINCT user_id) AS unique_users
FROM transactions
GROUP BY status
ORDER BY total_amount DESC;

-- 6. Payment-method summary
SELECT payment_method,
       COUNT(*) AS transaction_count,
       COUNT(DISTINCT user_id) AS unique_users,
       SUM(amount_inr) AS total_amount,
       AVG(amount_inr) AS average_amount
FROM transactions
GROUP BY payment_method
ORDER BY total_amount DESC;

-- 7. Region summary using INNER JOIN + HAVING
SELECT m.region,
       COUNT(t.transaction_id) AS transaction_count,
       SUM(t.amount_inr) AS total_amount
FROM transactions t
INNER JOIN merchants m ON t.merchant_id = m.merchant_id
GROUP BY m.region
HAVING SUM(t.amount_inr) > 50000
ORDER BY total_amount DESC;
