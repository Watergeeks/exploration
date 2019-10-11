import os
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
import plotly.express as px

# load data
df = pd.read_csv("data/eau_potable_production.csv")

# rename column headers
df = df.rename(columns={
    "Région administrative": "region",
    "Nom de la municipalité": "municipality", 
    "Numéro de l'installation de production": "installation_code",
    "Nom de l'installation de production d'eau potable": "installation_name",
    "Procédé de traitement": "process"
})

# TODO: delete after testing with smaller daf 
df = df[:5]
print(df)

# initialize geolocator
geolocator = Nominatim(user_agent="my-application")

# get coordinates
df["coordinates"] = df["municipality"].apply(lambda x: geolocator.geocode(x + ", Quebec"))
df["latitide"] = df["coordinates"].apply(lambda x: x.latitude if x != None else None)
df["longitude"] = df["coordinates"].apply(lambda x: x.longitude if x != None else None)

# rearrange columns for next step
df = df[["region", "municipality", "installation_name", "installation_code", "latitide", "longitude", "process"]]
print(df)

# create new dataframe to handle processes as individual data points
new_list = []
for index, row in df.iterrows():
    new_row = row.tolist()
    if type(row["process"]) is str:
        for p in row["process"].split("\n"):
            new_row.pop() # TODO: need to remove element at certain index after adding coordinates?
            new_row.append(p)
            new_list.append(new_row)
    else:
        new_row.pop()
        new_row.append("n/a")
        new_list.append(new_row)
new_df = pd.DataFrame(new_list, columns=list(df.columns))
print(new_df)

# define colors to depend on process
colors = {
    "Chloration": "#3498DB",
    "Filtration": "#E74C3C",
    "Ultraviolet": "#9B59B6",
    "Ozonation": "#17A589",
    "Charbon": "#E67E22",
    "n/a": "#000000"
}
new_df["color"] = new_df["process"].apply(lambda x: colors[x])

# define size of data point
new_df["size"] = 0.2
print(new_df)

# define map figure
fig = px.scatter_mapbox(
    new_df, 
    lat = "latitide", 
    lon = "longitude", 
    # hover_name = "municipality", 
    hover_data = ["region", "municipality", "installation_name", "installation_code", "process"],
    color = "color", 
    # mode = "markers",
    # marker = go.scattermapbox.Marker(size=14),
    # size = "size",
    zoom = 4, 
    height = 800
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":20,"l":20,"b":20})
fig.show()
