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
# df["coordinates"] = df["municipality"].apply(geolocator.geocode)
# df["latitide"] = df["coordinates"].apply(lambda x: x.latitude if x != None else None)
# df["longitude"] = df["coordinates"].apply(lambda x: x.longitude if x != None else None)

# TODO: delete this after check if we don't need to define new columns
# df["chloration"] = df["process"].apply(lambda x: True if "chloration" in x else False)
# df["filtration"] = df["process"].apply(lambda x: True if "filtration" in x else False)
# df["ultraviolet"] = df["process"].apply(lambda x: True if "ultraviolet" in x else False)
# df["ozonation"] = df["process"].apply(lambda x: True if "ozonation" in x else False)
# df["charbon"] = df["process"].apply(lambda x: True if "charbon" in x else False)

# create new dataframe to handle processes as individual data points
new_list = []
for index, row in df.iterrows():
    for p in row["process"].split("\n"):
        new_row = row.tolist()
        new_row.pop() # TODO: need to remove element at certain index after adding coordinates?
        new_row.append(p)
        new_list.append(new_row)
new_df = pd.DataFrame(new_list, columns=list(df.columns))
print(new_df)