# Retail Data Quality Review — local Tableau guide

**Business question:** Which cleaning choices change the answer?

Open [the packaged workbook](../deliverables/Retail%20Data%20Quality%20Review.twbx) in Tableau Desktop Free Edition 2026.3. Its reporting CSV is included. Nothing is published to Tableau Public. Use F7 to enter or leave presentation mode; hover marks for context, select marks to inspect them, or open the underlying worksheets to edit the analysis.

## What this report demonstrates

The brief puts the headline result beside the comparisons that explain it. Its native Tableau charts use prepared Python/SQL aggregates. The KPI and explanatory text describe the fixed historical population; there are no global date filters. Arbitrary filtering of a worksheet does not recompute the fixed text. The companion reports and case study remain available from the repository overview.

18 reporting records from 541,909 source lines. Preferred net GBP 9,769,872.05; exact-repeat sensitivity GBP 21,740.98; unidentified gross positive sales GBP 1,755,276.64.

The source, currency, period and limitations appear on the dashboard. The date and population labels matter when reading this fixed historical brief. Its comparisons do not establish causes or profit.

## Reproduce and edit

1. Follow the repository README to run the original validated Python/SQL pipeline. Locate the published `retail.sqlite` through the current snapshot pointer.
2. Close the report before regenerating its source. From the project root run `python tools/build_tableau.py --database "ABSOLUTE_PATH_TO_VALIDATED_DATABASE"`. This rebuilds the fixed historical brief, reporting CSV and verification record together. Historical assertions intentionally reject a different source population.
3. Open `tableau/Retail Data Quality Review.twb`, verify all three charts, then save once in Tableau. Native save materializes connection and member metadata used by the palette.
4. Run `python tools/package_tableau.py "." "Retail Data Quality Review"` to create the portable TWBX with data and source notices. Reopen the package and visually check all labels, colors and interpretation text.
5. For a new business period, deliberately update the extraction dates, assertions, KPI calculations, interpretation and attribution together. This brief is not an unattended rolling report.

`Data/analysis.csv` contains View, Label, Series, Value, Sort and Note. Values are in GBP. Each View is a separate chart population. `verification.json` records the CSV fingerprint and scope. Python builders use only the standard library. See the existing source/licensing guide for underlying data rights.

## Your practice task

Explain why missing customer identity does not invalidate the recorded money. Hover the three policy bars and identify which change would inflate net value. Do not add the counterfactual policies together.

Acceptance: explain the population, measure, comparison and next action without reading the project code. Change one worksheet and show that its totals still reconcile. Keep the modified copy and its reconciliation with your practice notes.
