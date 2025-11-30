import duckdb
import pandas as pd
import solara
import leafmap
from ipyleaflet import Marker, Icon # ⭐ 導入 Marker 和 Icon 類別

# -----------------------------
# 1. 資料處理 (不變)
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
# 2. Solara Reactive 狀態 (不變)
# -----------------------------
selected_city = solara.reactive(city_list[0])

# -----------------------------
# 3. Solara App 主頁
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

    # --- 地圖區塊 (Marker 修正) ---
    
    m = leafmap.Map(
        center=[lat, lng],
        zoom=10,
        height="600px"
    )
    
    m.add_basemap("Esri.WorldImagery")

    # ⭐ 替換為 add_marker 並使用紅色圖示
    # Leafmap 預設使用 ipyleaflet，我們可以利用 ipyleaflet 的 Marker 類別
    
    # 創建一個標準的紅色 Marker 圖示
    marker_icon = Icon(
        icon_url='https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadow_url='https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        icon_size=[25, 41],
        icon_anchor=[12, 41],
        popup_anchor=[1, -34],
        shadow_size=[41, 41]
    )

    # 創建 Marker 物件
    marker = Marker(
        location=[lat, lng],  # [緯度, 經度]
        icon=marker_icon,
        popup=f"<b>{name}</b><br>人口：{int(pop):,}"
    )

    # 將 Marker 加入地圖
    m.add_layer(marker)
    
    # 顯示地圖
    m.element()