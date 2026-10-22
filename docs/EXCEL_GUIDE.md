# Excel guide

The workbook uses two sheets: **Sales review** for monthly inputs, formulas, headline results and a chart, and **Country detail** for geographic inputs and share calculations. All monetary cells are GBP. Blue-font imported cells are SQL aggregates; dark formula cells calculate derived results.

## Monthly workflow

The monthly table has Month, Gross GBP, Cancellations GBP, Net GBP, Sale invoices, Average invoice GBP, Net without repeats GBP, and Repeat impact GBP. Net is gross less cancellations; average invoice is gross divided by sale invoices; repeat impact is net less the deduplicated sensitivity. Top metrics link to this same table.

After rerunning Python, replace the monthly imported columns with `monthly.csv` from the directory printed by `python src/publication.py`, converting pence to pounds once. Keep formula columns intact. The delivered template contains the 13 observed months; to add months, insert table rows, copy formulas, extend the chart and the bounded summary ranges. It does not automatically ingest arbitrary future periods.

December 2011 is visibly labeled partial. It is not comparable with a whole month. No forecast or target is implied.

## Country workflow

Refresh imported Country, Gross GBP, Cancellations GBP and Sale invoices from `countries.csv`. Net and share formulas recompute. Sorting should include whole rows. Country labels are retained from the source.

## Verification and reproduction

The build checks headline values against Python's independent integer-pence results, tests a temporary input change and its dependent formulas, scans formula errors, renders both sheets and exports XLSX. The report states the engine used. Native desktop Excel was not available for an additional application-level recalculation test.

`tools/build_workbook.mjs` uses the optional `@oai/artifact-tool` spreadsheet authoring package. In a compatible Node environment, make that dependency resolvable, then run:

```sh
node tools/build_workbook.mjs /absolute/path/to/project
```

The Python pipeline and all SQL reports remain independent of this optional spreadsheet-authoring dependency.

## Current published results

Run `python src/publication.py` to locate the current snapshot before opening generated CSVs. The root-level result files are reference examples when a latest.json pointer exists. See [result versions](RESULT_VERSIONS.md).

Workbook authoring also uses Python 3.10+ for display-only theme metadata normalization. Set `PYTHON` to its executable if `python` is unavailable. This helper preserves native workbook parts and does not recalculate formulas.
