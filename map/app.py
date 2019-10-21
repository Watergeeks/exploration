import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State, Input, Output

app = dash.Dash(
    __name__,
    meta_tags = [
        {"name": "viewport", "content": "width = device-width, initial-scale = 1.0"}
    ],
)

# for gunicorn
server = app.server

# for mapbox # TODO: fix mapbox styling and figure out how to access style properly
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

# define theme colors
COLORS = {
    "theme": {
        "white": "#F3F6FA",
        "grey1": "#707070",
        "grey2": "#1E1E1E",
        "orange": "#DD8600", #DD8600 vs #E67E22
        "yellow": "#FEC036", #FEC036 vs #D1A622
    },
    "map": [
        "#9B59B6", #purple
        "#3498DB", #blue
        "#33ccbb" #teal
        "#33cc88", #teal/green
        "#44cc33" #green
        "#CCDD33" #green/yellow
        "#FEC036", #yellow
        "#DD8600", #orange
        "#E74C3C", #red
    ]
}

# load data
df = {
    "water": pd.read_csv("data/water_temp.csv"),
    "wastewater": pd.read_csv("data/wastewater_temp.csv")
}

# define colors to depend on process
def get_colors(df):
    processes = set(df["process_code"].tolist())
    colors = {"None": "#FFFFFF"}
    for i, p in enumerate(processes):
        colors[p] = COLORS["map"][i]
    return colors
colors_water = get_colors(df["water"])
colors_wastewater = get_colors(df["wastewater"])
df["water"]["color"] = df["water"]["process_code"].apply(lambda x: colors_water[x])
df["wastewater"]["color"] = df["wastewater"]["process_code"].apply(lambda x: colors_wastewater[x])

def get_process_dropdown_items(df):
    processes = df[["process_code", "process_name"]].drop_duplicates()
    processes = processes.rename(columns = {"process_name": "label", "process_code": "value"})
    processes = processes.to_dict('records')
    return(processes)

# define size of data point
df["water"]["size"] = 10
df["wastewater"]["size"] = 10

side_panel_layout = html.Div(
    id = "panel-left",
    children = [
        html.H1(children = "WATERGEEKS"),
        html.Div(
            children = [
                html.Br(),
                html.H2(children = "Choose type of plant"), 
                html.Div(
                    className = "dropdown", 
                    children = dcc.Dropdown(
                        id = "plant-type",
                        className = "dropdown-component", # TODO: remove this?
                        options = [
                            {"label": "Water / Eau potable", "value": "water"},
                            {"label": "Wastewater / Eau usées", "value": "wastewater"},
                        ],
                        clearable = False,
                        value = "water",
                    )
                ),
                html.Br(),
                html.H2(children = "Choose type(s) of treatment"), 
                html.Div(
                    className = "radio-items",
                    children = dcc.RadioItems(
                        id = "sort-type",
                        options = [
                            {'label': 'See plants with ALL of the following', 'value': 'AND'},
                            {'label': 'See plants with ANY of the following', 'value': 'OR'},
                        ],
                        value = 'OR',
                        labelStyle = {'display': 'block'}
                    ) 
                ),
                html.Br(),
                html.Div(
                    className = "dropdown", # TODO: generate dropdown list for processes
                    children = dcc.Dropdown(
                        id = "treatment-type",
                        className = "dropdown-component", # TODO: remove this?
                        options = get_process_dropdown_items(df["water"]),
                        clearable = True,
                        multi = True,
                        value = None,
                    )
                )
            ]
        )
    ]
)

main_panel_layout = html.Div(
    id = "panel-right",
    children = [
        html.Div(
            id = "world-map-wrapper",
            children = [
                dcc.Graph(
                    id = "world-map",
                    figure = {
                        "data": [
                            {
                                "type": "scattermapbox",
                                "lat": df["water"]["latitude"],
                                "lon": df["water"]["longitude"],
                                "mode": "markers",
                                #"hoverinfo": "text+lon+lat",
                                #"text": df["water"]["municipality_name"],
                                #"textposition": "bottom right",
                                #"hoverdata": df["water"][["region_name", "municipality_name", "process_name"]],
                                "marker": {
                                    "size": df["water"]["size"], 
                                    "color": df["water"]["color"]
                                },
                            },
                        ],
                        "layout": {
                            "hovermode": "closest",
                            "mapbox": {
                                "accesstoken": MAPBOX_ACCESS_TOKEN,
                                #"style": open("assets/style.json", "r"),
                                "style": MAPBOX_STYLE,
                                "center": {"lat": 55, "lon": -71},
                                "zoom": 4,
                            },
                            "showlegend": False,
                            "autosize": True,
                            "margin": {"t": 0, "r": 0, "b": 0, "l": 0},
                        }
                    },
                    config = {
                        "displayModeBar": False, 
                        "scrollZoom": True
                    },
                ),
            ],
        ),
    ],
)

# define app layout
app.layout = html.Div(
    id = "root",
    children = [
        side_panel_layout,
        main_panel_layout
    ],
)

@app.callback(
    [
        Output("world-map", "figure"),
        Output("treatment-type", "options")
    ],
    [
        Input("plant-type", "value"),
        Input("sort-type", "value"),
        Input("treatment-type", "value"),
    ],
    [
        State("world-map", "figure")
    ],
)
def update_word_map(plant, sort, treatment, old_figure):
    figure = old_figure
    # switch between water and wastewater data
    if plant == "water":
        data = df["water"]
    else:
        data = df["wastewater"]
    # fix options in dropdown list processes
    options = get_process_dropdown_items(data)
    # filter data according to process
    if treatment != None:
        if sort == "ALL":
            data = data.loc[data['process_code'].isin(treatment)]
        else:
            data = data.loc[data['process_code'].isin(treatment)]
    figure["data"] = [
        {
            "type": "scattermapbox",
            "lat": data["latitude"],
            "lon": data["longitude"],
            "hoverinfo": "text+lon+lat",
            "mode": "markers",
            "marker": {
                "size": data["size"], 
                "color": data["color"]
            },
        },
    ]
    return figure, options

if __name__ == "__main__":
    app.run_server(debug = True)