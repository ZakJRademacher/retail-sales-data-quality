-- Exclusive primary reasons; quality flags can overlap and are reported separately.
SELECT reason,COUNT(*) AS rows,COALESCE(SUM(amount_pence),0) AS signed_pence
FROM lines WHERE kind='excluded' GROUP BY reason ORDER BY rows DESC,reason;
