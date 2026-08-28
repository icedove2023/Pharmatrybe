# Clinical Simulation Report – Phase 12

*Generated on 2026-07-18 13:54*

## 1. Executive Summary

This report presents the results of the clinical simulation, comprising two modes:
- **Replay Validation**: using the real 2021 surveillance cohort with known outcomes.
- **Synthetic Simulation**: using generated patient profiles without ground truth.

All predictions are based on the deployed models from Phase 10. No retraining was performed.

## 2. Replay Validation Summary

- Number of patients: 927
- Number of predictions: 4932
- Top 5 recommended drugs (by average CRS):
  - Doxycycline: 0.558
  - Trimethoprim Sulfa: 0.484
  - Tetracycline: 0.259
  - Levofloxacin: 0.210
  - Cefotaxime: 0.196

## 3. Synthetic Simulation Summary

- Number of synthetic patients: 100
- Number of predictions: 1000
- Top 5 recommended drugs (by average CRS):
  - Trimethoprim Sulfa: 0.431
  - Doxycycline: 0.356
  - Tetracycline: 0.179
  - Levofloxacin: 0.134
  - Cefpodoxime: 0.132

## 4. Figures

### Replay Mode Figures

![avg_crs_replay.png](..\figures\avg_crs_replay.png)

![crs_distribution_replay.png](..\figures\crs_distribution_replay.png)

![safety_flags_replay.png](..\figures\safety_flags_replay.png)

### Synthetic Mode Figures

![avg_crs_synthetic.png](..\figures\avg_crs_synthetic.png)

![crs_distribution_synthetic.png](..\figures\crs_distribution_synthetic.png)

![safety_flags_synthetic.png](..\figures\safety_flags_synthetic.png)

## 5. JSON Export

Machine-readable JSON files are available in the `json/` directory.

## 6. Conclusion

The CDSS demonstrates consistent behaviour across real and synthetic cohorts.
Recommendations are accompanied by confidence and safety flags, aiding clinical interpretation.
Further prospective validation is recommended.

---
*Report generated on 2026-07-18 13:54.*
