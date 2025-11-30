import duckdb
import pandas as pd
import solara
import leafmap  # ⭐ 改回使用標準 leafmap (ipyleaflet backend)

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

city_list = sorted(df["name"].unique())

# -----------------------------
# 2. Solara Reactive 狀態
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
    
    # 確保轉換為 Python 原生 float，避免 numpy 類型造成錯誤
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

    # --- 版面區塊 3：地圖 (修復版) ---
    
    # 1. 建立地圖
    # 使用標準 leafmap，center 格式為 [lat, lng]
    m = leafmap.Map(
        center=[lat, lng],
        zoom=10,
        height="600px"
    )
    
    # 2. 設定 Esri 衛星底圖
    # 標準版 leafmap 可以直接用這行指令
    m.add_basemap("Esri.WorldImagery")

    # 3. 加入標記
    # ⭐ 注意：標準版 leafmap 的 add_marker 參數不同
    # location=[lat, lng] (緯度在前)
    # 為了避免 icon 路徑問題，這裡改用 add_circle_marker，這也比較容易自訂顏色
    m.add_circle_marker(
        location=[lat, lng],
        radius=10,
        color="red",
        fill_color="red",
        fill_opacity=0.7,
        popup=f"<b>{name}</b><br>人口：{int(pop):,}"
    )

    # 4. 顯示地圖
    m.element()