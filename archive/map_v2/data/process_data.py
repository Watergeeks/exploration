import os
import argparse
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim

# define parser to parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("csv", type=str, choices=["water", "wastewater"], help="select csv file name to process data")
args = parser.parse_args()

# load data
df = pd.read_csv("data/" + args.csv + ".csv")

# select a mixed portion of the data (for testing version) # TODO: delete this
df = df.iloc[np.random.permutation(len(df))]
df = df[:100]

# initialize geolocator
geolocator = Nominatim(user_agent="my-application")

# get coordinates
df["coordinates"] = df["municipality_name"].apply(lambda x: geolocator.geocode(x + ", Quebec"))
df["latitude"] = df["coordinates"].apply(lambda x: x.latitude if x != None else None)
df["longitude"] = df["coordinates"].apply(lambda x: x.longitude if x != None else None)

# rearrange columns for next step
potential_columns = ["region_name", 
    "municipality_name", "municipality_code",
    "installation_name", "installation_code", 
    "latitude", "longitude", 
    "process_name", "process_code"]
sorted_columns = []
for col in potential_columns:
    if col in df.columns:
        sorted_columns.append(col)
df = df[sorted_columns]

if args.csv == "water":
    # create new dataframe to handle processes as individual data points
    new_list = []
    for index, row in df.iterrows():
        if type(row["process_name"]) is str:
            for pn, pc in zip(row["process_name"].split("\n"), row["process_code"].split("\n")):
                new_row = row.tolist()
                new_row.pop()
                new_row.pop()
                new_row.append(pn)
                new_row.append(pc)
                new_list.append(new_row)
        else:
            new_row = row.tolist()
            new_row.pop()
            new_row.pop()
            new_row.append("None")
            new_row.append("None")
            new_list.append(new_row)
    df = pd.DataFrame(new_list, columns=list(df.columns))

# output edited data into a csv file (for final version) # TODO: uncomment this
# df.to_csv("data/" + args.csv + "_clean.csv")

# temporarily delete (for testing version) # TODO: fix this missing lat/lon values, then delete this
df.dropna(subset=['latitude'], inplace=True)

# output edited data into a csv file (for testing version) # TODO: delete this
df.to_csv("data/" + args.csv + "_temp.csv")