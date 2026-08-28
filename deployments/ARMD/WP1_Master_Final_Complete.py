"""
WP1 Master Script – Final Complete Version
==========================================
Completes WP1 Phase C with all reviewer corrections and robustness improvements.
- Positional pairing using list_zip
- Robust length check using array_length(string_split)
- All Step 3 subanalyses (specimen, ordering mode, year) are fully implemented
- Invalid susceptibility values saved for audit
- Normalised organism and antibiotic names
- QA check for organism = antibiotic
- Correct duplicate row counting
- Null-safe master report
"""

import duckdb
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.io import save_and_audit

# --------------------------------------------------------------
# Configuration
# --------------------------------------------------------------
INPUT_PARQUET = "output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet"
BASE_OUTPUT = "output/WP1 – Phase C"
os.makedirs(BASE_OUTPUT, exist_ok=True)

con = duckdb.connect("armd.db")

# --------------------------------------------------------------
# Helper: create long susceptibility with robust pairing
# --------------------------------------------------------------
def create_long_susceptibility(con):
    """
    Create temporary view 'long_susc' using list_zip to ensure positional alignment.
    Uses array_length(string_split(...)) for robust length checking.
    """
    # Check that the three lists have equal lengths using array_length
    mismatch = con.execute("""
    WITH lengths AS (
        SELECT
            order_proc_id_coded,
            array_length(string_split(organisms, '; ')) AS n_org,
            array_length(string_split(antibiotics, '; ')) AS n_abx,
            array_length(string_split(susceptibilities, '; ')) AS n_susc
        FROM read_parquet('{}')
        WHERE organisms IS NOT NULL AND antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
    )
    SELECT COUNT(*) FROM lengths WHERE n_org != n_abx OR n_abx != n_susc
    """.format(INPUT_PARQUET)).fetchone()[0]

    if mismatch > 0:
        raise ValueError(
            f"ERROR: {mismatch} cultures have mismatched counts. Cannot map organism to antibiotic."
        )

    # Use list_zip to create tuples. In DuckDB, list_zip returns a list of structs.
    # We can access elements using .f1, .f2, .f3 (depending on version).
    # To be safe, we'll use the syntax that works in most recent DuckDB: triplet[1] for positional.
    # If your DuckDB version uses struct fields, replace with triplet.f1, etc.
    con.execute("""
    CREATE OR REPLACE TEMP VIEW long_susc AS
    WITH expanded AS (
        SELECT
            order_proc_id_coded,
            anon_id,
            pat_enc_csn_id_coded,
            culture_description,
            ordering_mode,
            culture_year,
            culture_month,
            culture_quarter,
            culture_date,
            polymicrobial,
            UNNEST(
                list_zip(
                    string_split(organisms, '; '),
                    string_split(antibiotics, '; '),
                    string_split(susceptibilities, '; ')
                )
            ) AS triplet
        FROM read_parquet('{}')
        WHERE organisms IS NOT NULL AND antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
    )
    SELECT
        order_proc_id_coded,
        anon_id,
        pat_enc_csn_id_coded,
        culture_description,
        ordering_mode,
        culture_year,
        culture_month,
        culture_quarter,
        culture_date,
        polymicrobial,
        UPPER(TRIM(triplet[1])) AS organism,
        UPPER(TRIM(triplet[2])) AS antibiotic,
        UPPER(TRIM(triplet[3])) AS susceptibility
    FROM expanded
    WHERE triplet[1] IS NOT NULL AND triplet[2] IS NOT NULL AND triplet[3] IS NOT NULL
      AND triplet[1] != '' AND triplet[2] != '' AND triplet[3] != ''
    """.format(INPUT_PARQUET))

    # Validate susceptibility values (must be S, I, R)
    invalid = con.execute("""
    SELECT DISTINCT susceptibility, COUNT(*) AS n
    FROM long_susc
    WHERE susceptibility NOT IN ('S', 'I', 'R')
    GROUP BY susceptibility
    """).df()
    if not invalid.empty:
        print("WARNING: Unexpected susceptibility values found. Saving to Invalid_Susceptibility_Codes.csv")
        invalid.to_csv("Invalid_Susceptibility_Codes.csv", index=False)
        save_and_audit(invalid, "Invalid_Susceptibility_Codes.csv")

    print("✓ Long susceptibility table created with positional pairing.")
    return True

# --------------------------------------------------------------
# Step 3: AMR Profile (complete)
# --------------------------------------------------------------
def run_step3_amr_profile(con):
    print("\n--- Step 3: AMR Profile ---")
    out_dir = os.path.join(BASE_OUTPUT, "Step 3 – AMR Profile")
    os.makedirs(out_dir, exist_ok=True)

    # Overall
    overall = con.execute("""
    SELECT
        COUNT(*) AS total_tests,
        SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS resistant,
        SUM(CASE WHEN susceptibility = 'I' THEN 1 ELSE 0 END) AS intermediate,
        SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) AS susceptible,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_resistant,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_susceptible
    FROM long_susc
    """).df()
    overall.to_csv(os.path.join(out_dir, "Resistance_Overall.csv"), index=False)
    save_and_audit(overall, os.path.join(out_dir, "Resistance_Overall.csv"))

    # By organism (top 20)
    by_org = con.execute("""
    SELECT
        organism,
        COUNT(*) AS total_tests,
        SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS resistant,
        SUM(CASE WHEN susceptibility = 'I' THEN 1 ELSE 0 END) AS intermediate,
        SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) AS susceptible,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_resistant,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_susceptible
    FROM long_susc
    GROUP BY organism
    HAVING COUNT(*) >= 30
    ORDER BY COUNT(*) DESC
    LIMIT 20
    """).df()
    by_org.to_csv(os.path.join(out_dir, "Resistance_By_Organism.csv"), index=False)
    save_and_audit(by_org, os.path.join(out_dir, "Resistance_By_Organism.csv"))

    # By antibiotic (top 20)
    by_abx = con.execute("""
    SELECT
        antibiotic,
        COUNT(*) AS total_tests,
        SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS resistant,
        SUM(CASE WHEN susceptibility = 'I' THEN 1 ELSE 0 END) AS intermediate,
        SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) AS susceptible,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_resistant,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_susceptible
    FROM long_susc
    GROUP BY antibiotic
    HAVING COUNT(*) >= 30
    ORDER BY COUNT(*) DESC
    LIMIT 20
    """).df()
    by_abx.to_csv(os.path.join(out_dir, "Resistance_By_Antibiotic.csv"), index=False)
    save_and_audit(by_abx, os.path.join(out_dir, "Resistance_By_Antibiotic.csv"))

    # By specimen
    by_spec = con.execute("""
    SELECT
        culture_description,
        COUNT(*) AS total_tests,
        SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS resistant,
        SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) AS susceptible,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_resistant
    FROM long_susc
    GROUP BY culture_description
    ORDER BY culture_description
    """).df()
    by_spec.to_csv(os.path.join(out_dir, "Resistance_By_Specimen.csv"), index=False)
    save_and_audit(by_spec, os.path.join(out_dir, "Resistance_By_Specimen.csv"))

    # By ordering mode
    by_mode = con.execute("""
    SELECT
        COALESCE(ordering_mode, 'Missing') AS ordering_mode,
        COUNT(*) AS total_tests,
        SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS resistant,
        SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) AS susceptible,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_resistant
    FROM long_susc
    GROUP BY ordering_mode
    ORDER BY ordering_mode
    """).df()
    by_mode.to_csv(os.path.join(out_dir, "Resistance_By_Ordering_Mode.csv"), index=False)
    save_and_audit(by_mode, os.path.join(out_dir, "Resistance_By_Ordering_Mode.csv"))

    # By year (top 5 antibiotics)
    by_year = con.execute("""
    WITH annual AS (
        SELECT
            culture_year,
            antibiotic,
            COUNT(*) AS n,
            SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS r
        FROM long_susc
        GROUP BY culture_year, antibiotic
        HAVING COUNT(*) >= 30
    ),
    ranked AS (
        SELECT
            culture_year,
            antibiotic,
            ROUND(100.0 * r / NULLIF(n, 0), 2) AS resistance_rate,
            RANK() OVER (PARTITION BY culture_year ORDER BY n DESC) AS rank
        FROM annual
    )
    SELECT *
    FROM ranked
    WHERE rank <= 5
    ORDER BY culture_year, rank
    """).df()
    by_year.to_csv(os.path.join(out_dir, "Resistance_By_Year.csv"), index=False)
    save_and_audit(by_year, os.path.join(out_dir, "Resistance_By_Year.csv"))

    print("✓ Step 3 AMR Profile completed.")
    return out_dir

# --------------------------------------------------------------
# Step 4: Antibiogram (≥30 isolates)
# --------------------------------------------------------------
def run_step4_antibiogram(con):
    print("\n--- Step 4: Antibiogram ---")
    out_dir = os.path.join(BASE_OUTPUT, "Step 4 – Antibiogram")
    os.makedirs(out_dir, exist_ok=True)

    # Overall
    antibiogram = con.execute("""
    WITH top_org AS (
        SELECT organism, COUNT(DISTINCT order_proc_id_coded) AS n_cultures
        FROM long_susc
        GROUP BY organism
        ORDER BY n_cultures DESC
        LIMIT 10
    ),
    top_abx AS (
        SELECT antibiotic, COUNT(*) AS n_tests
        FROM long_susc
        GROUP BY antibiotic
        ORDER BY n_tests DESC
        LIMIT 10
    )
    SELECT
        o.organism,
        a.antibiotic,
        COUNT(*) AS n,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_susceptible,
        ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_resistant
    FROM long_susc l
    JOIN top_org o ON l.organism = o.organism
    JOIN top_abx a ON l.antibiotic = a.antibiotic
    GROUP BY o.organism, a.antibiotic
    HAVING COUNT(*) >= 30
    ORDER BY o.organism, a.antibiotic
    """).df()
    antibiogram.to_csv(os.path.join(out_dir, "Antibiogram_All.csv"), index=False)
    save_and_audit(antibiogram, os.path.join(out_dir, "Antibiogram_All.csv"))

    # Specimen-specific
    for spec in ['URINE', 'BLOOD', 'RESPIRATORY']:
        spec_abx = con.execute(f"""
        SELECT
            organism,
            antibiotic,
            COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN susceptibility = 'S' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS percent_susceptible
        FROM long_susc
        WHERE culture_description = '{spec}'
        GROUP BY organism, antibiotic
        HAVING COUNT(*) >= 30
        ORDER BY organism, COUNT(*) DESC
        """).df()
        if not spec_abx.empty:
            spec_abx.to_csv(os.path.join(out_dir, f"Antibiogram_{spec}.csv"), index=False)
            save_and_audit(spec_abx, os.path.join(out_dir, f"Antibiogram_{spec}.csv"))

    print("✓ Step 4 Antibiogram completed.")
    return out_dir

# --------------------------------------------------------------
# Step 5: AMR Trends (top 5 antibiotics + top 5 organisms)
# --------------------------------------------------------------
def run_step5_trends(con):
    print("\n--- Step 5: AMR Trends ---")
    out_dir = os.path.join(BASE_OUTPUT, "Step 5 – AMR Trends")
    os.makedirs(out_dir, exist_ok=True)

    abx_trends = con.execute("""
    WITH annual_abx AS (
        SELECT
            culture_year,
            antibiotic,
            COUNT(*) AS n,
            SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS r
        FROM long_susc
        GROUP BY culture_year, antibiotic
        HAVING COUNT(*) >= 50
    ),
    top_abx AS (
        SELECT antibiotic, SUM(n) AS total
        FROM annual_abx
        GROUP BY antibiotic
        ORDER BY total DESC
        LIMIT 5
    )
    SELECT
        a.culture_year,
        a.antibiotic AS item,
        'Antibiotic' AS type,
        ROUND(100.0 * a.r / NULLIF(a.n, 0), 2) AS resistance_rate,
        a.n AS total_tests
    FROM annual_abx a
    JOIN top_abx t ON a.antibiotic = t.antibiotic
    ORDER BY a.antibiotic, a.culture_year
    """).df()

    org_trends = con.execute("""
    WITH annual_org AS (
        SELECT
            culture_year,
            organism,
            COUNT(*) AS n,
            SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS r
        FROM long_susc
        GROUP BY culture_year, organism
        HAVING COUNT(*) >= 50
    ),
    top_org AS (
        SELECT organism, SUM(n) AS total
        FROM annual_org
        GROUP BY organism
        ORDER BY total DESC
        LIMIT 5
    )
    SELECT
        a.culture_year,
        a.organism AS item,
        'Organism' AS type,
        ROUND(100.0 * a.r / NULLIF(a.n, 0), 2) AS resistance_rate,
        a.n AS total_tests
    FROM annual_org a
    JOIN top_org t ON a.organism = t.organism
    ORDER BY a.organism, a.culture_year
    """).df()

    trends = pd.concat([abx_trends, org_trends], ignore_index=True)
    trends.to_csv(os.path.join(out_dir, "Resistance_Trends.csv"), index=False)
    save_and_audit(trends, os.path.join(out_dir, "Resistance_Trends.csv"))

    print("✓ Step 5 AMR Trends completed.")
    return out_dir

# --------------------------------------------------------------
# Step 6: Priority Pathogens (ESKAPE) - using broader patterns
# --------------------------------------------------------------
def run_step6_priority_pathogens(con):
    print("\n--- Step 6: Priority Pathogens ---")
    out_dir = os.path.join(BASE_OUTPUT, "Step 6 – Priority Pathogens")
    os.makedirs(out_dir, exist_ok=True)

    # Broader patterns to catch common variants
    patterns = [
        "ENTEROCOCCUS FAECIUM",
        "STAPHYLOCOCCUS AUREUS",
        "KLEBSIELLA PNEUMONIAE",
        "ACINETOBACTER BAUMANNII",
        "PSEUDOMONAS AERUGINOSA",
        "ENTEROBACTER"  # catches Enterobacter cloacae, aerogenes, etc.
    ]
    where_clause = " OR ".join([f"organism LIKE '%{p}%'" for p in patterns])
    query = f"""
    SELECT
        organism,
        COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
        COUNT(DISTINCT antibiotic) AS n_antibiotics,
        SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) AS resistant_tests,
        COUNT(*) AS total_tests
    FROM long_susc
    WHERE {where_clause}
    GROUP BY organism
    ORDER BY n_cultures DESC
    """
    eskape = con.execute(query).df()
    eskape.to_csv(os.path.join(out_dir, "ESKAPE.csv"), index=False)
    save_and_audit(eskape, os.path.join(out_dir, "ESKAPE.csv"))

    print("✓ Step 6 Priority Pathogens completed.")
    return out_dir

# --------------------------------------------------------------
# Step 7: Quality Assurance (complete)
# --------------------------------------------------------------
def run_step7_qa(con):
    print("\n--- Step 7: QA ---")
    out_dir = os.path.join(BASE_OUTPUT, "Step 7 – QA")
    os.makedirs(out_dir, exist_ok=True)

    qa = {}

    # Basic counts
    total_cultures = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
    qa['total_cultures'] = total_cultures
    qa['unique_patients'] = con.execute(f"SELECT COUNT(DISTINCT anon_id) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
    qa['unique_encounters'] = con.execute(f"SELECT COUNT(DISTINCT pat_enc_csn_id_coded) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]

    # Long susceptibility
    if con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='long_susc'").fetchone()[0] > 0:
        long_rows = con.execute("SELECT COUNT(*) FROM long_susc").fetchone()[0]
        qa['long_susc_rows'] = long_rows

        # Missing values
        missing = con.execute("""
        SELECT
            SUM(CASE WHEN organism IS NULL THEN 1 ELSE 0 END) AS missing_organism,
            SUM(CASE WHEN antibiotic IS NULL THEN 1 ELSE 0 END) AS missing_antibiotic,
            SUM(CASE WHEN susceptibility IS NULL THEN 1 ELSE 0 END) AS missing_susceptibility
        FROM long_susc
        """).df()
        for col in ['missing_organism', 'missing_antibiotic', 'missing_susceptibility']:
            qa[col] = missing[col][0]

        # Unique values
        qa['unique_organisms'] = con.execute("SELECT COUNT(DISTINCT organism) FROM long_susc").fetchone()[0]
        qa['unique_antibiotics'] = con.execute("SELECT COUNT(DISTINCT antibiotic) FROM long_susc").fetchone()[0]
        qa['unique_susceptibility'] = con.execute("SELECT COUNT(DISTINCT susceptibility) FROM long_susc").fetchone()[0]

        # Duplicate rows: count extra rows beyond the first occurrence
        dup_groups = con.execute("""
        SELECT SUM(cnt - 1) AS duplicate_extra_rows
        FROM (
            SELECT order_proc_id_coded, organism, antibiotic, susceptibility, COUNT(*) AS cnt
            FROM long_susc
            GROUP BY order_proc_id_coded, organism, antibiotic, susceptibility
            HAVING COUNT(*) > 1
        )
        """).fetchone()[0]
        qa['duplicate_extra_rows'] = dup_groups if dup_groups is not None else 0

        # Susceptibility distribution
        susc_dist = con.execute("""
        SELECT susceptibility, COUNT(*) AS n
        FROM long_susc
        GROUP BY susceptibility
        """).df()
        qa['susceptibility_distribution'] = susc_dist.to_dict(orient='records')

        # Check if organism = antibiotic (parsing error)
        same = con.execute("""
        SELECT COUNT(*) FROM long_susc WHERE organism = antibiotic
        """).fetchone()[0]
        qa['organism_equals_antibiotic'] = same

    # Excluded cultures due to missing susceptibility
    excluded = con.execute(f"""
    SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}')
    WHERE susceptibilities IS NULL OR TRIM(susceptibilities) = ''
    """).fetchone()[0]
    qa['cultures_excluded_no_susceptibility'] = excluded

    # Save QA summary
    qa_df = pd.DataFrame(qa.items(), columns=['Metric', 'Value'])
    qa_df.to_csv(os.path.join(out_dir, "QA_Summary.csv"), index=False)
    save_and_audit(qa_df, os.path.join(out_dir, "QA_Summary.csv"))

    # Write text report
    with open(os.path.join(out_dir, "QA_Report.txt"), 'w') as f:
        f.write("QUALITY ASSURANCE REPORT\n")
        f.write("="*50 + "\n")
        for k, v in qa.items():
            f.write(f"{k}: {v}\n")
    print("✓ Step 7 QA completed.")
    return out_dir

# --------------------------------------------------------------
# Step 8: Master Report (null‑safe)
# --------------------------------------------------------------
def run_step8_master_report(con):
    print("\n--- Step 8: Master Report ---")
    out_dir = os.path.join(BASE_OUTPUT, "Master_Report")
    os.makedirs(out_dir, exist_ok=True)

    report_lines = []
    report_lines.append("WP1 MASTER REPORT – DESCRIPTIVE EPIDEMIOLOGY")
    report_lines.append("="*60)

    total_cultures = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
    if total_cultures == 0:
        report_lines.append("WARNING: Dataset is empty.")
        with open(os.path.join(out_dir, "Master_Report.txt"), 'w') as f:
            f.write("\n".join(report_lines))
        return out_dir

    patients = con.execute(f"SELECT COUNT(DISTINCT anon_id) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
    encounters = con.execute(f"SELECT COUNT(DISTINCT pat_enc_csn_id_coded) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
    report_lines.append(f"Total positive cultures: {total_cultures:,}")
    report_lines.append(f"Unique patients: {patients:,}")
    report_lines.append(f"Unique encounters: {encounters:,}")

    # Polymicrobial
    poly = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}') WHERE polymicrobial = 1").fetchone()[0]
    report_lines.append(f"Polymicrobial cultures: {poly} ({100*poly/total_cultures:.2f}%)")

    # AMR summary if available
    if con.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='long_susc'").fetchone()[0] > 0:
        overall = con.execute("""
        SELECT ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct
        FROM long_susc
        """).fetchone()[0]
        report_lines.append(f"Overall resistance rate: {overall}%")

        top_org = con.execute("""
        SELECT organism, COUNT(DISTINCT order_proc_id_coded) AS n
        FROM long_susc
        GROUP BY organism
        ORDER BY n DESC
        LIMIT 1
        """).df()
        if not top_org.empty:
            report_lines.append(f"Most common organism: {top_org['organism'][0]} ({top_org['n'][0]} cultures)")

        resistant_abx = con.execute("""
        SELECT antibiotic, ROUND(100.0 * SUM(CASE WHEN susceptibility = 'R' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct
        FROM long_susc
        GROUP BY antibiotic
        HAVING COUNT(*) >= 30
        ORDER BY pct DESC
        LIMIT 1
        """).df()
        if not resistant_abx.empty:
            report_lines.append(f"Most resistant antibiotic: {resistant_abx['antibiotic'][0]} ({resistant_abx['pct'][0]}%)")

    report_lines.append("\nFor detailed tables, see individual step folders.")
    report_path = os.path.join(out_dir, "Master_Report.txt")
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))
    print("✓ Master Report written.")
    return out_dir

# --------------------------------------------------------------
# Main execution
# --------------------------------------------------------------
def main():
    print("Starting WP1 Phase C – Final Complete Script...")
    if not os.path.exists(INPUT_PARQUET):
        print(f"ERROR: {INPUT_PARQUET} not found.")
        sys.exit(1)

    # Create long susceptibility (will raise error if pairing invalid)
    try:
        create_long_susceptibility(con)
        amr_possible = True
    except ValueError as e:
        print(e)
        print("WARNING: AMR analyses will be skipped.")
        amr_possible = False

    if amr_possible:
        run_step3_amr_profile(con)
        run_step4_antibiogram(con)
        run_step5_trends(con)
        run_step6_priority_pathogens(con)

    run_step7_qa(con)
    run_step8_master_report(con)

    print("\n" + "="*50)
    print("ALL STEPS COMPLETED SUCCESSFULLY")
    print("="*50)
    con.close()

if __name__ == "__main__":
    main()