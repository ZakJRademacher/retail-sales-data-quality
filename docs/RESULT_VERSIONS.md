# Result versions and failed refresh recovery

The pipeline builds each complete result in a fresh staging directory. It closes the SQLite database and finishes CSV exports and reconciliation checks before publishing `results/latest.json` with a single file replacement. An invalid source, database failure, export failure or failed pointer replacement leaves the previous complete version current.

## Find the current output

From the project root:

```sh
python src/publication.py
```

The command prints the current snapshot directory. For a custom output root, use `python src/publication.py --output /path/to/results`. Read the database, analysis.json and CSVs from that one printed directory. Do not mix files from different versions.

Successful runs create `results/snapshots/<run ID>/`. Historical versions remain available. Repeated runs create new complete versions without accumulating records. The flat files checked into `results/` remain a static reference sample. When a latest.json pointer exists, it is authoritative; root-level reference files are not the new run. If no pointer exists, the helper returns the reference folder for backward-compatible inspection.

## Recover from an error

Fix the reported source or storage issue and rerun. Failed runs may remain in `.staging_*` or as an unreferenced snapshot if final publication failed. They are never selected by latest.json. Keep the previous successful version until the new result has been checked. Remove abandoned versions deliberately when no readers need them.

A `.refresh.lock` file prevents overlapping pipeline runs. It is removed on ordinary success or an exception. After a process crash, inspect the lock and confirm no refresh is running before removing it. Do not run concurrent exports or edit published snapshot files.

The Python verification and presentation builders, Node workbook builder and packaging command resolve the pointer once per operation. This prevents a single operation from mixing versions. An already-open external reader must continue using its selected snapshot or deliberately reload the pointer.

## Portable bundles

`python tools/package_project.py` builds a ZIP in the project root, excludes old ZIPs and private persistent annotations, and verifies every archived file against its exact-byte manifest. Current aggregate result files are flattened into `results/` inside the bundle as a static reference; bulk row-level data and databases are omitted. The bundle includes no pointer to an omitted snapshot. A fresh pipeline run establishes its own versioned output.

Use `python tools/package_project.py --results /path/to/results` to package a separately generated result. Only package data that belongs in the intended demonstration.
