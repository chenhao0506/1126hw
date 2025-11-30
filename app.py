import duckdb
import pandas as pd
import solara
import leafmap.maplibregl as leafmap


# -----------------------------
# 1. 直接從網路讀取資料（避免 PermissionError）
# -----------------------------
url = "https://data.gishub.org/duckdb/cities.csv"

con = duckdb.connect()  # in-memory DB
con.install_extension("spatial")
con.load_extension("spatial")

df = con.sql(f"""
    SELECT 
        name,
        country,
        latitude,
        longitude,
        population
    FROM '{url}'
""").df()

city_list = sorted(df["name"].unique())


# -----------------------------
# 2. Solara reactive 狀態
# -----------------------------
selected_city = solara.reactive(city_list[0])
min_population = solara.reactive(0)


# -----------------------------
# 3. 建立地圖（使用正確的 maplibregl API）
# -----------------------------
def create_map(city, population_min):

    # ❗ MapLibre 不支援 basemap=，只能先建立 Map 再 add_basemap
    m = leafmap.Map(
        center=[20, 0],
        zoom=2
    )
    m.add_basemap("Esri.WorldImagery")  # ⭐ 預設底圖

    filtered = df[df["population"] >= population_min]

    for _, row in filtered.iterrows():
        lng = float(row["longitude"])
        lat = float(row["latitude"])

        # 選到的城市顯示另一種顏色
        if row["name"] == city:
            marker_color = "red"
        else:
            marker_color = "blue"

        # ⭐ 正確寫法：add_marker(lng, lat, ...)
        m.add_marker(
            lng,
            lat,
            popup=f"{row['name']}<br>人口：{row['population']:,}",
            options={"color": marker_color}
        )

    return m


# -----------------------------
# 4. Solara App 主頁
# -----------------------------
@solara.component
def Page():

    solara.Markdown("# 🌍 城市互動地圖（Esri 衛星圖 + DuckDB）")

    # 側邊欄
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

    # 顯示選定城市資訊
    city_info = df[df["name"] == selected_city.value].iloc[0]

    solara.Markdown(f"""
    ## {city_info['name']}
    - 國家：{city_info['country']}
    - 人口：{city_info['population']:,}
    - 經度：{city_info['longitude']}
    - 緯度：{city_info['latitude']}
    """)
