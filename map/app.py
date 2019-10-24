import seaborn as sns
import random
import pandas as pd
import dash
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import State, Input, Output

# initialize app
app = dash.Dash(
    __name__,
    meta_tags = [
        {"name": "viewport", "content": "width = device-width, initial-scale = 1.0"}
    ],
)

# suppress callback exceptions
app.config["suppress_callback_exceptions"] = True

# note for gunicorn
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

# define function to process data
def process_data(plant):
    # load data
    data = pd.read_csv("data/" + plant + "_temp.csv")
    # assign map colors depending on process
    processes = set(data["process_code"].tolist())
    rgb_colors = sns.color_palette("husl", len(processes))
    hex_colors = rgb_colors.as_hex()
    map_colors = {"None": "#FFFFFF"}
    for i, p in enumerate(processes):
        map_colors[p] = hex_colors[i]
    data["color"] = data["process_code"].apply(lambda p: map_colors[p])
    # define size of data point
    data["size"] = 10
    # assign compatibility scores # TODO: calculate properly later, may need to depend on starting plant!
    data["score"] = 0
    data["score"] = data["score"].apply(lambda x: random.uniform(0.0, 10.0)) 
    # return processed data
    return(data)

# load data
df = {
    "water": process_data("water"),
    "wastewater": process_data("wastewater")
}

# define function to get dropdown options for processes
def get_process_dropdown_options(data):
    options = data[["process_code", "process_name"]].drop_duplicates()
    options = options.rename(columns = {"process_name": "label", "process_code": "value"})
    options = options.to_dict('records')
    return(options)

# define side panel layout
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
                        id = "process-type",
                        className = "dropdown-component", # TODO: remove this?
                        options = get_process_dropdown_options(df["water"]),
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

# define main panel layout
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

# define data store component
data_store_component = dcc.Store(id="data-store", data=df["water"].to_dict('records'))

# generate app layout
app.layout = html.Div(
    id = "root",
    children = [
        side_panel_layout,
        main_panel_layout,
        data_store_component
    ],
)

# callback to update data store
@app.callback(
    [
        Output("data-store", "data"),
        Output("process-type", "options"),
    ],
    [
        Input("plant-type", "value"),
        Input("sort-type", "value"),
        Input("process-type", "value"),
    ]
)
def update_data(plant, sort, treatment):
    # switch between water and wastewater data
    data = df["water"] if plant == "water" else df["wastewater"]
    # update options in dropdown list of processes
    options = get_process_dropdown_options(data)
    # filter data according to process
    if treatment != None:
        if sort == "ALL":
            data = data.loc[data["process_code"].isin(treatment)] # TODO: come up with method
            # check = True
            # for t in treatment:
            #     d = data.loc[df['process_code'] == t]
            #     for m in data["municipality_name"].drop_duplicates():
            #         print(t)
            #         #d = data.loc[df['process_code'] == t]
            #         #check = check and (m in d) 
            #     print(check)
        else:
            data = data.loc[data["process_code"].isin(treatment)]
    return data.to_dict('records'), options

# callback to update table
@app.callback(
    [
        Output("table", "data"), 
        Output("table", "columns"),
    ],
    [
        Input("data-store", "data"),
    ]
)
def update_table(data):
    data = pd.DataFrame.from_records(data)
    data = data.drop(columns = ["color", "size"])
    data["latitude"] = round(data["latitude"], 5)
    data["longitude"] = round(data["longitude"], 5)
    table_columns = [{"name": i, "id": i} for i in data.columns]
    table_data = data.to_dict("rows")
    return table_data, table_columns

# callback to update map
@app.callback(
    Output("world-map", "figure"),
    [
        Input("data-store", "data"),
    ],
    [
        State("world-map", "figure"),
    ]
)
def update_map(data, figure):
    data = pd.DataFrame.from_records(data)
    figure["data"][0]["lat"] = data["latitude"]
    figure["data"][0]["lon"] = data["longitude"]
    figure["data"][0]["marker"] = {
        "size": data["size"], 
        "color": data["color"]
    }
    return figure

# callback to view data by showing bottom panel
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