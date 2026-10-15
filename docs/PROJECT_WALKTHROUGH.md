# Project walkthrough

## Explain the result to a client

The problem is a transaction export with cancellations, blank identifiers and ambiguous repeats. The goal is an accurate, repeatable sales review rather than deleting every awkward row. The workflow keeps an untouched source representation, classifies every line, and reconciles every total.

Review the files and run the tests before discussing the implementation in an interview. It is a personal public-data case study, not a prior paid engagement.

## Python

`src/download_data.py` downloads the Kaggle ZIP and extracts only the expected `data.csv` member. `src/pipeline.py` validates column order, normalizes values, uses Decimal for money and batches database inserts. Every original record and exclusion is traceable through `row_id`. `normalize()` has no I/O, so tests exercise missing inputs, signs, invalid dates, decimal rounding and large orders independently.

## SQL

- `monthly.sql`: conditional aggregation for gross and cancellation values, COUNT DISTINCT for invoices, and a deduplicated sensitivity.
- `countries.sql`: geographic grouping from the same eligible view, maintaining consistent population rules.
- `products.sql`: a CTE aggregates by stock code; DENSE_RANK ranks net value. Description is an example label and never a grouping key.
- `customer_repeat.sql`: a CTE calculates invoice frequency per known customer, then compares single- and multi-invoice customers. Missing IDs stay out of this analysis but remain in aggregate revenue.
- `exclusion_summary.sql` and `quality_flags.sql`: distinguish mutually exclusive exclusions from overlapping quality flags.

## Spreadsheet

Inspect the gross-less-cancellation formula and average-sale-invoice formula. Change one gross-sales input and confirm the summary and chart react. Restore it afterward. Read the partial-period warning before comparing months.

## Questions to be ready for

Why retain cancellations? They reduce net transaction value and are part of the source history. Why retain repeated lines? The source lacks a unique line key, so deletion is an assumption; a sensitivity makes its effect explicit. Why keep missing customer IDs? Aggregate sale value can still be valid without an identified customer. Why no profit number? There is no cost field. Why no December collapse conclusion? The final month ends on December 9.

## Adapting to a real job

First confirm the client's column schema, currency, timestamp convention, record grain, cancellation policy and unique identifiers. Agree whether exact repeats should be removed. Preserve their original export, then add tests for their rules and independently reconcile to their control totals. Do not simply reuse this historical dataset's policies without agreement.
