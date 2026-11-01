# Maintaining the Retail Data Quality presentation

Keep the report's labels, units, source attribution, and metric definitions visible when changing its appearance. Palette values live in `design-tokens.json`. Excel worksheets use a light background; the presentation builders retain their existing formula and data definitions. Segoe UI, Arial, and PDF Helvetica are system/runtime fonts rather than bundled font files.

## Update the report

After rebuilding native source, run `python tools/apply_visual_theme.py` from the project root. Open the report in Tableau Desktop, inspect every page, and check the interactions described in its guide. Restore defaults, save, rebuild the portable package where applicable, and reopen the saved download. Tableau's fixed written findings must remain consistent with the stated population.

Control example: **GBP 9,769,872.05 preferred net value and GBP 21,740.98 exact-repeat sensitivity.** Check the source totals and field mappings as well as the rounded labels. Formatting must not change calculations, missing-value rules, keys, or the population behind a measure.

## Regenerate covers

Cover source lives in `presentation/`. Capture the current report into the image named in `presentation/cover.json`, then run:

```sh
python presentation/build_cover.py --motion --workdir <scratch folder outside the project>
```

The cover builder needs the development Playwright package and Edge. It writes cover images and a short animation into `deliverables/`. That animation is separate from the report and PDF behavior.

## Check a small change

Try one accent change in a disposable copy, rebuild, and confirm the control example. Check long labels, explicit warnings, missing and zero values, keyboard controls where supported, and thumbnail crops. Restore the palette before portfolio use. Keep earlier screenshots and verification results as dated records; save new evidence separately.
