# -*- coding: utf-8 -*-
"""
Chenlin Cheng
6/15/2022
flyExclusive Code Challange

"""
### libraries & package ###
import pandas as pd
import time
from datetime import datetime


### import dataset ###
request = pd.read_csv('C:/Users/chenl/OneDrive/Desktop/Requests-Grid view.csv')
fleet = pd.read_csv('C:/Users/chenl/OneDrive/Desktop/Fleet-Grid view.csv')
clients = pd.read_csv('C:/Users/chenl/OneDrive/Desktop/Clients-Grid view.csv')

### clean dataset & create new variable ###
request["expected_dropoff_time"] = request["expected_dropoff_time"].str.replace("-04:00", "")
request["pickup_time"] = request["pickup_time"].str.replace("-04:00", "")
request["dropoff_time"] = request["dropoff_time"].str.replace("-04:00", "")

#request["expected_dropoff_time"] = pd.to_datetime(request["expected_dropoff_time"])
request["pickup_time"] = pd.to_datetime(request["pickup_time"])
request["dropoff_time"] = pd.to_datetime(request["dropoff_time"])

# create new variable for actual delivery time
request["delivery_time"] = request["dropoff_time"] - request["pickup_time"]

request["delivery_time_mins"] = 0

request["delivery_time_mins"][request['delivery_time'].dt.total_seconds() > 0] = \
    request['delivery_time'].dt.total_seconds() // 60

request["delivery_time_mins"][request['delivery_time'].dt.total_seconds() < 0] = \
  ((12*60*60) + request["delivery_time"].dt.total_seconds()) //60




### create distance function to calculate distance between clients ###

from math import sin, cos, sqrt, atan2

R = 6373.0

def dist(id1, id2):
    lat1 = clients["lat"][id1 - 1]
    lng1 = clients["lng"][id1 - 1]

    lat2 = clients["lat"][id2 - 1]
    lng2 = clients["lng"][id2 - 1]
    
    dlng = lng2 - lng1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    distance = "{:.2f}".format(distance)
    return distance

### create a new variable for distance of every delivery ###
request['distance'] = request.apply(lambda x: dist(x['pickup_client_id'], x['dropoff_client_id']), axis = 1)

### create a date variable ###
request[['date', 'time']] = request["expected_dropoff_time"].str.split("T", expand = True)

### nan number of each day (unfilled requests) ###
df = request.groupby('date').agg({'vehicle_id': lambda x: x.isnull().sum()}).reset_index()
df

### number of request per day ###
df2 = request.groupby(["date"])["request_id"].count()
df2

### a subset for analysis ###
analysis = request.iloc[:,[3, 5, 6, 7, 9, 10, 11]]
analysis = analysis.sort_values(["date", "vehicle_id"])
analysis["distance"] = pd.to_numeric(analysis["distance"], errors = 'coerce')
analysis["total_dist"] = analysis[["vehicle_id", "distance"]].groupby('vehicle_id').cumsum()

### wait time between deliveries ###
analysis["rest_time"] = analysis.groupby(['date','vehicle_id'])["dropoff_time"].diff()

analysis["rest_time_mins"] = 0

analysis["rest_time_mins"][analysis["rest_time"].dt.total_seconds() > 0] = \
    analysis["rest_time"].dt.total_seconds() // 60 - analysis['delivery_time_mins']

analysis["rest_time_mins"][analysis["rest_time"].dt.total_seconds() <= 0] = \
    (analysis["rest_time"].dt.total_seconds() // 60) + 720 - analysis['delivery_time_mins'] 

### export dataframe to csv ###
request.to_csv(r"request.csv", index = False)
analysis.to_csv(r"analysis.csv", index = False)


