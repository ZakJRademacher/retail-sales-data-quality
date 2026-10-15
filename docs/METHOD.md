# Method and decisions

## Business question

What sales trends can be reported from this export, and which data-quality decisions materially change the numbers? The intended reader is a small retail business owner or operations manager who needs a repeatable transaction-cleanup and reporting workflow.

## Source grain and provenance

Each source record is an invoice **line**, not an order or a customer. Repeated invoice numbers are expected across products. Invoice/stock code is not treated as a unique line key. The untouched source CSV remains local in `data/raw/`; its SHA-256 is recorded. Every record is assigned its physical CSV record position (header is row 1) and stored as JSON in `raw_rows`. A fingerprint detects exact repeats across all eight original values.

## Cleaning sequence

1. Require the eight source columns, in order. Reject malformed CSV shape with an explicit error rather than shifting data silently.
2. Preserve source text in `raw_rows`; trim displayed text and uppercase invoice and stock-code identifiers in `lines`. Preserve leading zeroes. Missing customer IDs become SQL NULL; no invented customer IDs or category mappings.
3. Parse month/day/year timestamps explicitly. Parse quantity as a finite integer and price with Decimal. Multiply quantity by price, then round the line amount half up to pence. Do not round unit price first.
4. Exclude invalid numeric/date/key records, nonpositive prices, zero quantities, and inconsistent invoice/quantity signs from valued reporting. A single primary reason is retained per excluded row. Earlier parsing/key problems take precedence. The source data still remains in the database.
5. A positive quantity on a non-C invoice is a sale. A negative quantity on a C invoice is a cancellation. Cancellations are retained as negative values, rather than being deleted to inflate revenue. C is the source's cancellation indicator; it does not establish that a physical return occurred or link a cancellation to a specific prior purchase.
6. Keep missing descriptions and customer IDs when the monetary fields are otherwise valid. Report these as flags. Missing-ID records still contribute to aggregate sales, but cannot support identified-customer repeat analysis.
7. Preserve exact repeated rows in primary totals. Publish a comparison excluding the second and later exact occurrences. The source does not contain sufficient evidence to decide whether all repeated lines are accidental duplicates.
8. Run all reporting SQL against `valued_lines`, the joined view of eligible normalized rows and repeat flags. Use stock codes as product group keys; the lexicographically maximum description is an example label, not a product master.

## Metric definitions

| Metric | Definition |
|---|---|
| Gross positive sales | Sum of positive-price sale-line amounts |
| Cancellation value | Absolute total of negative line amounts on eligible C invoices; unit prices are positive |
| Net transaction value | Gross positive sales minus cancellation value |
| Sale invoices | Count of distinct invoice IDs among eligible sale rows |
| Average sale invoice | Gross positive sales / sale invoices; excludes cancellations from numerator and denominator |
| Cancellation value share | Cancellation value / gross positive sales; not a matched or cohort return rate |
| Deduplicated sensitivity | Same eligible rules, excluding repeated occurrences of identical eight-column source rows |
| Repeat customer | Identified customer with more than one distinct eligible purchase invoice over the observed period |

## Reconciliation

All rows belong to exactly one of sale, cancellation, or excluded. Raw parseable signed value equals valued net value plus excluded signed value. Monthly, country and product sums each reconcile exactly in integer pence to the headline net value. Quality flags can overlap and must not be added as if they partition rows.

## Limitations and next actions

- December 2011 ends on December 9. Mark it partial; do not infer a collapse in sales from its lower total.
- Repeats may be legitimate. Ask the data owner for a true line identifier before using deduplication in production.
- Missing customer IDs mean the repeat-customer result does not describe all buyers. Blank customer IDs are not assumed to mean guest checkout.
- Special stock codes such as postage/manual charges remain in transaction values. Product rankings can include non-merchandise codes; investigate before using them for assortment decisions.
- Large positive and negative lines are retained when valid. Wholesale orders and offsetting cancellations can dominate some periods. Review these with source evidence instead of arbitrary outlier deletion.
- There are no reliable COGS, inventory balances, payment settlement, or marketing-spend fields. No profit, stockout, fraud, causal marketing or savings claims are made.
- The dataset is historical and from one retailer. Findings demonstrate a method, not current UK retail benchmarks or Albertsons operations.
