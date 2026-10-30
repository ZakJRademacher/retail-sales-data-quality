# Retail Data Quality Review — Tableau preview

**Question:** Which cleaning choices change the reported answer?

![Native Tableau report](../deliverables/tableau-retail-preview.png)

Preferred net value is GBP 9,769,872.05. Removing unidentified valued lines changes net by minus GBP 1,469,806.24; removing exact repeats changes it by minus GBP 21,740.98. These separate policy sensitivities are not additive. December 2011 is partial.

This is a fixed historical decision brief built from validated Python/SQL aggregates. KPI and interpretation text refer to that fixed population; arbitrary worksheet filtering does not recalculate the written findings. The native workbook was opened and checked in Tableau Desktop on October 29, 2026. [Download the packaged workbook](../deliverables/Retail%20Data%20Quality%20Review.twbx), including its reporting data, or use the [editable source and reproduction guide](../tableau/README.md). There is no Tableau Public deployment.

The existing public analysis, source instructions and earlier Excel/Power BI deliverables remain available from the repository README. Existing source attribution and data licenses continue to apply.
