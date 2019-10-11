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
df = df[:15]
print(df)

# initialize geolocator
geolocator = Nominatim(user_agent="my-application")

# get coordinates
df["coordinates"] = df["municipality"].apply(geolocator.geocode)
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