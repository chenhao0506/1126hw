import duckdb
import pandas as pd
import solara
import leafmap.maplibregl as leafmap

# -----------------------------
# 1. 資料處理
# -----------------------------
url = "https://data.gishub.org/duckdb/cities.csv"

con = duckdb.connect()
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
    WHERE population IS NOT NULL
""").df()

city_list = sorted(df["name"].unique())

# -----------------------------
# 2. Solara Reactive
# -----------------------------
selected_city = solara.reactive(city_list[0])

# -----------------------------
# 3. 地圖函式
# -----------------------------
def create_map(lat, lng, name, pop):
    m = leafmap.Map(center=[lat, lng], zoom=10, height="600px")
    m.add_basemap("Esri.WorldImagery")
    
    # MapLibre 正確寫法：add_marker(lng, lat)
    m.add_marker(
        lng,
        lat,
        popup=f"<b>{name}</b><br>人口：{int(pop):,}",
        options={"color": "red"}
    )
    return m

# -----------------------------
# 4. Solara App 主頁
# -----------------------------
@solara.component
def Page():
    
    with solara.Column(gap="20px"):
        solara.Markdown("# 🌍 城市互動地圖 (Esri 衛星圖)")
        
        solara.Select(
            label="請選擇城市：",
            values=city_list,
            value=selected_city
        )

    # --- 資料計算 ---
    city_data = df[df["name"] == selected_city.value].iloc[0]
    
    lat = float(city_data['latitude'])
    lng = float(city_data['longitude'])
    pop = city_data['population']
    name = city_data['name']

    with solara.Card(name):
        solara.Markdown(f"""
        - **國家**：{city_data['country']}
        - **人口**：{int(pop):,}
        - **座標**：{lat:.4f}, {lng:.4f}
        """)

    # --- 地圖 ---
    m = create_map(lat, lng, name, pop)
    m.to_streamlit()  # Solara 中顯示 MapLibre 地圖
