-- Country labels are source labels, not mapped to current political geography.
SELECT country, SUM(CASE WHEN kind='sale' THEN amount_pence ELSE 0 END) AS gross_pence,
 -SUM(CASE WHEN kind='cancellation' THEN amount_pence ELSE 0 END) AS cancellation_pence,
 SUM(amount_pence) AS net_pence,
 COUNT(DISTINCT CASE WHEN kind='sale' THEN invoice END) AS sale_invoices
FROM valued_lines GROUP BY country ORDER BY net_pence DESC,country;
