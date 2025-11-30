import duckdb
import pandas as pd
import solara
import plotly.express as px

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
        solara.Markdown("# 📊 國家城市數據儀表板")

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

    # -----------------------------
    # 4. 直方圖 + 圓餅圖
    # -----------------------------
    if not filtered_data.empty:
        with solara.Row():
            # 左邊：人口直方圖
            fig_hist = px.histogram(
                filtered_data,
                x="population",
                nbins=20,
                title=f"{selected_country.value} 城市人口分布",
                labels={"population": "人口數"}
            )
            fig_hist.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            solara.Plotly(fig_hist, height=400, width=500)

            # 右邊：人口比例圓餅圖
            fig_pie = px.pie(
                filtered_data,
                names="name",
                values="population",
                title=f"{selected_country.value} 各城市人口比例"
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            solara.Plotly(fig_pie, height=400, width=500)
