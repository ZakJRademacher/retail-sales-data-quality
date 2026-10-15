-- Rank stock codes, not descriptions: descriptions can vary for the same SKU.
WITH totals AS (
 SELECT sku, MAX(description) AS example_description,
 SUM(CASE WHEN kind='sale' THEN quantity ELSE 0 END) AS units_sold,
 -SUM(CASE WHEN kind='cancellation' THEN quantity ELSE 0 END) AS cancelled_units,
 SUM(amount_pence) AS net_pence,
 SUM(CASE WHEN kind='sale' THEN amount_pence ELSE 0 END) AS gross_pence
 FROM valued_lines GROUP BY sku
)
SELECT DENSE_RANK() OVER (ORDER BY net_pence DESC) AS revenue_rank,*
FROM totals ORDER BY net_pence DESC,sku;
