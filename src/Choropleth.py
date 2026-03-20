import os
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt

visualizations_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'visualizations'))
if not os.path.exists(visualizations_path):
    os.makedirs(visualizations_path)

df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'personas_censo2024.csv'), sep=";", usecols=["id_persona", "comuna"])
geodata = gpd.read_file(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'Comunas', 'comunas.shp'))

personas_por_comuna = df.groupby("comuna").size().reset_index(name="count")
personas_por_comuna = geodata.merge(personas_por_comuna, left_on="cod_comuna", right_on="comuna")

random_selection = np.random.choice(personas_por_comuna["Region"])
data_region = personas_por_comuna[personas_por_comuna['Region'] == random_selection]

if random_selection == "Región de Valparaíso":
    islas = ["Isla de Pascua", "Juan Fernández"]
    continental = data_region[~data_region["Comuna"].isin(islas)]
    data_region = continental

fig, ax = plt.subplots(figsize=(10, 10))
data_region.plot(
    ax=ax,
    column="count",
    cmap='Purples',
    legend=True,
    edgecolor='black',
)
plt.title(random_selection)
ax.set_xticks([])
ax.set_yticks([])

plt.savefig(os.path.join(visualizations_path," Choroplet"))

data_region = data_region.to_crs(epsg=4326)     #Para usar plotly es necesario pasar a formato estandar de referenciación
data_region = data_region.set_index("Comuna")

fig = px.choropleth(
    data_region,
    geojson=data_region.geometry,
    locations=data_region.index,
    projection="mercator",
    color="count",
    title= random_selection,
    hover_data={"count": True},
    color_continuous_scale="purples" # https://masamasace.github.io/plotly_color/
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_traces(hovertemplate="%{location}\n <br>Población: %{customdata[0]}")
fig.update_layout(width=900, height=700)

fig.write_html(os.path.join(visualizations_path, " Choroplet.html"))
