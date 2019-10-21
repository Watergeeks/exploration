import os
import pandas as pd
from geopy.geocoders import Nominatim

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

# initialize dash app
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

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
df["latitude"] = df["coordinates"].apply(lambda x: x.latitude if x != None else None)
df["longitude"] = df["coordinates"].apply(lambda x: x.longitude if x != None else None)

# rearrange columns for next step
df = df[["region", "municipality", "installation_name", "installation_code", "latitude", "longitude", "process"]]
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
new_df["size"] = 1.5
print(new_df)

# define dash app layout
app.layout = html.Div(
    children = [
        html.Div(
            className="eight columns",
            children=[
                dcc.Graph(
                    id = 'map',
                    figure = {
                        'data': [{
                            'lat': new_df['latitude'],
                            'lon': new_df['longitude'],
                            'type': 'scattermapbox',
                            'mode': 'markers',
                            # 'color': new_df['color'], 
                            # 'hover_data': ["region", "municipality", "installation_name", "installation_code", "process"],
                            'marker': {
                                'size': new_df['size'],
                                'sizeref': 0.1,
                                'sizemin': 1,
                                'sizemode': 'diameter',
                            },
                            # 'selectedpoints': selected_indices,
                            # 'selected': {
                            #     'marker': {'color': '#85144b'}
                            # }
                        }],
                        'layout': {
                            'mapbox_style': 'open-street-map',
                            'mapbox': {
                                'center': {
                                    'lat': 45.5017,
                                    'lon': -73.5673
                                },
                                'zoom': 5,
                                'accesstoken': mapbox_access_token
                            },
                            'margin': {'r': 20, 'l': 20, 't': 20, 'b': 20}
                        }
                    }
                ),
                html.Div(
                    children=[
                        "TABLE"
                    ]
                )
            ]
        )
    ]
)

# run dash app
if __name__ == "__main__":
    app.run_server(debug=True)