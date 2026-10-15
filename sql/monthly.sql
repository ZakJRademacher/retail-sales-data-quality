-- One row per observed month; Dec 2011 is partial, through Dec 9.
SELECT substr(invoice_date,1,7) AS month,
 SUM(CASE WHEN kind='sale' THEN amount_pence ELSE 0 END) AS gross_pence,
 -SUM(CASE WHEN kind='cancellation' THEN amount_pence ELSE 0 END) AS cancellation_pence,
 SUM(amount_pence) AS net_pence,
 COUNT(DISTINCT CASE WHEN kind='sale' THEN invoice END) AS sale_invoices,
 SUM(CASE WHEN is_repeat=0 THEN amount_pence ELSE 0 END) AS deduplicated_net_pence
FROM valued_lines GROUP BY month ORDER BY month;
