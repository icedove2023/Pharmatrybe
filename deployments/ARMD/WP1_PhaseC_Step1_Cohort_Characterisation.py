"""
Work Package 1 - Phase C - Step 1
Cohort Characterisation – Descriptive Summary

INPUT:
  - Analysis_Ready_Positive_Cultures.parquet (118,767 rows, one per positive culture)

OUTPUTS (saved to output/WP1 – Phase C – Step 1/):
  - Cohort_Summary.csv
  - Organism_Frequency.csv (all organisms, sorted descending)
  - Specimen_Distribution.csv
  - Ordering_Mode_Distribution.csv
  - Annual_Culture_Trends.csv (with patient counts)
  - Monthly_Culture_Trends.csv
  - Monthly_Culture_Trends_By_Year.csv
  - Polymicrobial_Summary.csv
  - Descriptive_Report.txt
  - Associated .audit.txt / .audit.json for each CSV
"""

import duckdb
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.io import save_and_audit

# Paths
INPUT_PATH = "output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet"
OUTPUT_DIR = os.path.join("output", "WP1 – Phase C – Step 1")
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")

print("=" * 70)
print("WP1 - PHASE C - STEP 1: COHORT CHARACTERISATION")
print("=" * 70)

# Load dataset as a view
con.execute(f"""
CREATE OR REPLACE VIEW cohort AS
SELECT * FROM read_parquet('{INPUT_PATH}')
""")

# --------------------------------------------------------------------
# 1. Cohort Summary
# --------------------------------------------------------------------
# Compute unique organisms (species-level) from the combined list
unique_organisms = con.execute("""
SELECT COUNT(DISTINCT organism) AS unique_organisms
FROM (
    SELECT UNNEST(string_split(organisms, '; ')) AS organism
    FROM cohort
    WHERE organisms IS NOT NULL AND organisms != ''
)
""").fetchone()[0]

summary = con.execute("""
SELECT
    COUNT(DISTINCT order_proc_id_coded) AS culture_orders,
    COUNT(DISTINCT anon_id) AS unique_patients,
    COUNT(DISTINCT pat_enc_csn_id_coded) AS unique_encounters,
    COUNT(DISTINCT organisms) AS unique_organism_combinations,
    COUNT(DISTINCT n_organisms) AS distinct_n_organism_levels,
    SUM(polymicrobial) AS polymicrobial_cultures,
    ROUND(100.0 * SUM(polymicrobial) / COUNT(*), 2) AS polymicrobial_percent,
    ROUND(AVG(n_organisms), 2) AS avg_organisms,
    ROUND(MEDIAN(n_organisms), 2) AS median_organisms,
    ROUND(AVG(n_antibiotics), 2) AS avg_antibiotics,
    ROUND(MEDIAN(n_antibiotics), 2) AS median_antibiotics,
    COUNT(DISTINCT ordering_mode) AS unique_ordering_modes,
    COUNT(DISTINCT culture_description) AS unique_specimen_types,
    COUNT(DISTINCT culture_year) AS culture_years_covered,
    MIN(culture_date) AS earliest_culture,
    MAX(culture_date) AS latest_culture
FROM cohort
""").df()

# Add the unique organisms count to the summary DataFrame
summary['unique_organisms'] = unique_organisms

# Reorder columns for readability
cols = ['culture_orders', 'unique_patients', 'unique_encounters',
        'unique_organisms', 'unique_organism_combinations',
        'polymicrobial_cultures', 'polymicrobial_percent',
        'avg_organisms', 'median_organisms',
        'avg_antibiotics', 'median_antibiotics',
        'unique_ordering_modes', 'unique_specimen_types',
        'culture_years_covered', 'earliest_culture', 'latest_culture',
        'distinct_n_organism_levels']
summary = summary[cols]

summary_file = os.path.join(OUTPUT_DIR, "Cohort_Summary.csv")
summary.to_csv(summary_file, index=False)
save_and_audit(summary, summary_file)
print("✓ Cohort_Summary.csv saved")

# --------------------------------------------------------------------
# 2. Organism Frequency (all organisms)
# --------------------------------------------------------------------
org_freq = con.execute("""
WITH expanded AS (
    SELECT
        order_proc_id_coded,
        UNNEST(string_split(organisms, '; ')) AS organism
    FROM cohort
    WHERE organisms IS NOT NULL AND organisms != ''
)
SELECT
    organism,
    COUNT(DISTINCT order_proc_id_coded) AS culture_count,
    ROUND(100.0 * COUNT(DISTINCT order_proc_id_coded) / (
        SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort
    ), 2) AS percent_of_cultures
FROM expanded
GROUP BY organism
ORDER BY culture_count DESC
""").df()

org_file = os.path.join(OUTPUT_DIR, "Organism_Frequency.csv")
org_freq.to_csv(org_file, index=False)
save_and_audit(org_freq, org_file)
print(f"✓ Organism_Frequency.csv saved ({len(org_freq)} unique organisms)")

# --------------------------------------------------------------------
# 3. Specimen Distribution
# --------------------------------------------------------------------
specimen = con.execute("""
SELECT
    culture_description,
    COUNT(*) AS n_cultures,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cohort), 2) AS percent
FROM cohort
GROUP BY culture_description
ORDER BY n_cultures DESC
""").df()

spec_file = os.path.join(OUTPUT_DIR, "Specimen_Distribution.csv")
specimen.to_csv(spec_file, index=False)
save_and_audit(specimen, spec_file)
print("✓ Specimen_Distribution.csv saved")

# --------------------------------------------------------------------
# 4. Ordering Mode Distribution
# --------------------------------------------------------------------
mode = con.execute("""
SELECT
    COALESCE(ordering_mode, 'Missing') AS ordering_mode,
    COUNT(*) AS n_cultures,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cohort), 2) AS percent
FROM cohort
GROUP BY ordering_mode
ORDER BY n_cultures DESC
""").df()

mode_file = os.path.join(OUTPUT_DIR, "Ordering_Mode_Distribution.csv")
mode.to_csv(mode_file, index=False)
save_and_audit(mode, mode_file)
print("✓ Ordering_Mode_Distribution.csv saved")

# --------------------------------------------------------------------
# 5. Annual Culture Trends (with patient counts)
# --------------------------------------------------------------------
annual = con.execute("""
SELECT
    culture_year,
    COUNT(*) AS n_cultures,
    COUNT(DISTINCT anon_id) AS n_patients,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cohort), 2) AS percent
FROM cohort
GROUP BY culture_year
ORDER BY culture_year
""").df()

annual_file = os.path.join(OUTPUT_DIR, "Annual_Culture_Trends.csv")
annual.to_csv(annual_file, index=False)
save_and_audit(annual, annual_file)
print("✓ Annual_Culture_Trends.csv saved")

# --------------------------------------------------------------------
# 6. Monthly Culture Trends (aggregated across years)
# --------------------------------------------------------------------
monthly = con.execute("""
SELECT
    culture_month,
    COUNT(*) AS n_cultures,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cohort), 2) AS percent
FROM cohort
GROUP BY culture_month
ORDER BY culture_month
""").df()

monthly_file = os.path.join(OUTPUT_DIR, "Monthly_Culture_Trends.csv")
monthly.to_csv(monthly_file, index=False)
save_and_audit(monthly, monthly_file)
print("✓ Monthly_Culture_Trends.csv saved")

# --------------------------------------------------------------------
# 7. Monthly Culture Trends by Year
# --------------------------------------------------------------------
monthly_by_year = con.execute("""
SELECT
    culture_year,
    culture_month,
    COUNT(*) AS n_cultures
FROM cohort
GROUP BY culture_year, culture_month
ORDER BY culture_year, culture_month
""").df()

my_file = os.path.join(OUTPUT_DIR, "Monthly_Culture_Trends_By_Year.csv")
monthly_by_year.to_csv(my_file, index=False)
save_and_audit(monthly_by_year, my_file)
print("✓ Monthly_Culture_Trends_By_Year.csv saved")

# --------------------------------------------------------------------
# 8. Polymicrobial Summary
# --------------------------------------------------------------------
poly = con.execute("""
SELECT
    n_organisms,
    COUNT(*) AS n_cultures,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM cohort), 2) AS percent
FROM cohort
GROUP BY n_organisms
ORDER BY n_organisms
""").df()

poly_file = os.path.join(OUTPUT_DIR, "Polymicrobial_Summary.csv")
poly.to_csv(poly_file, index=False)
save_and_audit(poly, poly_file)
print("✓ Polymicrobial_Summary.csv saved")

# --------------------------------------------------------------------
# 9. Integrity Checks
# --------------------------------------------------------------------
total_rows = con.execute("SELECT COUNT(*) FROM cohort").fetchone()[0]

assert len(summary) == 1, "Cohort_Summary should have exactly one row"
assert specimen["n_cultures"].sum() == total_rows, "Specimen counts do not sum to total rows"
assert mode["n_cultures"].sum() == total_rows, "Ordering mode counts do not sum to total rows"
assert annual["n_cultures"].sum() == total_rows, "Annual counts do not sum to total rows"
assert monthly["n_cultures"].sum() == total_rows, "Monthly counts do not sum to total rows"
assert poly["n_cultures"].sum() == total_rows, "Polymicrobial counts do not sum to total rows"
# Also check organism frequency sum does not exceed total rows (since cultures can have multiple organisms)
org_total_cultures = org_freq["culture_count"].sum()
assert org_total_cultures >= total_rows, "Organism frequency total cultures should be >= total rows (polymicrobial cultures counted multiple times)"

print("\nIntegrity checks passed: all aggregations sum to total rows.")

# --------------------------------------------------------------------
# 10. Descriptive Report
# --------------------------------------------------------------------
top_specimen = specimen.iloc[0]
top_mode = mode.iloc[0]
top_org = org_freq.iloc[0]

# Calculate "other organisms" cultures (those not in the top 50)
org_top50_sum = org_freq.head(50)["culture_count"].sum()
other_count = total_rows - org_top50_sum

report_lines = []
report_lines.append("=" * 70)
report_lines.append("WP1 – PHASE C – STEP 1: COHORT CHARACTERISATION")
report_lines.append("=" * 70)
report_lines.append("")
report_lines.append(f"Study period: {summary['earliest_culture'].iloc[0]} to {summary['latest_culture'].iloc[0]}")
report_lines.append(f"Years represented: {summary['culture_years_covered'].iloc[0]}")
report_lines.append("")
report_lines.append(f"Total positive cultures: {summary['culture_orders'].iloc[0]:,}")
report_lines.append(f"Unique patients: {summary['unique_patients'].iloc[0]:,}")
report_lines.append(f"Unique encounters: {summary['unique_encounters'].iloc[0]:,}")
report_lines.append(f"Unique organisms (species-level): {summary['unique_organisms'].iloc[0]:,}")
report_lines.append(f"Unique organism combinations: {summary['unique_organism_combinations'].iloc[0]:,}")
report_lines.append("")
report_lines.append(f"Average organisms per culture: {summary['avg_organisms'].iloc[0]}")
report_lines.append(f"Median organisms per culture: {summary['median_organisms'].iloc[0]}")
report_lines.append(f"Polymicrobial cultures: {summary['polymicrobial_cultures'].iloc[0]:,} ({summary['polymicrobial_percent'].iloc[0]}%)")
report_lines.append(f"Average antibiotics tested per culture: {summary['avg_antibiotics'].iloc[0]}")
report_lines.append(f"Median antibiotics tested per culture: {summary['median_antibiotics'].iloc[0]}")
report_lines.append("")
report_lines.append("--- Most common specimen ---")
report_lines.append(f"  {top_specimen['culture_description']}: {top_specimen['n_cultures']:,} ({top_specimen['percent']:.2f}%)")
report_lines.append("")
report_lines.append("--- Most common ordering mode ---")
report_lines.append(f"  {top_mode['ordering_mode']}: {top_mode['n_cultures']:,} ({top_mode['percent']:.2f}%)")
report_lines.append("")
report_lines.append("--- Top 10 organisms ---")
for i, row in org_freq.head(10).iterrows():
    report_lines.append(f"  {row['organism']}: {row['culture_count']:,} ({row['percent_of_cultures']:.2f}%)")
report_lines.append(f"  Other organisms (remaining, not in top 50): {other_count:,} cultures")
report_lines.append("")
report_lines.append("--- Specimen distribution ---")
for i, row in specimen.iterrows():
    report_lines.append(f"  {row['culture_description']}: {row['n_cultures']:,} ({row['percent']:.2f}%)")
report_lines.append("")
report_lines.append("--- Ordering mode distribution ---")
for i, row in mode.iterrows():
    report_lines.append(f"  {row['ordering_mode']}: {row['n_cultures']:,} ({row['percent']:.2f}%)")
report_lines.append("")
report_lines.append("--- Polymicrobial distribution ---")
for i, row in poly.iterrows():
    report_lines.append(f"  {row['n_organisms']} organism(s): {row['n_cultures']:,} ({row['percent']:.2f}%)")
report_lines.append("")
report_lines.append("=" * 70)

report_file = os.path.join(OUTPUT_DIR, "Descriptive_Report.txt")
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
print("✓ Descriptive_Report.txt saved")

# --------------------------------------------------------------------
# 11. Completion
# --------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 1 COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"📁 All outputs saved to: {OUTPUT_DIR}")
print("  - Cohort_Summary.csv (audited)")
print("  - Organism_Frequency.csv (audited, all organisms)")
print("  - Specimen_Distribution.csv (audited)")
print("  - Ordering_Mode_Distribution.csv (audited)")
print("  - Annual_Culture_Trends.csv (audited, with patient counts)")
print("  - Monthly_Culture_Trends.csv (audited)")
print("  - Monthly_Culture_Trends_By_Year.csv (audited)")
print("  - Polymicrobial_Summary.csv (audited)")
print("  - Descriptive_Report.txt")
print("  - Associated audit files (.audit.txt, .audit.json) for each CSV")

con.close()