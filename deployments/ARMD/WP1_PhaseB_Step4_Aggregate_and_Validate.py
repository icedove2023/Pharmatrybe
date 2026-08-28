"""
================================================================
Work Package 1 – Phase B – Step 4 + 4A
Aggregate Microbiology Cohort to One Row per Culture Order
& Validate Information Preservation
================================================================

Outputs:
  - microbiology_cultures_cohort_aggregated.csv
  - WP1_Table11_Aggregation_Validation.csv
================================================================
"""

import duckdb
import pandas as pd
import os

# -------------------------------------------------------------
# Output folder
# -------------------------------------------------------------
OUTPUT_DIR = os.path.join("output", "WP1 – Phase B – Step 4")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# Connect to DuckDB
# -------------------------------------------------------------
con = duckdb.connect("armd.db")

# Load cohort
con.execute("""
CREATE OR REPLACE VIEW cohort AS
SELECT *
FROM read_csv_auto('Data/microbiology_cultures_cohort.csv')
""")

print("=" * 70)
print("WP1 - PHASE B - STEP 4")
print("AGGREGATING TO ONE ROW PER CULTURE ORDER")
print("=" * 70)

# -------------------------------------------------------------
# Aggregation query
# -------------------------------------------------------------
aggregated = con.execute("""
SELECT
    order_proc_id_coded,
    MIN(anon_id) AS anon_id,
    MIN(pat_enc_csn_id_coded) AS pat_enc_csn_id_coded,
    MIN(order_time_jittered_utc) AS order_time_jittered_utc,
    MIN(ordering_mode) AS ordering_mode,
    MIN(culture_description) AS culture_description,
    MIN(was_positive) AS was_positive,
    COUNT(*) AS total_result_rows,
    COUNT(DISTINCT organism) AS n_organisms,
    COUNT(DISTINCT antibiotic) AS n_antibiotics,
    COUNT(DISTINCT susceptibility) AS n_susceptibility,
    STRING_AGG(DISTINCT organism, '; ' ORDER BY organism) AS organisms,
    STRING_AGG(DISTINCT antibiotic, '; ' ORDER BY antibiotic) AS antibiotics,
    STRING_AGG(DISTINCT susceptibility, '; ' ORDER BY susceptibility) AS susceptibilities
FROM cohort
GROUP BY order_proc_id_coded
ORDER BY order_proc_id_coded
""").df()

# -------------------------------------------------------------
# Save aggregated dataset
# -------------------------------------------------------------
agg_file = os.path.join(OUTPUT_DIR, "microbiology_cultures_cohort_aggregated.csv")
aggregated.to_csv(agg_file, index=False)

print(f"\nAggregated dataset saved: {agg_file}")
print(f"Rows: {len(aggregated)}")
print(f"Columns: {aggregated.shape[1]}")

# -------------------------------------------------------------
# Step 4A: Validate Information Preservation
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 4A - VALIDATING INFORMATION PRESERVATION")
print("=" * 70)

# For each culture, compare aggregated counts with original distinct values
validation_query = """
WITH original AS (
    SELECT
        order_proc_id_coded,
        COUNT(DISTINCT organism) AS orig_org_count,
        COUNT(DISTINCT antibiotic) AS orig_abx_count,
        COUNT(DISTINCT susceptibility) AS orig_susc_count
    FROM cohort
    GROUP BY order_proc_id_coded
)
SELECT
    agg.order_proc_id_coded,
    agg.n_organisms,
    orig.orig_org_count,
    agg.n_antibiotics,
    orig.orig_abx_count,
    agg.n_susceptibility,
    orig.orig_susc_count,
    CASE
        WHEN agg.n_organisms = orig.orig_org_count
         AND agg.n_antibiotics = orig.orig_abx_count
         AND agg.n_susceptibility = orig.orig_susc_count
        THEN 'PASS'
        ELSE 'FAIL'
    END AS validation_result
FROM aggregated AS agg
JOIN original AS orig
ON agg.order_proc_id_coded = orig.order_proc_id_coded
"""

validation_df = con.execute(validation_query).df()

# Summary of validation results
pass_count = (validation_df['validation_result'] == 'PASS').sum()
fail_count = (validation_df['validation_result'] == 'FAIL').sum()

print(f"\nCultures with PASS: {pass_count}")
print(f"Cultures with FAIL: {fail_count}")

if fail_count == 0:
    print("\n✅ All culture orders passed validation. No information lost.")
else:
    print(f"\n⚠️ {fail_count} cultures have mismatches. Review the validation report.")

# Save validation report
val_file = os.path.join(OUTPUT_DIR, "WP1_Table11_Aggregation_Validation.csv")
validation_df.to_csv(val_file, index=False)
print(f"\nValidation report saved: {val_file}")

# -------------------------------------------------------------
# Additional summary
# -------------------------------------------------------------
summary = {
    'Metric': [
        'Total culture orders',
        'Positive cultures',
        'Negative cultures',
        'Average organisms per culture',
        'Average antibiotics per culture',
        'Cultures with any organism'
    ],
    'Value': [
        len(aggregated),
        (aggregated['was_positive'] == 1).sum(),
        (aggregated['was_positive'] == 0).sum(),
        round(aggregated['n_organisms'].mean(), 3),
        round(aggregated['n_antibiotics'].mean(), 3),
        (aggregated['n_organisms'] > 0).sum()
    ]
}
summary_df = pd.DataFrame(summary)
summary_file = os.path.join(OUTPUT_DIR, "WP1_Table10_Aggregated_Summary.csv")
summary_df.to_csv(summary_file, index=False)
print(f"\nSummary statistics saved: {summary_file}")

# -------------------------------------------------------------
# Final
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 4 & 4A COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"All outputs saved to: '{OUTPUT_DIR}/'")
print("  - microbiology_cultures_cohort_aggregated.csv")
print("  - WP1_Table10_Aggregated_Summary.csv")
print("  - WP1_Table11_Aggregation_Validation.csv")

con.close()