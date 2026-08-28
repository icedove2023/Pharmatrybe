"""
Work Package 1 - Phase B - Step 3B
Create Analysis-Ready Positive Culture Dataset

INPUT:
  - Clean_Positive_Culture_Cohort.parquet (one row per culture order, 118,767 rows)

OUTPUTS (saved to output/WP1 – Phase B – Step 3B/):
  - Analysis_Ready_Positive_Cultures.csv (audited)
  - Analysis_Ready_Positive_Cultures.parquet
  - Cleaning_Log.csv (audited)
  - Dataset_Passport.csv (audited)
  - Data_Integrity_Checks.txt
  - Associated audit files (.audit.txt, .audit.json) for each CSV
"""

import duckdb
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.io import save_and_audit

# Paths
INPUT_PATH = "output/WP1 – Phase B – Step 3A/Clean_Positive_Culture_Cohort.parquet"
OUTPUT_DIR = os.path.join("output", "WP1 – Phase B – Step 3B")
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")

print("=" * 70)
print("WP1 - PHASE B - STEP 3B: CREATE ANALYSIS-READY POSITIVE CULTURE COHORT")
print("=" * 70)

# =============================================================================
# 1. LOAD CLEAN COHORT
# =============================================================================
con.execute(f"""
CREATE OR REPLACE TEMP TABLE clean_cohort AS
SELECT * FROM read_parquet('{INPUT_PATH}')
""")

original_rows = con.execute("SELECT COUNT(*) FROM clean_cohort").fetchone()[0]
original_cultures = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM clean_cohort").fetchone()[0]
print(f"\n1. Loaded clean cohort: {original_rows:,} rows, {original_cultures:,} culture orders")

# Integrity checks
place_check = con.execute("""
SELECT COUNT(*) FROM clean_cohort
WHERE LOWER(TRIM(COALESCE(organisms, ''))) IN ('null', '')
   OR organisms IS NULL
   OR TRIM(organisms) = ''
""").fetchone()[0]
print(f"   Placeholder check: {place_check} (expected 0)")

pos_check = con.execute("SELECT COUNT(*) FROM clean_cohort WHERE was_positive != 1").fetchone()[0]
print(f"   Positive check: {pos_check} (expected 0)")

dup_check = con.execute("""
SELECT COUNT(*) - COUNT(DISTINCT order_proc_id_coded) FROM clean_cohort
""").fetchone()[0]
print(f"   Duplicate ID check: {dup_check} (expected 0)")

# =============================================================================
# 2. TRANSFORMATIONS
# =============================================================================
print("\n2. Applying transformations...")

con.execute("""
CREATE OR REPLACE TEMP TABLE analysis_ready AS
SELECT
    order_proc_id_coded,
    anon_id,
    pat_enc_csn_id_coded,
    order_time_jittered_utc,
    -- Normalize ordering_mode
    CASE
        WHEN LOWER(TRIM(COALESCE(ordering_mode, ''))) = 'null'
             OR TRIM(COALESCE(ordering_mode, '')) = ''
        THEN NULL
        ELSE TRIM(ordering_mode)
    END AS ordering_mode,
    -- Normalize culture_description
    CASE
        WHEN LOWER(TRIM(COALESCE(culture_description, ''))) = 'null'
             OR TRIM(COALESCE(culture_description, '')) = ''
        THEN NULL
        ELSE TRIM(culture_description)
    END AS culture_description,
    was_positive,
    total_result_rows,
    n_organisms,
    n_antibiotics,
    n_susceptibility,
    -- Normalize organisms: replace all braces with parentheses globally, then standardise semicolons
    CASE
        WHEN LOWER(TRIM(COALESCE(organisms, ''))) = 'null'
             OR TRIM(COALESCE(organisms, '')) = ''
        THEN NULL
        ELSE
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        TRIM(organisms),
                        '\\{',
                        '(',
                        'g'
                    ),
                    '\\}',
                    ')',
                    'g'
                ),
                '\\s*;\\s*',
                '; ',
                'g'
            )
    END AS organisms,
    -- Normalize antibiotics: standardise semicolons
    CASE
        WHEN LOWER(TRIM(COALESCE(antibiotics, ''))) = 'null'
             OR TRIM(COALESCE(antibiotics, '')) = ''
        THEN NULL
        ELSE REGEXP_REPLACE(TRIM(antibiotics), '\\s*;\\s*', '; ', 'g')
    END AS antibiotics,
    -- Normalize susceptibilities: remove embedded "Null" and clean delimiters
    CASE
        WHEN LOWER(TRIM(COALESCE(susceptibilities, ''))) = 'null'
             OR TRIM(COALESCE(susceptibilities, '')) = ''
        THEN NULL
        ELSE
            NULLIF(
                TRIM(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                TRIM(susceptibilities),
                                '(^|\\s*;\\s*)Null(\\s*;\\s*|$)',
                                ';',
                                'gi'
                            ),
                            '\\s*;\\s*',
                            '; ',
                            'g'
                        ),
                        '^;\\s*|\\s*;$',
                        '',
                        'g'
                    )
                ),
                ''
            )
    END AS susceptibilities,
    -- Derived variables
    EXTRACT(YEAR FROM order_time_jittered_utc) AS culture_year,
    EXTRACT(MONTH FROM order_time_jittered_utc) AS culture_month,
    EXTRACT(QUARTER FROM order_time_jittered_utc) AS culture_quarter,
    DATE_TRUNC('day', order_time_jittered_utc) AS culture_date,
    CASE WHEN n_organisms > 1 THEN 1 ELSE 0 END AS polymicrobial
FROM clean_cohort
""")

final_rows = con.execute("SELECT COUNT(*) FROM analysis_ready").fetchone()[0]
final_cultures = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM analysis_ready").fetchone()[0]
print(f"   After transformation: {final_rows:,} rows, {final_cultures:,} culture orders")

# Validate row count unchanged
if final_rows != original_rows:
    raise RuntimeError(f"Row count changed from {original_rows} to {final_rows}")
print("\n3. Validation: Row count unchanged. PASS.")

# =============================================================================
# 3. CLEANING LOG
# =============================================================================
cleaning_log = pd.DataFrame({
    'Step': [
        '1. Loaded clean cohort',
        '2. Normalized text fields (trim, standardise semicolons, removed embedded "Null", replaced all braces with parentheses)',
        '3. Added derived variables (year, month, quarter, date, polymicrobial)',
        '4. Verified no row count change'
    ],
    'Cultures_Remaining': [original_cultures, original_cultures, original_cultures, original_cultures],
    'Rows_Remaining': [original_rows, original_rows, original_rows, original_rows],
    'Cultures_Removed': [0, 0, 0, 0],
    'Rows_Removed': [0, 0, 0, 0]
})
log_file = os.path.join(OUTPUT_DIR, "Cleaning_Log.csv")
save_and_audit(cleaning_log, log_file)
print("✓ Cleaning_Log.csv audited")

# =============================================================================
# 4. DATASET PASSPORT
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
    MAX(order_time_jittered_utc) AS latest_culture_date,
    SUM(polymicrobial) AS polymicrobial_cultures,
    ROUND(100.0 * SUM(polymicrobial) / COUNT(*), 2) AS polymicrobial_percent
FROM analysis_ready
""").df()

passport_file = os.path.join(OUTPUT_DIR, "Dataset_Passport.csv")
save_and_audit(passport, passport_file, expected_values={"min_rows": 1})
print("✓ Dataset_Passport.csv audited")

print("\n📋 Dataset Passport:")
print(passport.to_string(index=False))

# =============================================================================
# 5. SAVE ANALYSIS-READY COHORT (CSV + Parquet)
# =============================================================================
csv_path = os.path.join(OUTPUT_DIR, "Analysis_Ready_Positive_Cultures.csv")
con.execute(f"""
COPY (
    SELECT * FROM analysis_ready ORDER BY order_proc_id_coded
) TO '{csv_path}' WITH (HEADER, DELIMITER ',')
""")
print(f"\n✅ CSV saved: {csv_path}")

parquet_path = os.path.join(OUTPUT_DIR, "Analysis_Ready_Positive_Cultures.parquet")
con.execute(f"""
COPY (
    SELECT * FROM analysis_ready ORDER BY order_proc_id_coded
) TO '{parquet_path}' (FORMAT PARQUET)
""")
print(f"✅ Parquet saved: {parquet_path}")

# =============================================================================
# 6. AUDIT THE MAIN DATASET
# =============================================================================
analysis_df = con.execute("""
SELECT * FROM analysis_ready ORDER BY order_proc_id_coded
""").df()

save_and_audit(
    analysis_df,
    csv_path,
    id_column="order_proc_id_coded",
    expected_values={
        "rows": final_rows,
        "unique_ids": final_cultures,
        "no_duplicates": True,
        "min_rows": 1
    },
    placeholder_values=["Null", "NULL", "null", "NA"],
    domain_rules={
        "was_positive": {"values": [1]},
        "order_proc_id_coded": {"unique": True},
        "n_organisms": {"min": 1},
        "polymicrobial": {"values": [0, 1]}
    }
)
print("✓ Analysis_Ready_Positive_Cultures.csv audited")

# =============================================================================
# 7. DATA INTEGRITY CHECKS
# =============================================================================
integrity_results = []

# 1. Row count unchanged
integrity_results.append(("Row count unchanged", final_rows == original_rows, final_rows - original_rows))

# 2. No duplicate culture IDs
dup_ids = con.execute("""
SELECT COUNT(*) - COUNT(DISTINCT order_proc_id_coded) FROM analysis_ready
""").fetchone()[0]
integrity_results.append(("No duplicate culture IDs", dup_ids == 0, dup_ids))

# 3. All are positive
pos_violations = con.execute("SELECT COUNT(*) FROM analysis_ready WHERE was_positive != 1").fetchone()[0]
integrity_results.append(("All rows are positive", pos_violations == 0, pos_violations))

# 4. No missing organisms (including "null")
org_violations = con.execute("""
SELECT COUNT(*) FROM analysis_ready
WHERE n_organisms <= 0
   OR organisms IS NULL
   OR TRIM(organisms) = ''
   OR LOWER(TRIM(organisms)) = 'null'
""").fetchone()[0]
integrity_results.append(("No missing organisms", org_violations == 0, org_violations))

# 5. Polymicrobial flag consistent
poly_check = con.execute("""
SELECT COUNT(*) FROM analysis_ready
WHERE polymicrobial != (CASE WHEN n_organisms > 1 THEN 1 ELSE 0 END)
""").fetchone()[0]
integrity_results.append(("Polymicrobial flag consistent with n_organisms", poly_check == 0, poly_check))

# 6. No embedded "Null" in susceptibilities
sus_null_check = con.execute("""
SELECT COUNT(*) FROM analysis_ready
WHERE susceptibilities ILIKE '%Null%'
""").fetchone()[0]
integrity_results.append(("No embedded Null in susceptibilities", sus_null_check == 0, sus_null_check))

# 7. Polymicrobial values are only 0 or 1
poly_values = con.execute("""
SELECT DISTINCT polymicrobial FROM analysis_ready
""").df()['polymicrobial'].tolist()
poly_valid = all(v in [0, 1] for v in poly_values)
integrity_results.append(("Polymicrobial values only 0 or 1", poly_valid, len(poly_values) - 2))

# 8. No braces remain in organisms (will now pass after global replacement)
braces_check = con.execute("""
SELECT COUNT(*) FROM analysis_ready
WHERE organisms ILIKE '%{%' OR organisms ILIKE '%}%'
""").fetchone()[0]
integrity_results.append(("No braces remain in organisms", braces_check == 0, braces_check))

# Write integrity report
integrity_file = os.path.join(OUTPUT_DIR, "Data_Integrity_Checks.txt")
with open(integrity_file, "w", encoding="utf-8") as f:
    f.write("=" * 70 + "\n")
    f.write("DATA INTEGRITY CHECKS\n")
    f.write("=" * 70 + "\n\n")
    for desc, passed, count in integrity_results:
        status = "PASS" if passed else "FAIL"
        f.write(f"✓ {desc}: {status} ({count} violations)\n")
    if all(passed for _, passed, _ in integrity_results):
        f.write("\n✅ All checks passed. Dataset is analysis-ready.\n")

print("\nData Integrity Checks:")
for desc, passed, count in integrity_results:
    print(f"  ✓ {desc}: {'PASS' if passed else 'FAIL'} ({count} violations)")

# =============================================================================
# 8. COMPLETION
# =============================================================================
print("\n" + "=" * 70)
print("STEP 3B COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"✅ Analysis-ready cohort: {final_rows:,} rows, {final_cultures:,} culture orders")
print(f"📁 All outputs saved to: {OUTPUT_DIR}")
print("  - Analysis_Ready_Positive_Cultures.csv (audited)")
print("  - Analysis_Ready_Positive_Cultures.parquet")
print("  - Cleaning_Log.csv (audited)")
print("  - Dataset_Passport.csv (audited)")
print("  - Data_Integrity_Checks.txt")
print("  - Associated audit files (.audit.txt, .audit.json) for each CSV")

con.close()