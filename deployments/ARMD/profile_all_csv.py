import duckdb
import pandas as pd
from pathlib import Path

# -----------------------------
# SETTINGS
# -----------------------------

DATA_FOLDER = Path("data")
REPORT_FOLDER = Path("reports")

REPORT_FOLDER.mkdir(exist_ok=True)

con = duckdb.connect()


# -------------------------------------------------------
# Profile one CSV
# -------------------------------------------------------

def profile_csv(csv_file):

    table = "t"

    print("=" * 80)
    print(csv_file.name)
    print("=" * 80)

    con.execute(f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT *
        FROM read_csv_auto(
        '{csv_file.as_posix()}',
        sample_size=-1
    );
    """)

    report = []

    # --------------------------------------------------
    # Basic information
    # --------------------------------------------------

    rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    cols = con.execute(f"""
        DESCRIBE {table}
    """).fetchdf()

    report.append(f"# {csv_file.name}\n")
    report.append(f"Rows : {rows:,}")
    report.append(f"Columns : {len(cols)}")
    report.append("")

    # --------------------------------------------------
    # Column profiling
    # --------------------------------------------------

    for _, c in cols.iterrows():

        name = c["column_name"]
        dtype = c["column_type"]

        report.append("=" * 60)
        report.append(name)
        report.append(f"Type : {dtype}")

        # ---------------------------
        # Missing values
        # ---------------------------

        nulls = con.execute(f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE "{name}" IS NULL
        """).fetchone()[0]

        report.append(f"NULL values : {nulls:,}")

        # ---------------------------
        # Distinct values
        # ---------------------------

        distinct = con.execute(f"""
            SELECT COUNT(DISTINCT "{name}")
            FROM {table}
        """).fetchone()[0]

        report.append(f"Distinct values : {distinct:,}")

        # ------------------------------------------------
        # VARCHAR columns
        # ------------------------------------------------

        if "VARCHAR" in dtype.upper():

            report.append("\nTop 20 Values")

            try:

                values = con.execute(f"""
                    SELECT "{name}",
                           COUNT(*) AS Frequency
                    FROM {table}
                    GROUP BY "{name}"
                    ORDER BY Frequency DESC
                    LIMIT 20
                """).fetchdf()

                report.append(values.to_string(index=False))

            except:
                pass

        # ------------------------------------------------
        # Numeric columns
        # ------------------------------------------------

        elif any(x in dtype.upper() for x in
                 ["BIGINT","INTEGER","DOUBLE","FLOAT","DECIMAL"]):

            try:

                stats = con.execute(f"""
                    SELECT
                        MIN("{name}") as Min,
                        MAX("{name}") as Max,
                        AVG("{name}") as Mean,
                        MEDIAN("{name}") as Median
                    FROM {table}
                """).fetchdf()

                report.append("\nStatistics")
                report.append(stats.to_string(index=False))

                # ------------------------
                # Top frequencies
                # ------------------------

                freq = con.execute(f"""
                    SELECT "{name}",
                           COUNT(*) Frequency
                    FROM {table}
                    GROUP BY "{name}"
                    ORDER BY Frequency DESC
                    LIMIT 20
                """).fetchdf()

                report.append("\nTop Values")
                report.append(freq.to_string(index=False))

            except:
                pass

        # ------------------------------------------------
        # Timestamp columns
        # ------------------------------------------------

        elif "TIMESTAMP" in dtype.upper():

            try:

                dates = con.execute(f"""
                    SELECT
                        MIN("{name}") as Earliest,
                        MAX("{name}") as Latest
                    FROM {table}
                """).fetchdf()

                report.append(dates.to_string(index=False))

            except:
                pass

        report.append("\n")

    # ---------------------------------------------------
    # Save report
    # ---------------------------------------------------

    output = REPORT_FOLDER / f"{csv_file.stem}_profile.txt"

    with open(output, "w", encoding="utf-8") as f:

        f.write("\n".join(report))

    print(f"Saved -> {output}")


# -------------------------------------------------------
# Process all CSVs
# -------------------------------------------------------

files = sorted(DATA_FOLDER.glob("*.csv"))

for f in files:
    profile_csv(f)

print("\nFinished.")