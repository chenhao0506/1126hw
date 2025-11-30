import duckdb
import pandas as pd
import solara
import leafmap.maplibregl as leafmap

# -----------------------------
# 1. 資料處理
# -----------------------------
url = "https://data.gishub.org/duckdb/cities.csv"

# 建立連線並讀取資料
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

# 為了選單排序，取得城市列表
city_list = sorted(df["name"].unique())

# -----------------------------
# 2. Solara Reactive 狀態
# -----------------------------
# 預設選取第一個城市
selected_city = solara.reactive(city_list[0])

# -----------------------------
# 3. Solara App 主頁
# -----------------------------
@solara.component
def Page():
    
    # --- 版面區塊 1：標題與選單 (置頂) ---
    with solara.Column(gap="20px"):
        solara.Markdown("# 🌍 城市互動地圖 (Esri 衛星圖)")
        
        # 將選單放在最上方，不使用 Sidebar
        solara.Select(
            label="請選擇城市：",
            values=city_list,
            value=selected_city
        )

    # --- 資料計算 ---
    # 根據選單找出該城市的資料
    city_data = df[df["name"] == selected_city.value].iloc[0]
    
    lat = float(city_data['latitude'])
    lng = float(city_data['longitude'])
    pop = city_data['population']
    name = city_data['name']

    # --- 版面區塊 2：城市資訊 ---
    # 使用 Card 讓資訊看起來更整潔
    with solara.Card(name):
        solara.Markdown(f"""
        - **國家**：{city_data['country']}
        - **人口**：{int(pop):,}
        - **座標**：{lat:.4f}, {lng:.4f}
        """)

    # --- 版面區塊 3：地圖 (關鍵修復部分) ---
    # 這裡直接建立地圖，每次 city 改變時，因為是 reactive，這裡會重新渲染
    
    # 1. 初始化地圖，中心點設為選中城市，Zoom 放大一點以便觀察
    m = leafmap.Map(
        center=[lat, lng],
        zoom=10,
        style="streets", # maplibregl 預設樣式
        height="600px"   # ❗重要：設定高度，否則有時會顯示不出來
    )
    
    # 2. 加入 Esri 衛星底圖
    m.add_basemap("Esri.WorldImagery")

    # 3. 加入該城市的標記 (只加這一個，效能最好)
    m.add_marker(
        lng, 
        lat, 
        popup=f"{name}<br>人口：{int(pop):,}",
        options={"color": "red"}
    )

    # 4. ❗最重要的一步：將地圖顯示出來
    # 在 Solara 中，maplibregl 的物件可以直接被渲染
    m.element()