# Quality assurance report

Executed against the downloaded Kaggle CSV on October 15, 2026.

## Historical automated tests — October 15, 2026

13 unittest cases passed: numeric/date validation; sale/cancellation signs; missing customer retention; fractional quantities; sub-penny rounding; large orders; exact repeats; value reconciliation; repeatable rebuilding. The small test fixtures are synthetic and isolated from the real analysis.

## Full-data controls

- row_partition: PASS
- signed_value_reconciliation: PASS
- monthly_matches_net: PASS
- country_matches_net: PASS
- product_matches_net: PASS
- gross_less_cancellations: PASS
- duplicate_sensitivity: PASS

- Input: 541,909 rows.
- Sale: 530,104; cancellation: 9,288; excluded: 2,517.
- Raw parseable signed value: £9,747,747.93.
- Valued net: £9,769,872.05; excluded signed value: £-22,124.12.
- Exact repeated source occurrences: 5,268.
- Exact-repeat sensitivity net: £9,748,131.07.

The controls compare integer pence, not floating-point approximations. The excluded signed value can be negative and is not an estimate of lost revenue. See `workbook-verification.json` and `independent-verification.json` for additional execution evidence. Native desktop Excel recalculation was not tested; workbook formulas were tested in the artifact-tool calculation engine and exported for Excel.

## Current check — November 1, 2026

All 22 current tests pass, and a fresh full-source run reproduces all seven reconciliations and the documented amounts. The PDF and HTML briefing now state the current 22-test count. Earlier dated counts above describe their original checks. No new native Excel or Tableau refresh was performed.

## October 21 reliability update

The current local suite has 22 passing tests. Regression coverage includes the affected failure paths and portable bundle verification. Native Excel and Power BI checks were not repeated for this code update. See docs/RELIABILITY_UPDATE.md for the change and validation record.
