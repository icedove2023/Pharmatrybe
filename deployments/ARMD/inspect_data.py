import duckdb

con = duckdb.connect()

df = con.execute("""
SELECT
    order_proc_id_coded,
    organisms,
    antibiotics,
    susceptibilities
FROM read_parquet('output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet')
LIMIT 10
""").df()

print(df)