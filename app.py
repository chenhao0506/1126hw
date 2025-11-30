import duckdb
import pandas as pd
import solara

# -----------------------------
# 1. 讀取資料
# -----------------------------
url = "https://data.gishub.org/duckdb/cities.csv"

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")

df = con.sql(f"""
    SELECT name, country, latitude, longitude, population
    FROM '{url}'
    WHERE population IS NOT NULL
""").df()

# 取得國家列表
country_list = sorted(df["country"].unique())

# -----------------------------
# 2. Solara Reactive 狀態
# -----------------------------
selected_country = solara.reactive(country_list[0])
min_population = solara.reactive(0)

# -----------------------------
# 3. Solara App 主頁
# -----------------------------
@solara.component
def Page():

    with solara.Column(gap="20px"):
        solara.Markdown("# 📊 城市資料表格")

        # 選國家
        solara.Select(
            label="請選擇國家",
            values=country_list,
            value=selected_country
        )

        # 滑動尺標篩人口
        solara.SliderInt(
            "人口最少",
            min=0,
            max=50_000_000,
            value=min_population
        )

    # 篩選資料
    filtered_data = df[
        (df["country"] == selected_country.value) &
        (df["population"] >= min_population.value)
    ].reset_index(drop=True)

    # 顯示表格
    solara.Markdown(f"### 📋 數據表格 (共 {len(filtered_data)} 個城市)")
    solara.DataFrame(filtered_data)
