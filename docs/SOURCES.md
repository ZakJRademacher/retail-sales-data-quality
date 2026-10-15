# Sources and provenance

## Downloaded source

- Kaggle: https://www.kaggle.com/datasets/carrie1/ecommerce-data
- Dataset: E-Commerce Data, uploader Carrie, version 1 (page inspected October 15, 2026).
- Download: https://www.kaggle.com/api/v1/datasets/download/carrie1/ecommerce-data
- File: `data.csv`, Latin-1 encoding, eight columns, 541,909 records.
- Retrieval date: October 15, 2026.
- SHA-256 of extracted CSV: `d07aec9960083af2339975a3f9d3b26313b342dcd9f86cce0b919b1cde639a44`.
- The mirror's current license label is **Unknown**; it identifies the original UCI dataset.

## Original dataset and attribution

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33.

Original dataset page: https://archive.ics.uci.edu/dataset/352/online+retail

UCI states Creative Commons Attribution 4.0 International (CC BY 4.0), permitting sharing and adaptation with attribution. License text: https://creativecommons.org/licenses/by/4.0/

This project attributes the underlying data to UCI/Daqing Chen. It does not claim Kaggle independently supplied a permissive license. Data transformations: text normalization, explicit type/date parsing, line-level decimal rounding, eligibility classification, repeat flags, grouped SQL reports, and visual summaries. Original source data is not modified in place. Code is licensed separately under MIT.

## Reproduction and scope

Use the fingerprint to identify this exact input. A later Kaggle replacement may change the results; re-run tests and compare the row count and checksum. Source documentation describes the underlying retailer; all numeric findings here are computed by the included code, not copied from another analyst's notebook. Documentation discrepancies (such as UCI metadata stating no missing values) are resolved by reporting observed CSV null counts. The project does not infer identities for anonymous customer keys.
