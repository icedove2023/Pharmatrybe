"""
Work Package 1 - Phase B - Step 3A
Create the Official Clean Positive Culture Cohort
*** FOR THE AGGREGATED COHORT (one row per culture order) ***

INPUTS:
  - Aggregated cohort (one row per culture order)
  - Exclusion list of exclusively-null positive cultures

OUTPUTS:
  - Clean_Positive_Culture_Cohort.csv
  - Clean_Positive_Culture_Cohort.parquet
  - Excluded_CultureOrders.csv
  - Cohort_Flow_Summary.csv
  - Cleaning_Log.csv
  - Data_Integrity_Checks.txt
  - Dataset_Passport.csv
  - Associated .audit.txt / .audit.json files
"""

import duckdb
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.io import save_and_audit

# Paths
COHORT_PATH = "output/WP1 – Phase B – Step 4/microbiology_cultures_cohort_aggregated.csv"
EXCLUSIONS_PATH = "output/WP1 – Phase A – Step 2B/ExclusivelyNull_CultureOrders.csv"
OUTPUT_DIR = os.path.join("output", "WP1 – Phase B – Step 3A")
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")

print("=" * 70)
print("WP1 - PHASE B - STEP 3A: CREATE CLEAN POSITIVE CULTURE COHORT")
print("=" * 70)

# =============================================================================
# 1. LOAD AGGREGATED COHORT (one row per culture order)
# =============================================================================
con.execute(f"""
CREATE OR REPLACE TEMP TABLE cohort AS
SELECT * FROM read_csv_auto('{COHORT_PATH}')
""")

total_rows = con.execute("SELECT COUNT(*) FROM cohort").fetchone()[0]
total_cultures = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort").fetchone()[0]

# Assertion: must be one row per culture (aggregated)
if total_rows != total_cultures:
    raise RuntimeError(
        f"Aggregated cohort has {total_rows} rows but {total_cultures} distinct culture orders. "
        "Expected exactly one row per culture order. This is likely the long AST table, not the aggregated version."
    )

print(f"\n1. Aggregated cohort: {total_rows:,} rows, {total_cultures:,} culture orders")

# =============================================================================
# 2. LOAD EXCLUSIONS (empty positives)
# =============================================================================
excl_exists = os.path.exists(EXCLUSIONS_PATH)
if not excl_exists:
    print(f"⚠️ Exclusions file not found: {EXCLUSIONS_PATH}\n   Assuming no exclusions.")
    con.execute("CREATE OR REPLACE TEMP TABLE exclusions AS SELECT NULL AS order_proc_id_coded WHERE 1=0")
    excl_count = 0
else:
    con.execute(f"""
    CREATE OR REPLACE TEMP TABLE exclusions AS
    SELECT order_proc_id_coded FROM read_csv_auto('{EXCLUSIONS_PATH}')
    """)
    excl_count = con.execute("SELECT COUNT(*) FROM exclusions").fetchone()[0]
    print(f"2. Loaded {excl_count:,} exclusion IDs")

# =============================================================================
# 3. APPLY EXCLUSIONS (remove the 1,510 empty positives)
# =============================================================================
con.execute("""
CREATE OR REPLACE TEMP TABLE cohort_no_excl AS
SELECT c.*
FROM cohort c
LEFT JOIN exclusions e ON c.order_proc_id_coded = e.order_proc_id_coded
WHERE e.order_proc_id_coded IS NULL
""")
rows_after_excl = con.execute("SELECT COUNT(*) FROM cohort_no_excl").fetchone()[0]
cultures_after_excl = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort_no_excl").fetchone()[0]
excl_rows = total_rows - rows_after_excl
excl_cultures = total_cultures - cultures_after_excl
print(f"3. After excluding empty positives: {rows_after_excl:,} rows, {cultures_after_excl:,} cultures (removed {excl_rows:,} rows, {excl_cultures:,} cultures)")

# =============================================================================
# 4. FILTER TO POSITIVE CULTURES ONLY
# =============================================================================
con.execute("""
CREATE OR REPLACE TEMP TABLE positive_cohort AS
SELECT *
FROM cohort_no_excl
WHERE was_positive = 1
""")
pos_rows = con.execute("SELECT COUNT(*) FROM positive_cohort").fetchone()[0]
pos_cultures = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM positive_cohort").fetchone()[0]
neg_rows = rows_after_excl - pos_rows
neg_cultures = cultures_after_excl - pos_cultures
print(f"4. Positive cultures: {pos_rows:,} rows, {pos_cultures:,} cultures (removed {neg_rows:,} rows, {neg_cultures:,} negative)")

# =============================================================================
# 5. INTEGRITY CHECK: Ensure all positive cultures have at least one organism
#    In aggregated data, this means n_organisms > 0 and organisms string not empty.
#    Also ensure the string contains at least one non‑delimiter character.
# =============================================================================
bad_count = con.execute("""
SELECT COUNT(*) FROM positive_cohort
WHERE n_organisms <= 0
   OR organisms IS NULL
   OR TRIM(organisms) = ''
   OR LOWER(TRIM(organisms)) IN ('null', '')
   OR LENGTH(REGEXP_REPLACE(TRIM(organisms), '[; ]', '', 'g')) = 0
""").fetchone()[0]

if bad_count == 0:
    print("5. Integrity check: All positive cultures have at least one organism. Good.")
    con.execute("CREATE OR REPLACE TEMP TABLE clean_cohort AS SELECT * FROM positive_cohort")
    removed_bad_rows = 0
    removed_bad_cultures = 0
else:
    print(f"5. WARNING: Found {bad_count:,} positive cultures with no organism (should be 0). Removing them.")
    con.execute("""
    CREATE OR REPLACE TEMP TABLE clean_cohort AS
    SELECT *
    FROM positive_cohort
    WHERE n_organisms > 0
      AND organisms IS NOT NULL
      AND TRIM(organisms) != ''
      AND LOWER(TRIM(organisms)) NOT IN ('null', '')
      AND LENGTH(REGEXP_REPLACE(TRIM(organisms), '[; ]', '', 'g')) > 0
    """)
    removed_bad_rows = bad_count
    removed_bad_cultures = bad_count   # one row per culture, so same

# Final counts
clean_rows = con.execute("SELECT COUNT(*) FROM clean_cohort").fetchone()[0]
clean_cultures = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM clean_cohort").fetchone()[0]
print(f"   Final: {clean_rows:,} rows, {clean_cultures:,} cultures (removed {removed_bad_rows:,} rows)")

# =============================================================================
# 6. BUILD EXCLUDED CULTURES LIST (with multiple reasons)
# =============================================================================
con.execute("""
CREATE OR REPLACE TEMP TABLE excluded_log AS
SELECT
    order_proc_id_coded,
    'Exclusively-null positive' AS reason
FROM exclusions
WHERE order_proc_id_coded IS NOT NULL
UNION ALL
SELECT
    order_proc_id_coded,
    'Negative culture' AS reason
FROM cohort_no_excl
WHERE was_positive = 0
UNION ALL
SELECT
    order_proc_id_coded,
    'No organism in aggregated data' AS reason
FROM positive_cohort
WHERE n_organisms <= 0
   OR organisms IS NULL
   OR TRIM(organisms) = ''
   OR LOWER(TRIM(organisms)) IN ('null', '')
   OR LENGTH(REGEXP_REPLACE(TRIM(organisms), '[; ]', '', 'g')) = 0
""")

excluded_df = con.execute("""
SELECT
    order_proc_id_coded,
    STRING_AGG(DISTINCT reason, '; ') AS reasons
FROM excluded_log
GROUP BY order_proc_id_coded
ORDER BY order_proc_id_coded
""").df()

excluded_file = os.path.join(OUTPUT_DIR, "Excluded_CultureOrders.csv")
excluded_df.to_csv(excluded_file, index=False)
save_and_audit(excluded_df, excluded_file, id_column="order_proc_id_coded")

# =============================================================================
# 7. CLEANING LOG
# =============================================================================
cleaning_log = pd.DataFrame({
    'Step': [
        '1. Aggregated cohort',
        '2. Excluded empty positives',
        '3. Negative cultures removed',
        '4. Removed cultures with no organism',
        '5. Final clean cohort'
    ],
    'Cultures_Remaining': [
        total_cultures,
        cultures_after_excl,
        pos_cultures,
        clean_cultures,
        clean_cultures
    ],
    'Cultures_Removed': [
        0,
        excl_cultures,
        neg_cultures,
        removed_bad_cultures,
        0
    ],
    'Percent_Removed (of original)': [
        0.0,
        round(excl_cultures / total_cultures * 100, 2),
        round(neg_cultures / total_cultures * 100, 2),
        round(removed_bad_cultures / total_cultures * 100, 2),
        0.0
    ],
    'Rows_Remaining': [
        total_rows,
        rows_after_excl,
        pos_rows,
        clean_rows,
        clean_rows
    ],
    'Rows_Removed': [
        0,
        excl_rows,
        neg_rows,
        removed_bad_rows,
        0
    ]
})
log_file = os.path.join(OUTPUT_DIR, "Cleaning_Log.csv")
cleaning_log.to_csv(log_file, index=False)
save_and_audit(cleaning_log, log_file)

# =============================================================================
# 8. COHORT FLOW SUMMARY (CONSORT-style)
# =============================================================================
flow_data = [
    {"Step": "Aggregated microbiology cohort", "Cultures": total_cultures, "Rows": total_rows},
    {"Step": "Excluded exclusively-null positive cultures", "Cultures": excl_cultures, "Rows": excl_rows},
    {"Step": "Removed negative cultures", "Cultures": neg_cultures, "Rows": neg_rows},
    {"Step": "Removed cultures with no organism", "Cultures": removed_bad_cultures, "Rows": removed_bad_rows},
    {"Step": "Final clean positive culture cohort", "Cultures": clean_cultures, "Rows": clean_rows}
]
flow_df = pd.DataFrame(flow_data)
flow_file = os.path.join(OUTPUT_DIR, "Cohort_Flow_Summary.csv")
flow_df.to_csv(flow_file, index=False)
save_and_audit(flow_df, flow_file)

# =============================================================================
# 9. SAVE CLEAN COHORT (CSV + Parquet) with proper audit
# =============================================================================
csv_path = os.path.join(OUTPUT_DIR, "Clean_Positive_Culture_Cohort.csv")
con.execute(f"""
COPY (
    SELECT * FROM clean_cohort ORDER BY order_proc_id_coded
) TO '{csv_path}' WITH (HEADER, DELIMITER ',')
""")
print(f"\n✅ CSV saved: {csv_path}")

parquet_path = os.path.join(OUTPUT_DIR, "Clean_Positive_Culture_Cohort.parquet")
con.execute(f"""
COPY (
    SELECT * FROM clean_cohort ORDER BY order_proc_id_coded
) TO '{parquet_path}' (FORMAT PARQUET)
""")
print(f"✅ Parquet saved: {parquet_path}")

# Now load the saved CSV as a DataFrame for auditing
clean_df = con.execute(f"SELECT * FROM read_csv_auto('{csv_path}')").df()
save_and_audit(
    clean_df,
    csv_path,  # file path for report naming (audit will use the DataFrame)
    id_column="order_proc_id_coded",
    expected_values={
        "rows": clean_rows,
        "unique_ids": clean_cultures,
        "no_duplicates": True,
        "min_rows": 1
    },
    placeholder_values=["Null", "NULL", "null", "NA"],
    domain_rules={
        "was_positive": {"values": [1]},
        "order_proc_id_coded": {"unique": True}
    }
)

# =============================================================================
# 10. DATA INTEGRITY CHECKS (with explicit counts)
# =============================================================================
integrity_results = []

# 1. All retained rows are positive
pos_violations = con.execute("SELECT COUNT(*) FROM clean_cohort WHERE was_positive != 1").fetchone()[0]
integrity_results.append(("All retained rows are positive", pos_violations == 0, pos_violations))

# 2. No excluded culture IDs remain
excl_violations = con.execute("""
SELECT COUNT(*) FROM clean_cohort
WHERE order_proc_id_coded IN (SELECT order_proc_id_coded FROM exclusions)
""").fetchone()[0]
integrity_results.append(("No excluded culture IDs remain", excl_violations == 0, excl_violations))

# 3. All positive cultures have at least one organism (validated earlier, but re-check)
org_violations = con.execute("""
SELECT COUNT(*) FROM clean_cohort
WHERE n_organisms <= 0
   OR organisms IS NULL
   OR TRIM(organisms) = ''
   OR LOWER(TRIM(organisms)) IN ('null', '')
   OR LENGTH(REGEXP_REPLACE(TRIM(organisms), '[; ]', '', 'g')) = 0
""").fetchone()[0]
integrity_results.append(("All cultures have at least one organism", org_violations == 0, org_violations))

# 4. No missing order IDs
missing_id = con.execute("SELECT COUNT(*) FROM clean_cohort WHERE order_proc_id_coded IS NULL").fetchone()[0]
integrity_results.append(("No missing order IDs", missing_id == 0, missing_id))

# 5. No duplicate culture IDs
dup_ids = con.execute("""
SELECT COUNT(*) - COUNT(DISTINCT order_proc_id_coded) FROM clean_cohort
""").fetchone()[0]
integrity_results.append(("No duplicate culture IDs", dup_ids == 0, dup_ids))

# Write integrity report
integrity_file = os.path.join(OUTPUT_DIR, "Data_Integrity_Checks.txt")
with open(integrity_file, 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("DATA INTEGRITY CHECKS\n")
    f.write("=" * 70 + "\n\n")
    for desc, passed, count in integrity_results:
        status = "PASS" if passed else "FAIL"
        f.write(f"✓ {desc}: {status} ({count} violations)\n")
    if all(passed for _, passed, _ in integrity_results):
        f.write("\n✅ All checks passed. Cohort is internally consistent.\n")
    else:
        f.write("\n❌ Some checks failed. Please investigate.\n")

print("\nData Integrity Checks:")
for desc, passed, count in integrity_results:
    print(f"  ✓ {desc}: {'PASS' if passed else 'FAIL'} ({count} violations)")

# =============================================================================
# 11. DATASET PASSPORT (enhanced)
# =============================================================================
passport = con.execute("""
SELECT
    COUNT(DISTINCT order_proc_id_coded) AS culture_orders,
    COUNT(*) AS rows,
    COUNT(DISTINCT anon_id) AS unique_patients,
    COUNT(DISTINCT pat_enc_csn_id_coded) AS unique_encounters,
    ROUND(AVG(n_organisms), 2) AS avg_organisms_per_culture,
    ROUND(MEDIAN(n_organisms), 2) AS median_organisms_per_culture,
    ROUND(AVG(n_antibiotics), 2) AS avg_antibiotics_per_culture,
    ROUND(MEDIAN(n_antibiotics), 2) AS median_antibiotics_per_culture,
    COUNT(DISTINCT ordering_mode) AS unique_ordering_modes,
    COUNT(DISTINCT culture_description) AS unique_specimen_types,
    COUNT(DISTINCT organisms) AS unique_organism_combinations,
    MIN(order_time_jittered_utc) AS earliest_culture_date,
    MAX(order_time_jittered_utc) AS latest_culture_date
FROM clean_cohort
""").df()

passport_file = os.path.join(OUTPUT_DIR, "Dataset_Passport.csv")
passport.to_csv(passport_file, index=False)
print("\n📋 Dataset Passport:")
print(passport.to_string(index=False))

# =============================================================================
# 12. FINAL CONSISTENCY CHECK
# =============================================================================
expected_cultures = total_cultures - excl_cultures - neg_cultures - removed_bad_cultures
if clean_cultures != expected_cultures:
    raise RuntimeError(
        f"Final cohort mismatch: expected {expected_cultures}, got {clean_cultures}"
    )
print(f"\n✅ Accounting verified: {clean_cultures:,} cultures in final cohort.")

# =============================================================================
# 13. COMPLETION
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3A COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"✅ Clean cohort: {clean_rows:,} rows, {clean_cultures:,} culture orders")
print(f"📁 All outputs saved to: {OUTPUT_DIR}")
print("  - Clean_Positive_Culture_Cohort.csv")
print("  - Clean_Positive_Culture_Cohort.parquet")
print("  - Excluded_CultureOrders.csv")
print("  - Cohort_Flow_Summary.csv")
print("  - Cleaning_Log.csv")
print("  - Data_Integrity_Checks.txt")
print("  - Dataset_Passport.csv")
print("  - Associated audit files (.audit.txt, .audit.json)")

con.close()