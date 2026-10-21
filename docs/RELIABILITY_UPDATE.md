# Reliability update October 21 2026

The pipeline builds its database, CSV reports and analysis record in an isolated version. It closes the database, checks reconciliations and publishes one latest.json pointer only after success. Readers resolve this pointer once; original root-level results remain static reference files. Invalid input, database/export failures and failed final publication leave the prior version current. The source download manifest now records its actual retrieval time, while analysis labels the original sample date as reference_snapshot_retrieved and records processed_at_utc. The package includes current docs and an exact-byte manifest, excludes older ZIPs and flattens selected aggregate results for portable inspection.

## Validation

The updated local suite passes 22 tests on Python 3.12.14. Regression tests exercise the affected failure scenarios and package freshness, repeated builds and archived-byte hashes. Full historical input was reprocessed with unchanged headline figures. Native Excel/Power BI refresh and optional presentation regeneration were not repeated.

## Release provenance

This release is based on the GitHub commit recorded in release.json. The October 21 regression and full-data checks verify the reliability changes described above. Native desktop verification remains limited to the earlier observations documented in this project.
