#import seaborn as sns
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
        {
            "name": "viewport", 
            "content": "width = device-width, initial-scale = 1.0"
        }
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

# define potential columns # TODO: consider moving to merge_data function
COLUMNS = [
    "region_name", 
    "municipality_name", "municipality_code",
    "installation_name", "installation_code", 
    "latitude", "longitude", 
    "process_name", "process_code"
]

# define function to process data
def process_data(plant):
    # load data
    data = pd.read_csv("data/" + plant + "_temp.csv", index_col = 0)
    # assign map colors depending on process
    # processes = set(data["process_code"].tolist())
    # rgb_colors = sns.color_palette("husl", len(processes))
    # hex_colors = rgb_colors.as_hex()
    # map_colors = {}
    # for i, p in enumerate(processes):
    #     map_colors[p] = hex_colors[i]
    # map_colors["None"] = "#FFFFFF"
    # data["color"] = data["process_code"].apply(lambda p: map_colors[p])
    if plant == "water": 
        map_colors = {'FIL': '#f77189', 'CHB': '#bb9832', 'CHL': '#50b131', 'None': '#FFFFFF', 'UB': '#3ba3ec', 'OZ': '#e866f4'}
    else: 
        map_colors = {'ERR': '#f77189', 'BF': '#d58c32', 'DEG': '#a4a031', 'ENAF': '#50b131', 'BA': '#34ae91', 'ROS': '#37abb5', 'EA': '#3ba3ec', 'BD': '#bb83f4', 'ENA': '#f564d4', 'None': '#FFFFFF'}
    data["color"] = data["process_code"].apply(lambda p: map_colors[p])
    # define size of data point
    data["size"] = 10
    # assign random compatibility scores # TODO: calculate properly, may need to depend on starting plant!
    municipalities = set(data["municipality_name"].tolist())
    compatibilities = {}
    for m in municipalities:
        compatibilities[m] = random.uniform(0.5, 10.0)
    compatibilities["Montréal"] = 0.24534634536 # TODO: manually done for Montreal
    compatibilities["Fort-Coulonge"] = 0.234234546
    compatibilities["Longueuil"] = 0.33542343
    compatibilities["La Prairie"] = 0.19885342345
    compatibilities["Gouvernement régional d'Eeyou Istchee Baie-James"] = 0.3654332345
    data["compatibility_score"] = data["municipality_name"].apply(lambda m: compatibilities[m]) 
    # return processed data
    return(data)

# define function to merge data by process # TODO: finish implementing here and everywhere
def merge_data(data):
    columns = data.columns.tolist()
    group = ['region_name', 'municipality_name', 'installation_name']
    functions = {}
    for c in columns:
        if c == 'process_name' or c == 'process_code':
            functions[c] = ', '.join
        elif c not in group:
            functions[c] = 'first'
    data = data.groupby(group).agg(functions).reset_index()
    data['color'] = COLORS["yellow"]
    return data

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

def get_map_labels(data):
    # define map label template
    template = "Region: {} \n<br />Municipality: {} \n<br />Process: {} \n"
    labels = []
    for i, row in data.iterrows():
        labels.append(
            template.format(
                row["region_name"],
                row["municipality_name"],
                row["process_name"]
            )
        )
    labels = pd.Series(labels).astype(str)

    # # TODO: FINISH IMPLEMENT DIS  
    # # get merged data # TODO: reconsider merging
    # data = merge_data(data)
    
    return labels

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
                className = "dropdown-component",
                options = [
                    {"label": "water", "value": "water"},
                    {"label": "wastewater", "value": "wastewater"},
                ],
                value = "water",
                clearable = False
            )
        ),
        html.H3(children = "My municipality is..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "municipality-name",
                className = "dropdown-component",
                placeholder = "select municipality...",
                options = get_municipality_options(df["water"]),
                clearable = True
            )
        ),
        html.H3(children = "I am interested in processes such as..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "process-type",
                className = "dropdown-component",
                placeholder = "select processes...",
                options = get_process_options(df["water"]),
                clearable = True,
                multi = True
            )
        ),
        html.H3(children = "I want to view plants..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "sort-type",
                className = "dropdown-component",
                options = [
                    {"label": "considered most compatible with me", "value": "COMP"},
                    # TODO: uncomment when sorting method ready
                    # {"label": "with ALL of the listed processes", "value": "ALL"}, 
                    {"label": "with ANY of the listed processes", "value": "ANY"},
                ],
                value = "COMP",
                clearable = False
            ) 
        ),
        html.H3(children = "...displayed in..."),
        html.Div(
            className = "dropdown",
            children = dcc.Dropdown(
                id = "display-type",
                className = "dropdown-component",
                options = [
                    {"label": "a map", "value": "MAP"},
                    {"label": "a table", "value": "TABLE"},
                    {"label": "both a map and a table", "value": "BOTH"},
                ],
                value = "MAP", # TODO: reconsider default
                clearable = False
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
                    id = "map",
                    figure = {
                        "data": [
                            {
                                "type": "scattermapbox",
                                "lat": df["water"]["latitude"],
                                "lon": df["water"]["longitude"],
                                "mode": "markers",
                                "text": get_map_labels(df["water"]), # TODO: reconsider info needed for data points
                                "marker": {
                                    "size": df["water"]["size"], 
                                    "color": df["water"]["color"], # TODO: reconsider making all same color
                                    "opacity": 0.2 # TODO: reconsider opacity
                                }
                            }
                        ],
                        "layout": {
                            "hovermode": "closest",
                            "mapbox": {
                                "accesstoken": MAPBOX_ACCESS_TOKEN,
                                "style": MAPBOX_STYLE,
                                "center": {"lat": 55, "lon": -71},
                                "zoom": 4
                            },
                            "showlegend": False,
                            "autosize": True,
                            "margin": {"t": 0, "r": 0, "b": 0, "l": 0}
                        }
                    },
                    config = {
                        "displayModeBar": False, 
                        "scrollZoom": True
                    }
                )
            ]
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
                        "height": "auto"
                    },
                    style_table = {
                        # "paddingRight": "15px", # TODO: consider how to better see last column
                        "overflowY": "scroll"
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
                    data = df["water"].to_dict("rows")
                )
            ]
        )
    ]
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
        Output("municipality-name", "value")
    ],
    [
        Input("plant-type", "value")
    ]
)
def refresh_data_and_dropdown_options(plant):
    # switch between water and wastewater data
    data = df[plant]
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
    ]
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
        Input("municipality-name", "value"),
        Input("process-type", "value"),
        Input("sort-type", "value")
    ],
    [
        State("plant-type", "value")
    ]
)
def update_data(data, municipality, process, sort, plant):
    # translate dictionary records to a data frame
    data = pd.DataFrame.from_records(data)
    # filter data according to process
    if process != None and process != []:
        if sort == "ANY":
            data = data.loc[data["process_code"].isin(process)]
        elif sort == "ALL":
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
    else:
        data = df[plant]
    # filter data by compatibility
    if sort == "COMP":
        if municipality != None:
            # TODO: come up with non-random method using municipality input
            data_by_score = data.groupby('municipality_name').agg({'compatibility_score': 'mean'}).reset_index()
            data_with_score = data_by_score.loc[data_by_score["municipality_name"] == municipality, 'compatibility_score']
            score = float(data_with_score.to_string(index = False))
            data = data.loc[(data["compatibility_score"] >= score-0.2) & (data["compatibility_score"] <= score+0.2)]
    # prepare data in expected format for data store
    data = data.to_dict("records")
    return data

# callback to update table
@app.callback(
    [
        Output("table", "data"), 
        Output("table", "columns"),
        Output("table", "style_cell_conditional")
    ],
    [
        Input("final-data-store", "data"),
        Input("municipality-name", "value")
    ]
)
def update_table(data, municipality):
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
    # update conditional styling
    style_cond = []
    # TODO: finish designing condititonal styling
    # if municipality != None:
    #     style_cond.append(
    #         {
    #             "if": {
    #                 "column_id": "municipality_name",
    #                 "filter_query": "{municipality_name} eq '{}'".format(municipality)
    #             }, 
    #             "backgroundColor": COLORS["yellow"]
    #         }
    #     )
    return table_data, table_columns, style_cond

# callback to update map
@app.callback(
    Output("map", "figure"),
    [
        Input("final-data-store", "data")
    ],
    [
        State("map", "figure")
    ]
)
def update_map(data, figure):
    # translate dictionary records to a data frame
    data = pd.DataFrame.from_records(data)
    # update coordinates rounded for easy viewing
    figure["data"][0]["lat"] = round(data["latitude"], 5)
    figure["data"][0]["lon"] = round(data["longitude"], 5)
    # update marker text # TODO: reconsider info needed for data points
    figure["data"][0]["text"] = get_map_labels(data)
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