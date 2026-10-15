SELECT 'missing customer ID, retained when otherwise valid' AS flag,COUNT(*) AS rows
FROM lines WHERE customer IS NULL
UNION ALL SELECT 'missing description, retained when otherwise valid',COUNT(*) FROM lines WHERE description=''
UNION ALL SELECT 'exact repeated source row, retained',COUNT(*) FROM raw_rows WHERE is_repeat=1;
