import duckdb

con = duckdb.connect("armd.db")

print("DuckDB version:", duckdb.__version__)

print(con.execute("""
DESCRIBE
SELECT *
FROM read_csv_auto('microbiology_cultures_cohort.csv');
""").fetchdf())