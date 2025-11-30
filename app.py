# app.py
import duckdb
import pandas as pd
import solara
import plotly.express as px
import plotly.io as pio

url = "https://data.gishub.org/duckdb/cities.csv"

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")

df = con.sql(f"""
    SELECT name, country, latitude, longitude, population
    FROM '{url}'
    WHERE population IS NOT NULL
""").df()

country_list = sorted(df["country"].unique())
selected_country = solara.reactive(country_list[0])
min_population = solara.reactive(0)

@solara.component
def Page():
    with solara.Column(gap="20px"):
        solara.Markdown("# 🌍 國家城市數據儀表板")

        solara.Select(
            label="請選擇國家",
            values=country_list,
            value=selected_country
        )

        solara.SliderInt(
            "人口最少",
            min=0,
            max=50_000_000,
            value=min_population
        )

    filtered_data = df[
        (df["country"] == selected_country.value) &
        (df["population"] >= min_population.value)
    ].reset_index(drop=True)

    solara.Markdown(f"### 📋 數據表格 (共 {len(filtered_data)} 個城市)")
    solara.DataFrame(filtered_data)

    if not filtered_data.empty:
        with solara.Row():
            fig_hist = px.histogram(
                filtered_data,
                x="population",
                nbins=20,
                title=f"{selected_country.value} 城市人口分布",
                labels={"population": "人口數"}
            )
            solara.HTML(pio.to_html(fig_hist, include_plotlyjs='cdn'), style={"width":"50%","height":"400px"})

            fig_pie = px.pie(
                filtered_data,
                names="name",
                values="population",
                title=f"{selected_country.value} 各城市人口比例"
            )
            solara.HTML(pio.to_html(fig_pie, include_plotlyjs='cdn'), style={"width":"50%","height":"400px"})

# ✅ 直接呼叫 Page() 啟動
Page()
