import duckdb
import pandas as pd
import solara
import leafmap.maplibregl as leafmap


# -----------------------------
# 1. 載入資料
# -----------------------------
url = "https://data.gishub.org/duckdb/cities.csv"

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")

df = con.sql("""
    SELECT 
        name,
        country,
        latitude,
        longitude,
        population
    FROM "https://data.gishub.org/duckdb/cities.csv"
""").df()

city_list = sorted(df["name"].unique())


# -----------------------------
# 2. 建立 Solara Reactive 參數
# -----------------------------
selected_city = solara.reactive(city_list[0])
min_population = solara.reactive(0)


# -----------------------------
# 3. 做地圖（預設 Esri.WorldImagery）
# -----------------------------
def create_map(city, population_min):
    # ⭐ 不載入 OSM，直接指定預設底圖（你的要求）
    m = leafmap.Map(
        center=[20, 0],
        zoom=2,
        basemap="Esri.WorldImagery"
    )

    filtered = df[df["population"] >= population_min]

    for _, row in filtered.iterrows():
        color = "red" if row["name"] == city else "blue"
        m.add_marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"{row['name']}<br>人口：{row['population']}",
            color=color
        )

    return m


# -----------------------------
# 4. Solara App 主體
# -----------------------------
@solara.component
def Page():
    solara.Markdown("# 🌍 城市互動地圖（Esri 衛星圖）")

    with solara.Sidebar():
        solara.Markdown("### 設定選項")
        solara.Select(
            label="選擇城市",
            values=city_list,
            value=selected_city
        )
        solara.SliderInt(
            "人口最少",
            min=0,
            max=50_000_000,
            value=min_population
        )

    city_info = df[df["name"] == selected_city.value].iloc[0]

    # 資訊顯示區 + 地圖
    with solara.Column():
        solara.Markdown(f"""
        ## {city_info['name']}
        - 國家：{city_info['country']}
        - 人口：{city_info['population']:,}
        - 經度：{city_info['longitude']}
        - 緯度：{city_info['latitude']}
        """)

        m = create_map(selected_city.value, min_population.value)
        m.to_streamlit()  # Solara 4+ 的標準顯示方式
