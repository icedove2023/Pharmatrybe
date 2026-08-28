"""
Work Package 1 - Phase A - Step 2B
Profile Positive Cultures Containing Placeholder Organism Rows

- Identifies the 1,510 culture orders that have at least one row with organism='Null' among positive cultures.
- Retrieves ALL rows for those culture orders.
- Classifies each culture into categories (only Null, Null+one real organism, Null+multiple real organisms, etc.).
- Characterises antibiotics and susceptibilities, distinguishing placeholder vs real.
- Saves full data, per-culture summary, and detailed AST patterns.

All outputs saved in: output/WP1 – Phase A – Step 2B/
"""

import duckdb
import os

CSV_PATH = "Data/microbiology_cultures_cohort.csv"
OUTPUT_DIR = os.path.join("output", "WP1 – Phase A – Step 2B")
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")
con.execute(f"""
CREATE OR REPLACE VIEW raw_cohort AS
SELECT * FROM read_csv_auto('{CSV_PATH}')
""")

print("=" * 70)
print("STEP 2B: PROFILE POSITIVE CULTURES WITH PLACEHOLDER ORGANISM ROWS")
print("=" * 70)

# -------------------------------------------------------------
# 1. Create temporary table of culture orders with at least one
#    placeholder organism row among positive cultures.
# -------------------------------------------------------------
con.execute("""
CREATE OR REPLACE TEMP TABLE exception_ids AS
SELECT DISTINCT order_proc_id_coded
FROM raw_cohort
WHERE was_positive = 1
  AND (LOWER(TRIM(COALESCE(organism, ''))) = 'null'
       OR organism IS NULL
       OR TRIM(organism) = '')
""")

n_cultures = con.execute("SELECT COUNT(*) FROM exception_ids").fetchone()[0]
print(f"\nIdentified {n_cultures:,} positive culture orders with at least one placeholder organism row.")

if n_cultures == 0:
    print("No exceptions. Exiting.")
    con.close()
    exit()

# -------------------------------------------------------------
# 2. Retrieve ALL rows for these culture orders (the complete record)
# -------------------------------------------------------------
con.execute("""
CREATE OR REPLACE TEMP TABLE full_exception_rows AS
SELECT r.*
FROM raw_cohort r
JOIN exception_ids e ON r.order_proc_id_coded = e.order_proc_id_coded
ORDER BY r.order_proc_id_coded, r.order_time_jittered_utc
""")

total_rows = con.execute("SELECT COUNT(*) FROM full_exception_rows").fetchone()[0]
print(f"Total rows retrieved for these cultures: {total_rows:,}")

# Save the full dataset for manual inspection
con.execute(f"""
COPY full_exception_rows TO '{OUTPUT_DIR}/Full_Exception_Cultures_AllRows.csv'
WITH (HEADER, DELIMITER ',')
""")

# -------------------------------------------------------------
# 3. Per-culture characterisation, including classification
# -------------------------------------------------------------
con.execute("""
CREATE OR REPLACE TEMP TABLE per_culture_summary AS
SELECT
    e.order_proc_id_coded,
    COUNT(*) AS total_rows,
    SUM(CASE
        WHEN LOWER(TRIM(COALESCE(r.organism, ''))) = 'null'
          OR r.organism IS NULL
          OR TRIM(r.organism) = ''
        THEN 1
        ELSE 0
    END) AS null_organism_rows,
    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(COALESCE(r.organism, ''))) != 'null'
         AND TRIM(COALESCE(r.organism, '')) != ''
        THEN r.organism
    END) AS distinct_real_organisms,
    STRING_AGG(DISTINCT CASE
        WHEN LOWER(TRIM(COALESCE(r.organism, ''))) != 'null'
         AND TRIM(COALESCE(r.organism, '')) != ''
        THEN r.organism
    END, '; ') AS real_organisms_list,
    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(COALESCE(r.antibiotic, ''))) != 'null'
         AND TRIM(COALESCE(r.antibiotic, '')) != ''
        THEN r.antibiotic
    END) AS distinct_antibiotics,
    COUNT(DISTINCT CASE
        WHEN LOWER(TRIM(COALESCE(r.susceptibility, ''))) != 'null'
         AND TRIM(COALESCE(r.susceptibility, '')) != ''
        THEN r.susceptibility
    END) AS distinct_susceptibilities,
    -- Classification
    CASE
        WHEN COUNT(DISTINCT CASE
                WHEN LOWER(TRIM(COALESCE(r.organism, ''))) != 'null'
                 AND TRIM(COALESCE(r.organism, '')) != ''
                THEN r.organism
            END) = 0
        THEN 'A - Only Null organisms'
        WHEN COUNT(DISTINCT CASE
                WHEN LOWER(TRIM(COALESCE(r.organism, ''))) != 'null'
                 AND TRIM(COALESCE(r.organism, '')) != ''
                THEN r.organism
            END) = 1
        THEN 'B - One real organism + Null rows'
        ELSE 'C - Multiple real organisms + Null rows'
    END AS culture_category
FROM exception_ids e
JOIN raw_cohort r ON e.order_proc_id_coded = r.order_proc_id_coded
GROUP BY e.order_proc_id_coded
""")

print("\nPer-culture summary created.")

# Save per-culture summary
con.execute(f"""
COPY per_culture_summary TO '{OUTPUT_DIR}/PerCulture_Summary_Exceptions.csv'
WITH (HEADER, DELIMITER ',')
""")

# -------------------------------------------------------------
# 4. Summary statistics of the classification
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("CLASSIFICATION SUMMARY")
print("=" * 70)

category_counts = con.execute("""
SELECT culture_category, COUNT(*) AS n_cultures
FROM per_culture_summary
GROUP BY culture_category
ORDER BY culture_category
""").df()

print(category_counts.to_string(index=False))

# Also count exclusively null cultures for exclusion recommendation
exclusive_null_count = con.execute("""
SELECT COUNT(*) FROM per_culture_summary
WHERE culture_category = 'A - Only Null organisms'
""").fetchone()[0]

print(f"\nCultures exclusively Null (no real organism anywhere): {exclusive_null_count:,}")

# -------------------------------------------------------------
# 5. Characterise antibiotic and susceptibility patterns
#    We'll look at the most common patterns among Null-rows specifically.
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("PATTERNS OF ANTIBIOTICS & SUSCEPTIBILITIES IN NULL-ORGANISM ROWS")
print("=" * 70)

# This query extracts only the rows where organism is Null (or placeholder)
# and shows the antibiotics and susceptibilities associated with them.
ast_patterns = con.execute("""
SELECT
    antibiotic,
    susceptibility,
    COUNT(*) AS n_rows,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures
FROM full_exception_rows
WHERE LOWER(TRIM(COALESCE(organism, ''))) = 'null'
   OR organism IS NULL
   OR TRIM(organism) = ''
GROUP BY antibiotic, susceptibility
ORDER BY n_rows DESC
LIMIT 30
""").df()

print("\nTop 30 antibiotic–susceptibility patterns in Null-organism rows:")
print(ast_patterns.to_string(index=False))

# Save
ast_patterns.to_csv(os.path.join(OUTPUT_DIR, "NullOrganism_AST_Patterns.csv"), index=False)

# -------------------------------------------------------------
# 6. For cultures with real organisms, check if the Null rows
#    are simply duplicates of existing AST (i.e., redundant)
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("NON-NULL CULTURES: COMPARING REAL vs NULL ROWS")
print("=" * 70)

# For each culture that has at least one real organism, count how many
# antibiotics appear in both real-organism rows and Null-organism rows.
# This would indicate that Null rows are redundant AST records.
con.execute("""
CREATE OR REPLACE TEMP TABLE overlap_analysis AS
WITH real_abx AS (
    SELECT DISTINCT
        order_proc_id_coded,
        antibiotic
    FROM full_exception_rows
    WHERE LOWER(TRIM(COALESCE(organism, ''))) != 'null'
      AND TRIM(COALESCE(organism, '')) != ''
),
null_abx AS (
    SELECT DISTINCT
        order_proc_id_coded,
        antibiotic
    FROM full_exception_rows
    WHERE LOWER(TRIM(COALESCE(organism, ''))) = 'null'
       OR organism IS NULL
       OR TRIM(organism) = ''
)
SELECT
    r.order_proc_id_coded,
    COUNT(r.antibiotic) AS real_abx_count,
    COUNT(n.antibiotic) AS null_abx_count,
    COUNT(DISTINCT r.antibiotic) AS real_distinct,
    COUNT(DISTINCT n.antibiotic) AS null_distinct,
    COUNT(DISTINCT CASE WHEN n.antibiotic IS NOT NULL THEN n.antibiotic END) AS antibiotics_in_both
FROM real_abx r
LEFT JOIN null_abx n ON r.order_proc_id_coded = n.order_proc_id_coded AND r.antibiotic = n.antibiotic
GROUP BY r.order_proc_id_coded
""")

overlap = con.execute("""
SELECT
    COUNT(*) AS cultures_with_overlap,
    AVG(antibiotics_in_both) AS avg_overlap_antibiotics,
    SUM(CASE WHEN null_distinct > 0 THEN 1 ELSE 0 END) AS cultures_with_any_null_abx
FROM overlap_analysis
""").df()

print(overlap.to_string(index=False))

# -------------------------------------------------------------
# 7. Save the list of exclusively Null culture orders for potential exclusion
# -------------------------------------------------------------
if exclusive_null_count > 0:
    con.execute(f"""
    COPY (
        SELECT order_proc_id_coded
        FROM per_culture_summary
        WHERE culture_category = 'A - Only Null organisms'
    ) TO '{OUTPUT_DIR}/ExclusivelyNull_CultureOrders.csv'
    WITH (HEADER, DELIMITER ',')
    """)
    print(f"Saved list of {exclusive_null_count} exclusively-null culture orders.")

# -------------------------------------------------------------
# 8. Completion
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 2B COMPLETED")
print("=" * 70)
print(f"All outputs saved to: {OUTPUT_DIR}")
print("  - Full_Exception_Cultures_AllRows.csv")
print("  - PerCulture_Summary_Exceptions.csv")
print("  - NullOrganism_AST_Patterns.csv")
if exclusive_null_count > 0:
    print("  - ExclusivelyNull_CultureOrders.csv")

con.close()