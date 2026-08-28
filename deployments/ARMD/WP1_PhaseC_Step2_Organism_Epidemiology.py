"""
Work Package 1 - Phase C - Step 2
Organism Epidemiology – Stratified Summaries

INPUT:
  - Analysis_Ready_Positive_Cultures.parquet (118,767 rows, one per positive culture)

OUTPUTS (saved to output/WP1 – Phase C – Step 2/):
  - Organism_Frequency.csv               (all organisms, sorted descending)
  - Organisms_By_Specimen.csv            (organism counts by specimen, with rank and percent)
  - Organisms_By_Ordering_Mode.csv       (organism counts by inpatient/outpatient, with rank)
  - Organisms_By_Year.csv                (top 10 organisms per year, with percent within year)
  - Polymicrobial_Pairs.csv              (top 20 co‑occurring pairs, with percent of polymicrobial cultures)
  - Descriptive_Report.txt               (plain‑text summary with key findings)
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
OUTPUT_DIR = os.path.join("output", "WP1 – Phase C – Step 2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")

print("=" * 70)
print("WP1 - PHASE C - STEP 2: ORGANISM EPIDEMIOLOGY")
print("=" * 70)

# Load dataset as a view
con.execute(f"""
CREATE OR REPLACE VIEW cohort AS
SELECT * FROM read_parquet('{INPUT_PATH}')
""")

# Total cultures
total_cultures = con.execute("SELECT COUNT(*) FROM cohort").fetchone()[0]
total_polymicrobial = con.execute("SELECT COUNT(*) FROM cohort WHERE n_organisms >= 2").fetchone()[0]

# --------------------------------------------------------------------
# 1. Organism Frequency (all organisms)
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
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
    ROUND(100.0 * COUNT(DISTINCT order_proc_id_coded) / (
        SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort
    ), 2) AS percent_of_cultures
FROM expanded
GROUP BY organism
ORDER BY n_cultures DESC
""").df()

freq_file = os.path.join(OUTPUT_DIR, "Organism_Frequency.csv")
org_freq.to_csv(freq_file, index=False)
save_and_audit(org_freq, freq_file)
print(f"✓ Organism_Frequency.csv saved ({len(org_freq)} unique organisms)")

# --------------------------------------------------------------------
# 2. Organisms by Specimen Type (with rank)
# --------------------------------------------------------------------
org_specimen = con.execute("""
WITH expanded AS (
    SELECT
        order_proc_id_coded,
        culture_description,
        UNNEST(string_split(organisms, '; ')) AS organism
    FROM cohort
    WHERE organisms IS NOT NULL AND organisms != ''
)
SELECT
    culture_description,
    organism,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
    ROUND(100.0 * COUNT(DISTINCT order_proc_id_coded) / NULLIF(
        (SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort WHERE culture_description = e.culture_description), 0
    ), 2) AS percent_within_specimen,
    RANK() OVER (PARTITION BY culture_description ORDER BY COUNT(DISTINCT order_proc_id_coded) DESC) AS rank
FROM expanded e
GROUP BY culture_description, organism
ORDER BY culture_description, rank
""").df()

spec_file = os.path.join(OUTPUT_DIR, "Organisms_By_Specimen.csv")
org_specimen.to_csv(spec_file, index=False)
save_and_audit(org_specimen, spec_file)
print("✓ Organisms_By_Specimen.csv saved")

# --------------------------------------------------------------------
# 3. Organisms by Ordering Mode (with rank)
# --------------------------------------------------------------------
org_mode = con.execute("""
WITH expanded AS (
    SELECT
        order_proc_id_coded,
        COALESCE(ordering_mode, 'Missing') AS ordering_mode,
        UNNEST(string_split(organisms, '; ')) AS organism
    FROM cohort
    WHERE organisms IS NOT NULL AND organisms != ''
)
SELECT
    ordering_mode,
    organism,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
    ROUND(100.0 * COUNT(DISTINCT order_proc_id_coded) / NULLIF(
        (SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort WHERE COALESCE(ordering_mode, 'Missing') = e.ordering_mode), 0
    ), 2) AS percent_within_mode,
    RANK() OVER (PARTITION BY ordering_mode ORDER BY COUNT(DISTINCT order_proc_id_coded) DESC) AS rank
FROM expanded e
GROUP BY ordering_mode, organism
ORDER BY ordering_mode, rank
""").df()

mode_file = os.path.join(OUTPUT_DIR, "Organisms_By_Ordering_Mode.csv")
org_mode.to_csv(mode_file, index=False)
save_and_audit(org_mode, mode_file)
print("✓ Organisms_By_Ordering_Mode.csv saved")

# --------------------------------------------------------------------
# 4. Organisms by Year (top 10 per year, with percent within year)
# --------------------------------------------------------------------
org_year = con.execute("""
WITH expanded AS (
    SELECT
        order_proc_id_coded,
        culture_year,
        UNNEST(string_split(organisms, '; ')) AS organism
    FROM cohort
    WHERE organisms IS NOT NULL AND organisms != ''
)
SELECT
    culture_year,
    organism,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
    ROUND(100.0 * COUNT(DISTINCT order_proc_id_coded) / (
        SELECT COUNT(DISTINCT order_proc_id_coded)
        FROM cohort c2
        WHERE c2.culture_year = e.culture_year
    ), 2) AS percent_within_year,
    RANK() OVER (PARTITION BY culture_year ORDER BY COUNT(DISTINCT order_proc_id_coded) DESC) AS rank
FROM expanded e
GROUP BY culture_year, organism
QUALIFY rank <= 10
ORDER BY culture_year, rank
""").df()

year_file = os.path.join(OUTPUT_DIR, "Organisms_By_Year.csv")
org_year.to_csv(year_file, index=False)
save_and_audit(org_year, year_file)
print("✓ Organisms_By_Year.csv saved")

# --------------------------------------------------------------------
# 5. Polymicrobial Pairs (top 20 co‑occurring pairs)
#    Only for cultures with n_organisms >= 2, using distinct organisms
# --------------------------------------------------------------------
pairs = con.execute("""
WITH expanded AS (
    SELECT
        order_proc_id_coded,
        organism
    FROM (
        SELECT
            order_proc_id_coded,
            UNNEST(string_split(organisms, '; ')) AS organism
        FROM cohort
        WHERE n_organisms >= 2
    )
    GROUP BY order_proc_id_coded, organism
),
pairs AS (
    SELECT
        o1.order_proc_id_coded,
        o1.organism AS org1,
        o2.organism AS org2
    FROM expanded o1
    JOIN expanded o2
    ON o1.order_proc_id_coded = o2.order_proc_id_coded
    AND o1.organism < o2.organism
)
SELECT
    org1,
    org2,
    COUNT(DISTINCT order_proc_id_coded) AS pair_count,
    ROUND(100.0 * COUNT(DISTINCT order_proc_id_coded) / (
        SELECT COUNT(DISTINCT order_proc_id_coded)
        FROM cohort
        WHERE n_organisms >= 2
    ), 2) AS percent_of_polymicrobial
FROM pairs
GROUP BY org1, org2
ORDER BY pair_count DESC
LIMIT 20
""").df()

pairs_file = os.path.join(OUTPUT_DIR, "Polymicrobial_Pairs.csv")
pairs.to_csv(pairs_file, index=False)
save_and_audit(pairs, pairs_file)
print("✓ Polymicrobial_Pairs.csv saved")

# --------------------------------------------------------------------
# 6. Integrity Checks
# --------------------------------------------------------------------
# Overall organism counts sum to >= total cultures (polymicrobial counted multiple times)
assert org_freq["n_cultures"].sum() >= total_cultures, "Organism counts should be >= total cultures"

# For each specimen, sum of organism counts >= specimen total
for spec in org_specimen["culture_description"].unique():
    spec_total = con.execute(f"SELECT COUNT(DISTINCT order_proc_id_coded) FROM cohort WHERE culture_description = '{spec}'").fetchone()[0]
    spec_sum = org_specimen[org_specimen["culture_description"] == spec]["n_cultures"].sum()
    assert spec_sum >= spec_total, f"For specimen {spec}, sum ({spec_sum}) should be >= specimen total ({spec_total})"

print("\nIntegrity checks passed.")

# --------------------------------------------------------------------
# 7. Descriptive Report
# --------------------------------------------------------------------
# Top organism overall
top_org = org_freq.iloc[0]
# Top polymicrobial pair
top_pair = pairs.iloc[0] if len(pairs) > 0 else None

report_lines = []
report_lines.append("=" * 70)
report_lines.append("WP1 – PHASE C – STEP 2: ORGANISM EPIDEMIOLOGY")
report_lines.append("=" * 70)
report_lines.append("")
report_lines.append(f"Total positive cultures: {total_cultures:,}")
report_lines.append(f"Unique organisms (species-level): {len(org_freq):,}")
report_lines.append(f"Polymicrobial cultures (≥2 organisms): {total_polymicrobial:,} ({total_polymicrobial/total_cultures*100:.2f}%)")
report_lines.append("")
report_lines.append(f"Most common organism overall: {top_org['organism']} ({top_org['n_cultures']:,} cultures, {top_org['percent_of_cultures']:.2f}%)")
if top_pair is not None:
    report_lines.append(f"Most common polymicrobial pair: {top_pair['org1']} + {top_pair['org2']} ({top_pair['pair_count']} cultures, {top_pair['percent_of_polymicrobial']:.2f}% of polymicrobial cultures)")
report_lines.append("")
report_lines.append("--- Top 5 organisms by specimen ---")
for spec in ['URINE', 'RESPIRATORY', 'BLOOD']:
    top5 = org_specimen[org_specimen["culture_description"] == spec].head(5)
    report_lines.append(f"  {spec}:")
    for _, row in top5.iterrows():
        report_lines.append(f"    {row['organism']}: {row['n_cultures']} ({row['percent_within_specimen']:.2f}% of {spec})")
report_lines.append("")
report_lines.append("--- Top 5 organisms by ordering mode ---")
for mode in ['Inpatient', 'Outpatient', 'Missing']:
    top5 = org_mode[org_mode["ordering_mode"] == mode].head(5)
    report_lines.append(f"  {mode}:")
    for _, row in top5.iterrows():
        report_lines.append(f"    {row['organism']}: {row['n_cultures']} ({row['percent_within_mode']:.2f}% of {mode})")
report_lines.append("")
report_lines.append("=" * 70)

report_file = os.path.join(OUTPUT_DIR, "Descriptive_Report.txt")
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))
print("✓ Descriptive_Report.txt saved")

# --------------------------------------------------------------------
# 8. Completion
# --------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 2 COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"📁 All outputs saved to: {OUTPUT_DIR}")
print("  - Organism_Frequency.csv (audited, all organisms)")
print("  - Organisms_By_Specimen.csv (audited)")
print("  - Organisms_By_Ordering_Mode.csv (audited)")
print("  - Organisms_By_Year.csv (audited)")
print("  - Polymicrobial_Pairs.csv (audited)")
print("  - Descriptive_Report.txt")
print("  - Associated audit files (.audit.txt, .audit.json) for each CSV")

con.close()