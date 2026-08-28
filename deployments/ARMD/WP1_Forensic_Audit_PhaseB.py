"""
WP1 Forensic Audit – Phase B Dataset
====================================
Determines the true structure of organisms, antibiotics, and susceptibilities.
No assumptions. All findings are data-driven.

Phases:
A. Dataset Integrity
B. Schema
C. Column Profiling (placeholders)
D. Organism Audit
E. Antibiotic Audit
F. Susceptibility Audit
G. Separator Audit
H. Pairing Audit (counts per culture)
I. Pairing Pattern Audit (1 vs many)
J. Long Table Simulation (sample)
K. Data Model Inference
L. Final Verdict

Outputs saved to: output/WP1 – Audit – PhaseB/
"""

import duckdb
import pandas as pd
import os
import sys
import re
from datetime import datetime

# Add project root for utils (if needed, but we'll use simple to_csv)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# We'll use our own audit function for CSVs to keep consistency
# (If save_and_audit exists, we can use it; otherwise we'll just save.)

OUTPUT_DIR = "output/WP1 – Audit – PhaseB"
os.makedirs(OUTPUT_DIR, exist_ok=True)

INPUT_PARQUET = "output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet"

con = duckdb.connect("armd.db")

print("=" * 80)
print("WP1 FORENSIC AUDIT: PHASE B DATASET")
print("=" * 80)

# --------------------------------------------------------------
# Helper to save a DataFrame and write a simple audit message
# --------------------------------------------------------------
def save_df(df, filename, description=""):
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  ✓ Saved {filename} ({len(df)} rows)" + (f" - {description}" if description else ""))
    return path

# --------------------------------------------------------------
# PHASE A: Dataset Integrity
# --------------------------------------------------------------
print("\nPHASE A: Dataset Integrity")
print("-" * 40)

# Check file exists
if not os.path.exists(INPUT_PARQUET):
    raise FileNotFoundError(f"Input file not found: {INPUT_PARQUET}")
print(f"✓ File exists: {INPUT_PARQUET}")

# Row count
total_rows = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
print(f"  Total rows: {total_rows:,}")

# Duplicate culture IDs
dup_cultures = con.execute(f"""
SELECT COUNT(*) - COUNT(DISTINCT order_proc_id_coded)
FROM read_parquet('{INPUT_PARQUET}')
""").fetchone()[0]
print(f"  Duplicate culture IDs: {dup_cultures:,}")

# Duplicate anon_id, pat_enc_csn_id_coded (if exist)
dup_anon = con.execute(f"""
SELECT COUNT(*) - COUNT(DISTINCT anon_id)
FROM read_parquet('{INPUT_PARQUET}')
""").fetchone()[0]
print(f"  Duplicate patient IDs: {dup_anon:,}")

dup_enc = con.execute(f"""
SELECT COUNT(*) - COUNT(DISTINCT pat_enc_csn_id_coded)
FROM read_parquet('{INPUT_PARQUET}')
""").fetchone()[0]
print(f"  Duplicate encounter IDs: {dup_enc:,}")

# --------------------------------------------------------------
# PHASE B: Schema
# --------------------------------------------------------------
print("\nPHASE B: Schema")
print("-" * 40)
schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{INPUT_PARQUET}')").df()
print(schema.to_string(index=False))
save_df(schema, "B_Schema.csv")

# --------------------------------------------------------------
# PHASE C: Column Profiling (placeholders)
# --------------------------------------------------------------
print("\nPHASE C: Column Profiling")
print("-" * 40)

# Columns of interest
cols = ['anon_id', 'pat_enc_csn_id_coded', 'ordering_mode', 'culture_description',
        'organisms', 'antibiotics', 'susceptibilities', 'polymicrobial', 'n_organisms', 'n_antibiotics']

profiles = []
for col in cols:
    # Count non-null, blank, literal "Null", etc.
    q = f"""
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS null_count,
        SUM(CASE WHEN TRIM(COALESCE({col}, '')) = '' THEN 1 ELSE 0 END) AS blank_count,
        SUM(CASE WHEN LOWER(TRIM(COALESCE({col}, ''))) = 'null' THEN 1 ELSE 0 END) AS literal_null,
        COUNT(DISTINCT {col}) AS distinct_values
    FROM read_parquet('{INPUT_PARQUET}')
    """
    res = con.execute(q).df()
    res['column'] = col
    profiles.append(res)

profile_df = pd.concat(profiles, ignore_index=True)
print(profile_df.to_string(index=False))
save_df(profile_df, "C_Column_Profiling.csv")

# --------------------------------------------------------------
# PHASE D: Organism Audit (raw strings, split counts, issues)
# --------------------------------------------------------------
print("\nPHASE D: Organism Audit")
print("-" * 40)

# We'll use a sample of rows (or all) to detect issues.
# We'll create a temp table with organism strings
org_audit = con.execute(f"""
WITH org_data AS (
    SELECT
        order_proc_id_coded,
        organisms AS raw_org,
        string_split(organisms, '; ') AS org_list,
        array_length(string_split(organisms, '; ')) AS n_org
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE organisms IS NOT NULL
)
SELECT
    COUNT(*) AS total_cultures,
    SUM(CASE WHEN n_org = 0 THEN 1 ELSE 0 END) AS zero_org,
    SUM(CASE WHEN n_org = 1 THEN 1 ELSE 0 END) AS one_org,
    SUM(CASE WHEN n_org > 1 THEN 1 ELSE 0 END) AS multi_org,
    SUM(CASE WHEN raw_org LIKE '%;' THEN 1 ELSE 0 END) AS trailing_semi,
    SUM(CASE WHEN raw_org LIKE '%; %' THEN 1 ELSE 0 END) AS has_space_after_semi,
    SUM(CASE WHEN raw_org LIKE '%  %' THEN 1 ELSE 0 END) AS double_space,
    SUM(CASE WHEN raw_org LIKE '%\t%' THEN 1 ELSE 0 END) AS tab,
    SUM(CASE WHEN raw_org LIKE '%\n%' THEN 1 ELSE 0 END) AS newline
FROM org_data
""").df()
print("Organism audit:")
print(org_audit.to_string(index=False))
save_df(org_audit, "D_Organism_Audit.csv")

# Also get distinct organism strings (for inspection)
org_sample = con.execute(f"""
SELECT DISTINCT organisms
FROM read_parquet('{INPUT_PARQUET}')
WHERE organisms IS NOT NULL AND organisms != ''
LIMIT 100
""").df()
save_df(org_sample, "D_Organism_Sample.csv")

# --------------------------------------------------------------
# PHASE E: Antibiotic Audit
# --------------------------------------------------------------
print("\nPHASE E: Antibiotic Audit")
print("-" * 40)
abx_audit = con.execute(f"""
WITH abx_data AS (
    SELECT
        order_proc_id_coded,
        antibiotics AS raw_abx,
        string_split(antibiotics, '; ') AS abx_list,
        array_length(string_split(antibiotics, '; ')) AS n_abx
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE antibiotics IS NOT NULL
)
SELECT
    COUNT(*) AS total_cultures,
    SUM(CASE WHEN n_abx = 0 THEN 1 ELSE 0 END) AS zero_abx,
    SUM(CASE WHEN n_abx = 1 THEN 1 ELSE 0 END) AS one_abx,
    SUM(CASE WHEN n_abx > 1 THEN 1 ELSE 0 END) AS multi_abx,
    SUM(CASE WHEN raw_abx LIKE '%;' THEN 1 ELSE 0 END) AS trailing_semi,
    SUM(CASE WHEN raw_abx LIKE '%; %' THEN 1 ELSE 0 END) AS has_space_after_semi
FROM abx_data
""").df()
print("Antibiotic audit:")
print(abx_audit.to_string(index=False))
save_df(abx_audit, "E_Antibiotic_Audit.csv")

abx_sample = con.execute(f"""
SELECT DISTINCT antibiotics
FROM read_parquet('{INPUT_PARQUET}')
WHERE antibiotics IS NOT NULL AND antibiotics != ''
LIMIT 100
""").df()
save_df(abx_sample, "E_Antibiotic_Sample.csv")

# --------------------------------------------------------------
# PHASE F: Susceptibility Audit
# --------------------------------------------------------------
print("\nPHASE F: Susceptibility Audit")
print("-" * 40)

# First, count distinct susceptibility strings
susc_distinct = con.execute(f"""
SELECT
    susceptibilities,
    COUNT(*) AS n
FROM read_parquet('{INPUT_PARQUET}')
WHERE susceptibilities IS NOT NULL
GROUP BY susceptibilities
ORDER BY n DESC
""").df()
print("Top 20 susceptibility strings:")
print(susc_distinct.head(20).to_string(index=False))
save_df(susc_distinct, "F_Susceptibility_Distinct.csv")

# Count values (split)
susc_values = con.execute(f"""
SELECT UNNEST(string_split(susceptibilities, '; ')) AS val
FROM read_parquet('{INPUT_PARQUET}')
WHERE susceptibilities IS NOT NULL AND susceptibilities != ''
""").df()
susc_value_counts = susc_values['val'].value_counts().reset_index()
susc_value_counts.columns = ['value', 'count']
print("Top 20 susceptibility values:")
print(susc_value_counts.head(20).to_string(index=False))
save_df(susc_value_counts, "F_Susceptibility_Values.csv")

# --------------------------------------------------------------
# PHASE G: Separator Audit
# --------------------------------------------------------------
print("\nPHASE G: Separator Audit")
print("-" * 40)

# For organisms, antibiotics, susceptibilities, detect which separators appear
sep_audit = con.execute(f"""
WITH sep AS (
    SELECT
        organisms AS text,
        'organisms' AS field
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE organisms IS NOT NULL
    UNION ALL
    SELECT antibiotics, 'antibiotics'
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE antibiotics IS NOT NULL
    UNION ALL
    SELECT susceptibilities, 'susceptibilities'
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE susceptibilities IS NOT NULL
)
SELECT
    field,
    SUM(CASE WHEN text LIKE '%; %' THEN 1 ELSE 0 END) AS semi_space,
    SUM(CASE WHEN text LIKE '%;%' AND NOT text LIKE '%; %' THEN 1 ELSE 0 END) AS semi_no_space,
    SUM(CASE WHEN text LIKE '%|%' THEN 1 ELSE 0 END) AS pipe,
    SUM(CASE WHEN text LIKE '%, %' THEN 1 ELSE 0 END) AS comma_space,
    SUM(CASE WHEN text LIKE '%,%' AND NOT text LIKE '%, %' THEN 1 ELSE 0 END) AS comma_no_space,
    SUM(CASE WHEN text LIKE '%/%' THEN 1 ELSE 0 END) AS slash,
    SUM(CASE WHEN text LIKE '%::%' THEN 1 ELSE 0 END) AS colon_colon
FROM sep
GROUP BY field
""").df()
print("Separator audit:")
print(sep_audit.to_string(index=False))
save_df(sep_audit, "G_Separator_Audit.csv")

# --------------------------------------------------------------
# PHASE H: Pairing Audit (counts)
# --------------------------------------------------------------
print("\nPHASE H: Pairing Audit (counts)")
print("-" * 40)

pairing = con.execute(f"""
WITH counts AS (
    SELECT
        order_proc_id_coded,
        array_length(string_split(organisms, '; ')) AS n_org,
        array_length(string_split(antibiotics, '; ')) AS n_abx,
        array_length(string_split(susceptibilities, '; ')) AS n_susc
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE organisms IS NOT NULL AND antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
)
SELECT
    COUNT(*) AS total_cultures,
    SUM(CASE WHEN n_org = n_abx AND n_abx = n_susc THEN 1 ELSE 0 END) AS perfect,
    SUM(CASE WHEN n_org = n_abx AND n_abx != n_susc THEN 1 ELSE 0 END) AS org_eq_abx_ne_susc,
    SUM(CASE WHEN n_org = n_susc AND n_org != n_abx THEN 1 ELSE 0 END) AS org_eq_susc_ne_abx,
    SUM(CASE WHEN n_abx = n_susc AND n_abx != n_org THEN 1 ELSE 0 END) AS abx_eq_susc_ne_org,
    SUM(CASE WHEN n_org != n_abx AND n_abx != n_susc AND n_org != n_susc THEN 1 ELSE 0 END) AS all_different,
    SUM(CASE WHEN n_org = 1 AND n_abx > 1 THEN 1 ELSE 0 END) AS one_org_many_abx,
    SUM(CASE WHEN n_org > 1 AND n_abx = 1 THEN 1 ELSE 0 END) AS many_org_one_abx,
    SUM(CASE WHEN n_org > 1 AND n_abx > 1 AND n_org = n_abx THEN 1 ELSE 0 END) AS equal_multi,
    SUM(CASE WHEN n_org > 1 AND n_abx > 1 AND n_org != n_abx THEN 1 ELSE 0 END) AS unequal_multi
FROM counts
""").df()
print("Pairing categories:")
print(pairing.to_string(index=False))
save_df(pairing, "H_Pairing_Counts.csv")

# Also save the cultures with mismatches (sample)
mismatch_cultures = con.execute(f"""
WITH counts AS (
    SELECT
        order_proc_id_coded,
        organisms,
        antibiotics,
        susceptibilities,
        array_length(string_split(organisms, '; ')) AS n_org,
        array_length(string_split(antibiotics, '; ')) AS n_abx,
        array_length(string_split(susceptibilities, '; ')) AS n_susc
    FROM read_parquet('{INPUT_PARQUET}')
    WHERE organisms IS NOT NULL AND antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
)
SELECT *
FROM counts
WHERE n_org != n_abx OR n_abx != n_susc
LIMIT 20
""").df()
save_df(mismatch_cultures, "H_Mismatch_Examples.csv")

# --------------------------------------------------------------
# PHASE I: Long Table Simulation (sample)
# --------------------------------------------------------------
print("\nPHASE I: Long Table Simulation (sample of 100 random rows)")
print("-" * 40)

# We'll use a subset of rows that have perfect pairing (or we'll split anyway)
# Create a simulated long table from 100 random rows
sim_long = con.execute(f"""
WITH sample AS (
    SELECT *
    FROM read_parquet('{INPUT_PARQUET}')
    TABLESAMPLE 100 ROWS
    WHERE organisms IS NOT NULL AND antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
)
SELECT
    order_proc_id_coded,
    anon_id,
    culture_description,
    ordering_mode,
    UNNEST(string_split(organisms, '; ')) AS organism,
    UNNEST(string_split(antibiotics, '; ')) AS antibiotic,
    UNNEST(string_split(susceptibilities, '; ')) AS susceptibility
FROM sample
""").df()
print("Simulated long table (first 20 rows):")
print(sim_long.head(20).to_string(index=False))
save_df(sim_long, "I_Long_Table_Simulation.csv")

# --------------------------------------------------------------
# PHASE J: Data Model Inference
# --------------------------------------------------------------
print("\nPHASE J: Data Model Inference")
print("-" * 40)

# We can infer based on the pairing categories:
# - If most cultures have n_org == n_abx == n_susc, then it's likely organism-specific pairing (each organism has its own antibiotics)
# - If many have one_org_many_abx, then antibiotics are culture-wide
# - If many have many_org_one_abx, that's unusual (could be a single antibiotic for all organisms)

inference = []
if pairing['perfect'][0] > 0.8 * pairing['total_cultures'][0]:
    inference.append("Most cultures have perfect pairing: organism-antibiotic-susceptibility are aligned.")
if pairing['one_org_many_abx'][0] > 0.1 * pairing['total_cultures'][0]:
    inference.append("Significant proportion have one organism with multiple antibiotics: likely culture-wide antibiogram.")
if pairing['abx_eq_susc_ne_org'][0] > 0.05 * pairing['total_cultures'][0]:
    inference.append("Some cultures have antibiotics and susceptibilities equal but organism count different: may indicate organism grouping.")
# Check if there are mixed patterns
print("Inference based on pairing counts:")
for line in inference:
    print(f"  - {line}")
if not inference:
    print("  No clear dominant pattern. Likely mixed data model.")

# --------------------------------------------------------------
# PHASE K: Final Verdict
# --------------------------------------------------------------
print("\nPHASE K: Final Verdict")
print("-" * 40)

# Summarize key findings
verdict = []
verdict.append(f"Total rows: {total_rows:,}")
verdict.append(f"Duplicate culture IDs: {dup_cultures:,}")
verdict.append("")
verdict.append(f"Cultures with organism count = antibiotic count = susceptibility count: {pairing['perfect'][0]:,} ({pairing['perfect'][0]/pairing['total_cultures'][0]*100:.2f}%)")
verdict.append(f"Cultures with organism count = 1 and antibiotic count > 1: {pairing['one_org_many_abx'][0]:,} ({pairing['one_org_many_abx'][0]/pairing['total_cultures'][0]*100:.2f}%)")
verdict.append(f"Cultures with unequal counts (all different): {pairing['all_different'][0]:,}")
verdict.append("")
# Susceptibility value formats
susc_formats = susc_value_counts['value'].str.upper().unique()
verdict.append("Susceptibility value formats detected:")
for val in susc_formats[:10]:
    verdict.append(f"  - {val}")
if any('RESISTANT' in v for v in susc_formats):
    verdict.append("  --> Words (Resistant/Susceptible) detected.")
if any(v in ['S','I','R'] for v in susc_formats):
    verdict.append("  --> Codes (S/I/R) detected.")
verdict.append("")
verdict.append("Separator used:")
for idx, row in sep_audit.iterrows():
    field = row['field']
    # Find the predominant separator
    max_sep = row[['semi_space','semi_no_space','pipe','comma_space','comma_no_space','slash','colon_colon']].idxmax()
    verdict.append(f"  {field}: {max_sep} ({row[max_sep]} occurrences)")

verdict.append("")
verdict.append("Recommended approach for long table:")
if pairing['perfect'][0] > 0.8 * pairing['total_cultures'][0]:
    verdict.append("  Use positional pairing (list_zip) as most rows are aligned.")
elif pairing['one_org_many_abx'][0] > 0.5 * pairing['total_cultures'][0]:
    verdict.append("  Most cultures have single organism with multiple antibiotics. Use cross-join for each organism?")
    verdict.append("  But verify if antibiotics are organism-specific or culture-wide.")
else:
    verdict.append("  Mixed structure. Need to inspect mismatches and decide case-by-case.")
    verdict.append("  Consider using the 'organisms' list as one field and 'antibiotics' as another, but be cautious.")

# Write verdict to file
verdict_text = "\n".join(verdict)
with open(os.path.join(OUTPUT_DIR, "K_Final_Verdict.txt"), 'w') as f:
    f.write("WP1 PHASE B FORENSIC AUDIT – FINAL VERDICT\n")
    f.write("=" * 60 + "\n")
    f.write(verdict_text)
print("\nVerdict written to K_Final_Verdict.txt")

# --------------------------------------------------------------
# Summary of all outputs
# --------------------------------------------------------------
print("\n" + "=" * 80)
print("FORENSIC AUDIT COMPLETED")
print("=" * 80)
print(f"All outputs saved to: {OUTPUT_DIR}")
print("Files generated:")
files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv') or f.endswith('.txt')]
for f in sorted(files):
    print(f"  - {f}")

con.close()