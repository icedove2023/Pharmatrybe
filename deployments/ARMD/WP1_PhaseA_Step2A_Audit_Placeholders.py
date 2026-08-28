"""
Work Package 1 - Phase A - Step 2A
Audit placeholder values ("Null", empty strings, SQL NULL) in microbiology result fields.
Reports:
  - Row-level counts and percentages.
  - Culture-order-level counts and percentages.
  - Breakdown by was_positive (negative vs positive cultures).
  - Flag for cultures that contain at least one real organism.
  - Saves unexpected positive cultures with placeholder organism to CSV.
"""

import duckdb
import pandas as pd
import os

# ---------- CONFIGURATION ----------
CSV_PATH = "Data/microbiology_cultures_cohort.csv"   # <-- CHANGE if needed
OUTPUT_DIR = os.path.join("output", "WP1 – Phase A – Step 2A")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- CONNECT AND LOAD ----------
con = duckdb.connect("armd.db")
con.execute(f"""
CREATE OR REPLACE VIEW raw_cohort AS
SELECT *
FROM read_csv_auto('{CSV_PATH}')
""")

total_rows = con.execute("SELECT COUNT(*) FROM raw_cohort").fetchone()[0]
total_cultures = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM raw_cohort").fetchone()[0]

print("=" * 70)
print("AUDIT: PLACEHOLDER VALUES IN MICROBIOLOGY RESULT FIELDS")
print("=" * 70)
print(f"Total rows               : {total_rows:,}")
print(f"Distinct culture orders  : {total_cultures:,}\n")

# -------------------------------------------------------------
# Helper function for row-level counts per field
# -------------------------------------------------------------
def count_placeholders_by_field(column):
    # Literal "Null" (case-insensitive) using COALESCE
    literal_null = con.execute(f"""
        SELECT COUNT(*) FROM raw_cohort
        WHERE LOWER(TRIM(COALESCE({column}, ''))) = 'null'
    """).fetchone()[0]

    # Empty string (non-NULL but empty or whitespace)
    empty_str = con.execute(f"""
        SELECT COUNT(*) FROM raw_cohort
        WHERE {column} IS NOT NULL
          AND TRIM({column}) = ''
    """).fetchone()[0]

    # SQL NULL
    sql_null = con.execute(f"""
        SELECT COUNT(*) FROM raw_cohort
        WHERE {column} IS NULL
    """).fetchone()[0]

    # Valid (non-placeholder)
    valid = con.execute(f"""
        SELECT COUNT(*) FROM raw_cohort
        WHERE {column} IS NOT NULL
          AND TRIM({column}) != ''
          AND LOWER(TRIM({column})) != 'null'
    """).fetchone()[0]

    return {
        'literal_null': literal_null,
        'empty_string': empty_str,
        'sql_null': sql_null,
        'valid': valid,
        'total': total_rows
    }

# -------------------------------------------------------------
# Row-level placeholder counts per field
# -------------------------------------------------------------
fields = ['organism', 'antibiotic', 'susceptibility']
row_summary = []

for field in fields:
    counts = count_placeholders_by_field(field)
    row_summary.append({
        'Field': field,
        'Literal "Null"': f"{counts['literal_null']:,} ({counts['literal_null']/total_rows:.1%})",
        'Empty string': f"{counts['empty_string']:,} ({counts['empty_string']/total_rows:.1%})",
        'SQL NULL': f"{counts['sql_null']:,} ({counts['sql_null']/total_rows:.1%})",
        'Valid': f"{counts['valid']:,} ({counts['valid']/total_rows:.1%})"
    })

row_df = pd.DataFrame(row_summary)
print("ROW-LEVEL PLACEHOLDER COUNTS")
print(row_df.to_string(index=False))
row_df.to_csv(os.path.join(OUTPUT_DIR, "WP1_Table_Placeholder_Row_Counts.csv"), index=False)

# -------------------------------------------------------------
# Culture-order-level placeholder counts per field
# -------------------------------------------------------------
def count_cultures_with_placeholder(column):
    literal_null_cultures = con.execute(f"""
        SELECT COUNT(DISTINCT order_proc_id_coded)
        FROM raw_cohort
        WHERE LOWER(TRIM(COALESCE({column}, ''))) = 'null'
    """).fetchone()[0]

    empty_str_cultures = con.execute(f"""
        SELECT COUNT(DISTINCT order_proc_id_coded)
        FROM raw_cohort
        WHERE {column} IS NOT NULL
          AND TRIM({column}) = ''
    """).fetchone()[0]

    sql_null_cultures = con.execute(f"""
        SELECT COUNT(DISTINCT order_proc_id_coded)
        FROM raw_cohort
        WHERE {column} IS NULL
    """).fetchone()[0]

    any_placeholder_cultures = con.execute(f"""
        SELECT COUNT(DISTINCT order_proc_id_coded)
        FROM raw_cohort
        WHERE LOWER(TRIM(COALESCE({column}, ''))) = 'null'
           OR {column} IS NULL
           OR TRIM({column}) = ''
    """).fetchone()[0]

    return {
        'literal_null_cultures': literal_null_cultures,
        'empty_str_cultures': empty_str_cultures,
        'sql_null_cultures': sql_null_cultures,
        'any_placeholder_cultures': any_placeholder_cultures,
        'total_cultures': total_cultures
    }

culture_summary = []
for field in fields:
    cc = count_cultures_with_placeholder(field)
    culture_summary.append({
        'Field': field,
        'Literal "Null"': f"{cc['literal_null_cultures']:,} ({cc['literal_null_cultures']/total_cultures:.1%})",
        'Empty string': f"{cc['empty_str_cultures']:,} ({cc['empty_str_cultures']/total_cultures:.1%})",
        'SQL NULL': f"{cc['sql_null_cultures']:,} ({cc['sql_null_cultures']/total_cultures:.1%})",
        'Any placeholder': f"{cc['any_placeholder_cultures']:,} ({cc['any_placeholder_cultures']/total_cultures:.1%})"
    })

culture_df = pd.DataFrame(culture_summary)
print("\nCULTURE-ORDER-LEVEL PLACEHOLDER COUNTS")
print(culture_df.to_string(index=False))
culture_df.to_csv(os.path.join(OUTPUT_DIR, "WP1_Table_Placeholder_Culture_Counts.csv"), index=False)

# -------------------------------------------------------------
# Placeholders by was_positive (row-level)
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("PLACEHOLDERS BY CULTURE POSITIVITY (ROW-LEVEL)")
print("=" * 70)

for field in fields:
    df = con.execute(f"""
    SELECT
        was_positive,
        COUNT(*) AS total_rows,
        SUM(
            CASE
                WHEN LOWER(TRIM(COALESCE({field}, ''))) = 'null'
                  OR {field} IS NULL
                  OR TRIM({field}) = ''
                THEN 1
                ELSE 0
            END
        ) AS placeholder_rows
    FROM raw_cohort
    GROUP BY was_positive
    ORDER BY was_positive
    """).df()
    df['placeholder_pct'] = (df['placeholder_rows'] / df['total_rows']).apply(lambda x: f"{x:.1%}")
    print(f"\nField: {field}")
    print(df.to_string(index=False))
    df.to_csv(os.path.join(OUTPUT_DIR, f"WP1_{field}_by_positive.csv"), index=False)

# -------------------------------------------------------------
# Placeholders by was_positive (culture-order-level)
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("PLACEHOLDERS BY CULTURE POSITIVITY (CULTURE-ORDER-LEVEL)")
print("=" * 70)

for field in fields:
    df = con.execute(f"""
    SELECT
        was_positive,
        COUNT(DISTINCT order_proc_id_coded) AS total_cultures,
        COUNT(DISTINCT CASE
            WHEN LOWER(TRIM(COALESCE({field}, ''))) = 'null'
              OR {field} IS NULL
              OR TRIM({field}) = ''
            THEN order_proc_id_coded
        END) AS placeholder_cultures
    FROM raw_cohort
    GROUP BY was_positive
    ORDER BY was_positive
    """).df()
    df['placeholder_pct'] = (df['placeholder_cultures'] / df['total_cultures']).apply(lambda x: f"{x:.1%}")
    print(f"\nField: {field}")
    print(df.to_string(index=False))
    df.to_csv(os.path.join(OUTPUT_DIR, f"WP1_{field}_by_positive_culture.csv"), index=False)

# -------------------------------------------------------------
# NEW: Identify cultures that contain at least one real organism
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("CULTURES WITH AT LEAST ONE REAL ORGANISM")
print("=" * 70)

real_org_cultures = con.execute("""
SELECT
    order_proc_id_coded,
    MAX(
        CASE
            WHEN LOWER(TRIM(COALESCE(organism, ''))) != 'null'
             AND TRIM(COALESCE(organism, '')) != ''
            THEN 1
            ELSE 0
        END
    ) AS has_real_organism
FROM raw_cohort
GROUP BY order_proc_id_coded
""").df()

total_with_real = real_org_cultures['has_real_organism'].sum()
total_without_real = len(real_org_cultures) - total_with_real

print(f"Cultures with at least one real organism: {total_with_real:,} ({total_with_real/total_cultures:.1%})")
print(f"Cultures with NO real organism: {total_without_real:,} ({total_without_real/total_cultures:.1%})")

# Save this flag table for later use
real_org_cultures.to_csv(os.path.join(OUTPUT_DIR, "WP1_Cultures_with_Real_Organism.csv"), index=False)

# -------------------------------------------------------------
# NEW: Save unexpected positive cultures with placeholder organism
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("UNEXPECTED: POSITIVE CULTURES WITH PLACEHOLDER ORGANISM")
print("=" * 70)

unexpected = con.execute("""
SELECT *
FROM raw_cohort
WHERE was_positive = 1
  AND (
      LOWER(TRIM(COALESCE(organism, ''))) = 'null'
      OR organism IS NULL
      OR TRIM(organism) = ''
  )
""").df()

print(f"Rows in unexpected category: {len(unexpected):,}")

if len(unexpected) > 0:
    # Also count distinct cultures
    distinct_unexpected = unexpected['order_proc_id_coded'].nunique()
    print(f"Distinct culture orders in this category: {distinct_unexpected:,}")
    unexpected.to_csv(
        os.path.join(OUTPUT_DIR, "PositiveCultures_With_PlaceholderOrganism.csv"),
        index=False
    )
    print(f"Saved: PositiveCultures_With_PlaceholderOrganism.csv")
else:
    print("No unexpected rows found. All positive cultures have a real organism.")

# -------------------------------------------------------------
# Completion
# -------------------------------------------------------------
print("\n" + "=" * 70)
print("AUDIT COMPLETED")
print("=" * 70)
print(f"All outputs saved to: {OUTPUT_DIR}")
print("  - WP1_Table_Placeholder_Row_Counts.csv")
print("  - WP1_Table_Placeholder_Culture_Counts.csv")
print("  - WP1_{field}_by_positive.csv (for each field)")
print("  - WP1_{field}_by_positive_culture.csv (for each field)")
print("  - WP1_Cultures_with_Real_Organism.csv")
if len(unexpected) > 0:
    print("  - PositiveCultures_With_PlaceholderOrganism.csv")

con.close()