import duckdb
import pandas as pd
import leafmap.maplibregl as leafmap
import solara

url = "https://data.gishub.org/duckdb/cities.csv"
leafmap.download_file(url, unzip=True)
con = duckdb.connect("nyc_data.db")
# 為新建立的connection再安裝和載入 spatial (用於空間資料處理)
con.install_extension("spatial")
con.load_extension("spatial")



con.sql("""
SELECT name, population
FROM "https://data.gishub.org/duckdb/cities.csv"
WHERE country = "Country"
ORDER BY population DESC
LIMIT 10;
""").show()