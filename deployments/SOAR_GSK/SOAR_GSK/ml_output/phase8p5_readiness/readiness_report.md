# Model Readiness Assessment Report

*Generated on 2026-07-14 14:15*

## 1. Summary

Total drug-species combinations assessed: 42
Ready for modeling: 27
Excluded: 15

### Recommended Types

| Recommended_Type                          |   count |
|:------------------------------------------|--------:|
| Binary (R vs Non-R)                       |      18 |
| Exclude - No Data                         |      11 |
| Multiclass (S/I/R)                        |       8 |
| Exclude - Inadequate Class Representation |       3 |
| Binary (S vs I)                           |       1 |
| Exclude - No Resistance                   |       1 |

## 2. Ready for Modeling

| Drug                    | Species                  |    S |   I |    R | Recommended_Type    | Recommended_Model                           |
|:------------------------|:-------------------------|-----:|----:|-----:|:--------------------|:--------------------------------------------|
| Amoxicillin Clavulanate | Haemophilus influenzae   | 2336 | 201 |   58 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Amoxicillin Clavulanate | Streptococcus pneumoniae |  841 | 363 |  328 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Amoxicillin             | Haemophilus influenzae   |  986 | 172 |  533 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Amoxicillin             | Streptococcus pneumoniae | 1206 | 377 |  350 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Ampicillin              | Haemophilus influenzae   | 2046 |  72 |  462 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Ampicillin              | Streptococcus pneumoniae |  148 | 377 |    0 | Binary (S vs I)     | Logistic Regression, Random Forest          |
| Azithromycin            | Haemophilus influenzae   | 2525 |   0 |   68 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Azithromycin            | Streptococcus pneumoniae | 1247 |   0 | 1082 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Cefixime                | Haemophilus influenzae   | 1274 |   0 |  254 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Cefotaxime              | Haemophilus influenzae   | 1350 |   0 |  178 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Cefpodoxime             | Haemophilus influenzae   | 1260 |   0 |  268 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Cefpodoxime             | Streptococcus pneumoniae |  564 |   0 |  429 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Ceftibuten              | Haemophilus influenzae   | 1286 |   0 |  242 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Ceftriaxone             | Haemophilus influenzae   | 1443 |   0 |  113 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Ceftriaxone             | Streptococcus pneumoniae | 1673 | 611 |   45 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Cefuroxime              | Haemophilus influenzae   | 1886 | 440 |  269 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Cefuroxime              | Streptococcus pneumoniae |  726 |  59 |  719 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Clarithromycin          | Streptococcus pneumoniae |  609 |   0 | 1067 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Doxycycline             | Streptococcus pneumoniae |  532 |   0 |  461 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Erythromycin            | Streptococcus pneumoniae | 1259 |   0 | 1078 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Levofloxacin            | Haemophilus influenzae   | 2271 |   0 |  322 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Moxifloxacin            | Haemophilus influenzae   | 2303 |   0 |  290 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Penicillin              | Streptococcus pneumoniae |  403 | 826 |  298 | Multiclass (S/I/R)  | XGBoost (primary), Random Forest (baseline) |
| Tetracycline            | Haemophilus influenzae   | 1470 |   0 |   58 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Tetracycline            | Streptococcus pneumoniae |  503 |   0 |  490 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Trimethoprim Sulfa      | Haemophilus influenzae   | 1458 |   0 | 1064 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |
| Trimethoprim Sulfa      | Streptococcus pneumoniae | 1393 |   0 |  939 | Binary (R vs Non-R) | XGBoost, Logistic Regression                |

## 3. Excluded

| Drug                               | Species                  |   Total_Isolates | Notes                                                              |
|:-----------------------------------|:-------------------------|-----------------:|:-------------------------------------------------------------------|
| Amoxicillin Clavulanate fixed at 2 | Haemophilus influenzae   |                0 | No isolates with SIR label.                                        |
| Amoxicillin Clavulanate fixed at 2 | Streptococcus pneumoniae |                0 | No isolates with SIR label.                                        |
| Cefaclor                           | Haemophilus influenzae   |                0 | No isolates with SIR label.                                        |
| Cefaclor                           | Streptococcus pneumoniae |                0 | No isolates with SIR label.                                        |
| Cefdinir                           | Haemophilus influenzae   |                0 | No isolates with SIR label.                                        |
| Cefdinir                           | Streptococcus pneumoniae |                0 | No isolates with SIR label.                                        |
| Cefixime                           | Streptococcus pneumoniae |                0 | No isolates with SIR label.                                        |
| Cefotaxime                         | Streptococcus pneumoniae |              993 | S=694, I=277, R=22. Not enough samples for reliable modeling.      |
| Ceftibuten                         | Streptococcus pneumoniae |                0 | No isolates with SIR label.                                        |
| Clarithromycin                     | Haemophilus influenzae   |             2589 | No R isolates and insufficient S/I data for meaningful prediction. |
| Doxycycline                        | Haemophilus influenzae   |                0 | No isolates with SIR label.                                        |
| Erythromycin                       | Haemophilus influenzae   |                0 | No isolates with SIR label.                                        |
| Levofloxacin                       | Streptococcus pneumoniae |             2338 | S=0, I=2312, R=26. Not enough samples for reliable modeling.       |
| Moxifloxacin                       | Streptococcus pneumoniae |             2338 | S=2318, I=0, R=20. Not enough samples for reliable modeling.       |
| Penicillin                         | Haemophilus influenzae   |                0 | No isolates with SIR label.                                        |

## 4. Recommendations

### For Binary Tasks
- Focus on detecting **R (Resistant)** vs **Non-R (S + I)**.
- Use **Temporal validation** (train 2014-2020, test 2021).
- Consider **SMOTE** if imbalance ratio > 5.
- Evaluate **F1 (R)** and **Precision/Recall (R)** as primary metrics.

### For Multiclass Tasks
- Use **XGBoost** with **class weights** or **SMOTE**.
- Evaluate **Macro F1** and **Per-class F1**.
- Use **Temporal + Geographic (GroupKFold by Country)** cross-validation.

## 5. Duplicate Inspection

Total rows in duplicate groups: 2709 (54.9%)
Unique keys with duplicates: 890
Duplicate report saved to: `C:\Users\Adetokunbo\Desktop\villi\ml_output\phase8p5_readiness\duplicate_inspection.csv`

**Action required:** Review the duplicate report. If these represent the same patient/isolate, deduplicate. If they are different patients with the same demographics, they are legitimate and can be retained.
