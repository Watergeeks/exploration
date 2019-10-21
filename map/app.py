import pandas as pd
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State, Input, Output
from generate_colors import generate_colors

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
    "white": "#F3F6FA",
    "grey": "#707070",
    "dark1": "#1E1E1E",
    "dark2": "#2b2b2b",
    "orange": "#DD8600", #DD8600 vs #E67E22
    "yellow": "#FEC036", #FEC036 vs #D1A622
}

# load data
df = {
    "water": pd.read_csv("data/water_temp.csv"),
    "wastewater": pd.read_csv("data/wastewater_temp.csv")
}

# define colors to depend on process
def get_colors(df):
    processes = set(df["process_code"].tolist())
    map_colors = {"None": "#FFFFFF"}
    hex_colors = generate_colors(len(processes))
    for i, p in enumerate(processes):
        map_colors[p] = hex_colors[i]
    return map_colors
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

# round coordinates
df["water"]["latitude"] = round(df["water"]["latitude"], 5)
df["water"]["longitude"] = round(df["water"]["longitude"], 5)
df["wastewater"]["latitude"] = round(df["wastewater"]["latitude"], 5)
df["wastewater"]["longitude"] = round(df["wastewater"]["longitude"], 5)

side_panel_layout = html.Div(
    id = "panel-left",
    children = [
        html.Div(
            children = [
                html.H1(children = "WATERGEEKS"),
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
                            {'label': 'See plants with ALL of the following', 'value': 'ALL'},
                            {'label': 'See plants with ANY of the following', 'value': 'ANY'},
                        ],
                        value = 'ANY',
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
        ),
        html.Div(
            html.Button(
                id = "view-data",
                children = "View data table"
            )
        )
    ]
)

main_panel_layout = html.Div(
    id = "panel-right",
    children = [
        html.Div(
            id = "panel-right-top",
            children = [
                dcc.Graph(
                    id = "world-map",
                    figure = {
                        "data": [
                            {
                                "type": "scattermapbox",
                                "lat": df["water"]["latitude"],
                                "lon": df["water"]["longitude"],
                                "mode": "markers+text",
                                "hoverinfo": "text+lon+lat",
                                "hoverdata": df["water"]["municipality_name"],
                                #"hoverinfo": "text+lon+lat",
                                #"text": df["water"]["municipality_name"],
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
        html.Div(
            id = "panel-right-bottom",
            children = [
                dt.DataTable(
                    id="table",
                    sort_action="native",
                    filter_action="native",
                    row_deletable=True,
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                    },
                    style_table={
                        "paddingRight": "15px",
                        "overflowY": "scroll",
                    },
                    style_cell={
                        "textAlign": "left",
                        "fontSize": "12px",
                        "fontFamily": "sans-serif",
                        "backgroundColor": COLORS["dark1"],
                        "border": COLORS["dark2"],
                        "width": "100%",
                        "midWidth": "0px",
                        "padding": "5px"
                    },
                    columns=[{"name": i, "id": i} for i in df["water"].columns],
                    data=df["water"].to_dict("rows"),
                )
            ]
        )
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
        Output("table", "data"), 
        Output("table", "columns"), 
        Output("world-map", "figure"),
        Output("treatment-type", "options"),
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
def update_map_and_data(plant, sort, treatment, old_figure):
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
            data = data.loc[data['process_code'].isin(treatment)] #TODO: edit this!
            # check = True
            # for t in treatment:
            #     d = data.loc[df['process_code'] == t]
            #     for m in data["municipality_name"].drop_duplicates():
            #         print(t)
            #         #d = data.loc[df['process_code'] == t]
            #         #check = check and (m in d) 
            #     print(check)
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
    data = data.drop(columns=["color", "size"])
    data["latitude"] = round(data["latitude"], 5)
    data["longitude"] = round(data["longitude"], 5)
    table_columns = [{"name": i, "id": i} for i in data.columns]
    table_data = data.to_dict("rows")
    return table_data, table_columns, figure, options

@app.callback(
    [
        Output("panel-right-top", "style"),
        Output("panel-right-bottom", "style"),
        Output("view-data", "children"),
    ],
    [
        Input("view-data", "n_clicks")
    ],
    [
        State("view-data", "children"),
    ],
)
def view_data(button_clicks, button_text):
    top_style = {"height": "100vh"}
    bottom_style = {"height": "0vh"}
    if button_clicks != None:
        if button_text == "View data table":
            button_text = "Hide data table"
            top_style = {"height": "50vh"}
            bottom_style = {"height": "50vh"}
        else:
            button_text = "View data table"
    return top_style, bottom_style, button_text


if __name__ == "__main__":
    app.run_server(debug = True)