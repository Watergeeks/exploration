import os
import pandas as pd
from geopy.geocoders import Nominatim

# load data
df = pd.read_csv("data/eau_potable_production.csv")

# rename column headers
df = df.rename(columns={
    "Région administrative": "region",
    "Nom de la municipalité": "municipality", 
    "Numéro de l'installation de production": "installation_code",
    "Nom de l'installation de production d'eau potable": "installation_name",
    "Procédé de traitement": "processes"
})

# temporary
df = df[:50]
print(df)

# initialize geolocator
geolocator = Nominatim(user_agent="my-application")

# get coordinates
df["coordinates"] = df["municipality"].apply(geolocator.geocode)
df["latitide"] = df["coordinates"].apply(lambda x: x.latitude if x != None else None)
df["longitude"] = df["coordinates"].apply(lambda x: x.longitude if x != None else None)

print(df)

#location = geolocator.geocode("Abitibi-Témiscamingue")
#print(location.address)