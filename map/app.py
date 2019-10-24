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

# note for mapbox # TODO: fix mapbox styling and figure out how to access style properly
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

# define theme colors
COLORS = {
    "white": "#F3F6FA",
    "grey": "#707070",
    "dark1": "#1E1E1E",
    "dark2": "#2B2B2B",
    "orange": "#DD8600", #DD8600 vs #E67E22
    "yellow": "#FEC036", #FEC036 vs #D1A622
}

# define function to process data
def process_data(plant):
    # load data
    data = pd.read_csv("data/" + plant + "_temp.csv", index_col = 0)
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
    # assign compatibility scores # TODO: calculate properly, may need to depend on starting plant!
    municipalities = set(data["municipality_name"].tolist())
    compatibilities = {}
    for m in municipalities:
        compatibilities[m] = random.uniform(0.0, 10.0)
    data["score"] = data["municipality_name"].apply(lambda m: compatibilities[m]) 
    # return processed data
    return(data)

# load data
df = {
    "water": process_data("water"),
    "wastewater": process_data("wastewater")
}

# define function to get dropdown options for municipalities
def get_municipality_options(data):
    options = data[["municipality_name"]].drop_duplicates()
    options["municipality_code"] = options["municipality_name"]
    options = options.rename(columns = {"municipality_name": "label", "municipality_code": "value"})
    options = options.to_dict("records")
    return(options)

# define function to get dropdown options for processes
def get_process_options(data):
    options = data[["process_code", "process_name"]].drop_duplicates()
    options = options.rename(columns = {"process_name": "label", "process_code": "value"})
    options = options.to_dict("records")
    return(options)

# define side panel layout
side_panel_layout = html.Div(
    id = "panel-left",
    children = [
        html.H2(children = "Watergeeks"),
        html.Br(),
        html.H3(children = "My plant treats..."),
        html.Div(
            className = "dropdown", 
            children = dcc.Dropdown(
                id = "plant-type",
                className = "dropdown-component", # TODO: remove this?
                options = [
                    {"label": "water", "value": "water"},
                    {"label": "wastewater", "value": "wastewater"},
                ],
                clearable = False,
                value = "water",
            )
        ),
        html.H3(children = "My municipality is..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "municipality-name",
                className = "dropdown-component", # TODO: remove this?
                placeholder = "select municipality...",
                options = get_municipality_options(df["water"]),
                clearable = True,
            )
        ),
        html.H3(children = "I am interested in processes such as..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "process-type",
                className = "dropdown-component", # TODO: remove this?
                placeholder = "select processes...",
                options = get_process_options(df["water"]),
                clearable = True,
                multi = True,
            )
        ),
        html.H3(children = "I want to view plants..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "sort-type",
                className = "dropdown-component", # TODO: remove this?
                options = [
                    {"label": "considered most compatible with me", "value": "COMP"},
                    {"label": "with ALL of the listed processes", "value": "ALL"},
                    {"label": "with ANY of the listed processes", "value": "ANY"},
                ],
                value = "ANY"
            ) 
        ),
        html.H3(children = "...displayed in..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "display-type",
                className = "dropdown-component", # TODO: remove this?
                options = [
                    {"label": "a map", "value": "MAP"},
                    {"label": "a table", "value": "TABLE"},
                    {"label": "both a map and a table", "value": "BOTH"},
                ],
                value = "MAP" # TODO: reconsider default
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
                    id = "table",
                    sort_action = "native",
                    filter_action = "native",
                    row_deletable = False,
                    style_data = {
                        "whiteSpace": "normal",
                        "height": "auto",
                    },
                    style_table = {
                        # "paddingRight": "15px", # TODO: consider how to better see last column
                        "overflowY": "scroll",
                    },
                    style_cell = {
                        "textAlign": "left",
                        "fontSize": "12px",
                        "fontFamily": "sans-serif",
                        "backgroundColor": COLORS["dark1"],
                        "border": COLORS["dark2"],
                        "width": "100%",
                        "midWidth": "0px",
                        "padding": "5px"
                    },
                    # TODO: update column widths (https://github.com/plotly/dash-table/issues/432)
                    # style_cell_conditional = [
                    #     {"if": {"row_index": "even"}, "backgroundColor": "#f9f9f9"}
                    # ]
                    columns = [{"name": i, "id": i} for i in df["water"].columns],
                    data = df["water"].to_dict("rows"),
                )
            ]
        )
    ],
)

# define data store components
data_store_components = html.Div(
    children = [
        dcc.Store(
            id = "initial-data-store",
            data = df["water"].to_dict('records')
        ),
        dcc.Store(
            id = "final-data-store",
            data = df["water"].to_dict('records')
        )
    ]
)

# generate app layout
app.layout = html.Div(
    id = "root",
    children = [
        side_panel_layout,
        main_panel_layout,
        data_store_components
    ],
)

# callback to refresh data store and dropdown options
@app.callback(
    [
        Output("initial-data-store", "data"),
        Output("municipality-name", "options"),
        Output("process-type", "options"),
        Output("municipality-name", "value"),
    ],
    [
        Input("plant-type", "value"),
    ]
)
def refresh_data_and_dropdown_options(plant):
    # switch between water and wastewater data
    data = df["water"] if plant == "water" else df["wastewater"]
    # update options in dropdown list of municipalities
    municipality_options = get_municipality_options(data)
    # update options in dropdown list of processes
    process_options = get_process_options(data)
    # prepare data in expected format for data store
    data = data.to_dict("records")
    return data, municipality_options, process_options, None

# callback to automatically select dropdown values for processes
@app.callback(
    Output("process-type", "value"),
    [
        Input("municipality-name", "value"),
        Input("initial-data-store", "data")
    ],
)
def select_dropdown_values(municipality, data):
    # translate dictionary records to a data frame
    data = pd.DataFrame.from_records(data)
    if municipality != None:
        data = data.loc[data["municipality_name"] == municipality]
    processes = data["process_code"].drop_duplicates().tolist()
    return processes

# callback to update data store
@app.callback(
    Output("final-data-store", "data"),
    [
        Input("initial-data-store", "data"),
        Input("sort-type", "value"),
        Input("process-type", "value"),
    ],
    [
        State("municipality-name", "value"),
    ]
)
def update_data(data, sort, process, municipality):
    # translate dictionary records to a data frame
    data = pd.DataFrame.from_records(data)
    # filter data according to process
    if process != None:
        if sort == "ALL":
            # TODO: come up with correct method
            data = data.loc[data["process_code"].isin(process)]
            # check = True
            # for t in treatment:
            #     d = data.loc[df['process_code'] == t]
            #     for m in data["municipality_name"].drop_duplicates():
            #         print(t)
            #         #d = data.loc[df['process_code'] == t]
            #         #check = check and (m in d) 
            #     print(check)
        elif sort == "ANY":
            data = data.loc[data["process_code"].isin(process)]
        else:
            # TODO: come up with correct method, using municipality input
            data = data.loc[data["process_code"].isin(process)]
    # prepare data in expected format for data store
    data = data.to_dict("records")
    return data

# callback to update table
@app.callback(
    [
        Output("table", "data"), 
        Output("table", "columns"),
    ],
    [
        Input("final-data-store", "data"),
    ]
)
def update_table(data):
    # translate dictionary records to a data frame
    data = pd.DataFrame.from_records(data)
    # remove columns not necessary for viewing
    data = data.drop(columns = ["color", "size"])
    # round coordinates for easy viewing
    data["latitude"] = round(data["latitude"], 5)
    data["longitude"] = round(data["longitude"], 5)
    # prepare columns in expected format for table
    table_columns = [{"name": i, "id": i} for i in data.columns]
    # prepare data in expected format for table
    table_data = data.to_dict("rows")
    return table_data, table_columns

# callback to update map
@app.callback(
    Output("world-map", "figure"),
    [
        Input("final-data-store", "data"),
    ],
    [
        State("world-map", "figure"),
    ]
)
def update_map(data, figure):
    # translate dictionary records to a data frame
    data = pd.DataFrame.from_records(data)
    # update coordinates
    figure["data"][0]["lat"] = data["latitude"]
    figure["data"][0]["lon"] = data["longitude"]
    # update marker styling
    figure["data"][0]["marker"] = {
        "size": data["size"], 
        "color": data["color"]
    }
    return figure

# callback to update display mode
@app.callback(
    [
        Output("panel-right-top", "style"),
        Output("panel-right-bottom", "style")
    ],
    [
        Input("display-type", "value")
    ]
)
def update_display(display):
    # make map the primary view
    if display == "MAP":
        top_style = {"height": "100vh"}
        bottom_style = {"height": "0vh"}
    # make table the primary view
    elif display == "TABLE": 
        top_style = {"height": "0vh"}
        bottom_style = {"height": "100vh"}
    # make split view
    else:
        top_style = {"height": "50vh"}
        bottom_style = {"height": "50vh"}
    return top_style, bottom_style

if __name__ == "__main__":
    app.run_server(debug = True)