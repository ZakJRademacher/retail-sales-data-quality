# Case study: retail sales and data quality

Personal portfolio project. Actual public Kaggle/UCI data; no private employer or client data.

## The problem

A retail export needs cleanup without losing valid sales, hiding cancellations or assuming repeated lines are errors. The project produces an auditable report and explicit decision rules.

## Findings

- Valued net transaction value is £9,769,872.05: £10,666,684.54 gross positive sales less £896,812.49 in cancellations.
- November 2011 has the highest net value among complete observed months: £1,461,756.25. December 2011 is partial and cannot support a full-month comparison.
- The United Kingdom contributes 84.0% of valued net transaction value. Its concentration should be considered before treating these results as a broad international benchmark.
- Missing customer IDs occur in 135,080 records. Identifying customers is not necessary to retain their £1,755,276.64 in gross sales.
- Removing all exact repeated occurrences would reduce net value by £21,740.98 (0.2%). This is a sensitivity, not evidence that every repeat is an error.
- Among 4,338 identified purchase customers, 2,845 (65.6%) have multiple purchase invoices. This excludes unknown customer IDs.

## Deliverables

Python ingestion and normalization; SQLite database with original-row lineage; six SQL reports; full cleaned and exception CSVs; formula-based Excel review; business report; tests; data dictionary and refresh documentation.

## Interpretation

Use the report to prioritize clarification of repeats and unknown customer IDs, and to compare complete observed months. It does not estimate profit, business savings, inventory availability or future sales. Special charge codes remain included in transaction value. See METHOD.md for all rules.
