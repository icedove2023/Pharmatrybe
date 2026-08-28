# Dataset Harmonization and Integration Report

*Generated on 2026-07-14 13:14*

## 1. Executive Summary

Two datasets were successfully harmonized and merged:

- **Dataset A (SOAR):** 2521 rows, 84 columns
- **Dataset B (GSK):** 2413 rows, 76 columns
- **Merged Dataset:** 4934 rows, 63 columns

## 2. Dataset Comparison

| Metric     | Dataset A (SOAR)                                 | Dataset B (GSK)                                  |
|:-----------|:-------------------------------------------------|:-------------------------------------------------|
| Rows       | 2521                                             | 2413                                             |
| Columns    | 79                                               | 23                                               |
| Countries  | 10                                               | 0                                                |
| Year Range | 2018 - 2021                                      | 2014 - 2016                                      |
| Species    | Haemophilus influenzae, Streptococcus pneumoniae | Streptococcus pneumoniae, Haemophilus influenzae |

## 3. Column Compatibility

- Common columns: 18
- Only in Dataset A: 61
- Only in Dataset B: 5

## 4. Duplicate Detection

- Dataset A unique keys: 1795
- Dataset B unique keys: 6
- Overlapping keys: 0

## 5. Data Provenance

| Dataset                   | Source   | Years     |   Countries |   Rows |   H. influenzae |   S. pneumoniae |
|:--------------------------|:---------|:----------|------------:|-------:|----------------:|----------------:|
| SOAR (Dataset A)          | Vivli    | 2018-2021 |          10 |   2521 |            1528 |             993 |
| GSK Published (Dataset B) | GSK      | 2014-2016 |           0 |   2413 |            1067 |            1346 |

## 6. Species Distribution

| Species | Dataset A | Dataset B |
|---------|-----------|-----------|
| Haemophilus influenzae | 1528 | 1067 |
| Streptococcus pneumoniae | 993 | 1346 |

## 7. Next Steps

1. **Run EDA on merged dataset** – Generate updated exploratory analysis.
2. **Apply EUCAST breakpoints** – Recalculate S/I/R labels using uniform breakpoint version.
3. **Retrain prototypes** – Train new models on merged data.
4. **Compare performance** – Old vs new model comparison.
5. **Prepare for publication** – Include harmonization process in methods.

## 8. Files Generated

- Merged dataset: `soar_merged.csv`
- This report: `C:\Users\Adetokunbo\Desktop\villi\ml_output\phase6_harmonization\harmonization_report.md`
- Figures: `C:\Users\Adetokunbo\Desktop\villi\ml_output\phase6_harmonization\figures/`
