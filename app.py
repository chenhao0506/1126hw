import duckdb
import pandas as pd
import solara
import leafmap.maplibregl as leafmap

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
# 3. 地圖函式
# -----------------------------
def create_country_map(country, population_min):
    filtered = df[(df["country"] == country) & (df["population"] >= population_min)]

    if filtered.empty:
        center = [20, 0]
        zoom = 2
    else:
        center = [filtered["latitude"].mean(), filtered["longitude"].mean()]
        zoom = 4

    m = leafmap.Map(center=center, zoom=zoom, height="600px")
    m.add_basemap("Esri.WorldImagery")

    # 建立 marker list
    markers = []
    for _, row in filtered.iterrows():
        markers.append({
            "coordinates": [row["longitude"], row["latitude"]],
            "popup": f"<b>{row['name']}</b><br>人口：{int(row['population']):,}",
            "color": "red"
        })

    # ✅ 批量加入
    if markers:
        m.add_markers(markers)  # 注意 add_markers() 才能接受 list

    return m, filtered

# -----------------------------
# 4. Solara App 主頁
# -----------------------------
@solara.component
def Page():

    with solara.Column(gap="20px"):
        solara.Markdown("# 🌍 國家城市互動地圖 (Esri 衛星圖)")

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

    # --- 顯示地圖 + 篩選後資料 ---
    m, filtered_data = create_country_map(selected_country.value, min_population.value)
    m.to_streamlit()  # 顯示地圖

    # --- 顯示資料表格 ---
    solara.Markdown(f"### 📋 數據表格 (共 {len(filtered_data)} 個城市)")
    solara.DataFrame(filtered_data.reset_index(drop=True))