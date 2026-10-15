-- Denominator includes only identified customers with at least one sale invoice.
WITH customers AS (
 SELECT customer,COUNT(DISTINCT invoice) AS sale_invoices,SUM(amount_pence) AS gross_pence
 FROM valued_lines WHERE kind='sale' AND customer IS NOT NULL GROUP BY customer
)
SELECT CASE WHEN sale_invoices=1 THEN 'one purchase invoice' ELSE 'multiple purchase invoices' END AS customer_group,
 COUNT(*) AS customers,SUM(sale_invoices) AS sale_invoices,SUM(gross_pence) AS gross_pence
FROM customers GROUP BY customer_group ORDER BY customer_group;
