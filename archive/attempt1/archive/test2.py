# import plotly.express as px

# px.set_mapbox_access_token(open(".mapbox_token").read())

# carshare = px.data.carshare()

# fig = px.scatter_mapbox(
#     carshare, 
#     lat="centroid_lat", 
#     lon="centroid_lon", 
#     color="peak_hour", 
#     size="car_hours",
#     color_continuous_scale=px.colors.cyclical.IceFire, 
#     size_max=15, 
#     zoom=10
# )

# fig.show()

import pandas as pd
import plotly.express as px

us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
print(us_cities[:5])

fig = px.scatter_mapbox(
    us_cities, 
    lat="lat", 
    lon="lon", 
    hover_name="City", 
    hover_data=["State", "Population"],
    color_discrete_sequence=["#DD8600"], 
    zoom=4, 
    height=800
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":20,"l":20,"b":20})
fig.show()