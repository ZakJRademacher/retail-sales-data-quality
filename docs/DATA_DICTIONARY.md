# Data dictionary

## Original CSV (Latin-1 encoding)

| Field | Type preserved/parsed | Meaning |
|---|---|---|
| InvoiceNo | text | Invoice identifier; initial C denotes cancellation |
| StockCode | text | Product or special charge code; preserve leading zeroes |
| Description | text, may be blank | Source description; not a unique product master |
| Quantity | integer | Signed item quantity |
| InvoiceDate | month/day/year hour:minute | Timestamp; no timezone supplied |
| UnitPrice | decimal GBP | Unit price; may be nonpositive in source |
| CustomerID | text or blank | Anonymous customer key; blank remains unknown |
| Country | text | Source customer country label |

## Database

`raw_rows`: `row_id` (source CSV record number, header excluded but numbering starts at 2), `raw_json` (all original values), `fingerprint` (SHA-256 of eight-field JSON), `is_repeat` (1 for second and later identical source records).

`lines`: `row_id`, `invoice`, `sku`, `description`, `country`, `customer` (NULL if absent), `invoice_date` (ISO timestamp text), `quantity`, `unit_price` (decimal text to preserve source precision), `amount_pence` (signed integer rounded per line), `kind` (sale, cancellation or excluded), `reason` (exclusive primary exclusion reason or NULL).

`valued_lines`: join of eligible `lines` with `raw_rows.is_repeat`. Main SQL analysis always uses this view.

## Exported reports

- `monthly.csv`: gross/cancellation/net pence, distinct sale invoices and deduplicated net pence by observed calendar month. December 2011 is partial.
- `countries.csv`: same primary value metrics and sale-invoice counts grouped by source country label.
- `products.csv`: DENSE_RANK by net value, stock code, example description, positive sale units, cancelled units, net and gross pence. Full ranking, not only the top ten.
- `customer_repeat.csv`: identified customers grouped into one or multiple purchase invoices; customer count, sale-invoice count and gross pence. No inferred identity for missing IDs.
- `exclusion_summary.csv`: primary exclusion reason, rows and signed pence excluded.
- `quality_flags.csv`: overlapping flags and counts, including records that may also be excluded for another reason.
- `cleaned_lines.csv`: all eligible rows, with source row IDs, normalized fields and repeat indicator.
- `exceptions.csv`: excluded rows with numeric fields where parseable and the reason.
- `analysis.json`: complete metrics, checks, six report arrays, input SHA-256 and source metadata.

## Units

CSV/database monetary fields ending in `_pence` are integer GBP minor units. Divide by 100 once for pounds. Presentation files convert to pounds; the original UnitPrice is already in pounds. No currency conversion or inflation adjustment is applied.
