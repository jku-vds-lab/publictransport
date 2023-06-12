from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

import numpy as np 
import pandas as pd
from datetime import datetime, timedelta
from geojson import Polygon, Point, Feature, FeatureCollection
from shapely.geometry import Polygon, Point
from shapely.ops import cascaded_union

app = FastAPI()

#origins = [
#    "http://localhost",
#    "http://localhost:8080",
#]

#Star ["*"] is bad it allows all origins, methods ... better change it later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_factors_1minute_circle_ = [[0.9999999999999999, 0.9999847965700978], [1.0000075770935701, 0.9999848697787114], [1.0000150813256343, 0.999985088699548], [1.000022440418435, 0.9999854512243794], [1.0000295834891657, 0.9999859538620552], [1.0000364417330232, 0.9999865917721185], [1.000042949086338, 0.9999873588114115], [1.0000490428633828, 0.9999882475932298], [1.0000546643606987, 0.9999892495584478], [1.0000597594230969, 0.9999903550579349], [1.0000642789658598, 0.999991553445468], [1.0000681794480875, 0.9999928331802493], [1.0000714232926053, 0.9999941819380366], [1.0000739792483688, 0.9999955867298204], [1.0000758226918514, 0.9999970340269061], [1.000076935864502, 0.9999985098911937], [1.0000773080439682, 1.0000000001094027], [1.0000769356474302, 1.0000014903299514], [1.0000758222660504, 1.000002966201167], [1.0000739786302038, 1.0000044135095034], [1.0000714225058345, 1.0000058183164282], [1.0000681785229488, 1.0000071670926647], [1.000064277937909, 1.0000084468484949], [1.00005975833184, 1.0000096452588672], [1.0000546632480742, 1.000010750782106], [1.0000490417721495, 1.0000117527710763], [1.0000429480584312, 1.0000126415757338], [1.0000364408079434, 1.0000134086360757], [1.000029582702461, 1.0000140465645881], [1.000022439800334, 1.000014549217405], [1.0000150808998851, 1.0000149117534871], [1.0000075768765284, 1.0000151306812517], [0.9999999999999999, 1.000015203892205], [0.9999924232382877, 1.0000151306812517], [0.9999849195549682, 1.0000149117534871], [0.9999775612067101, 1.000014549217405], [0.9999704190477078, 1.0000140465645881], [0.9999635618477276, 1.0000134086360757], [0.9999570556303232, 1.0000126415757338], [0.9999509630375695, 1.0000117527710763], [0.9999453427274135, 1.000010750782106], [0.9999402488094227, 1.0000096452588672], [0.9999357303243352, 1.0000084468484949], [0.9999318307724052, 1.0000071670926647], [0.9999285876950565, 1.0000058183164282], [0.9999260323138521, 1.0000044135095034], [0.999924189230238, 1.000002966201167], [0.999923076188936, 1.0000014903299514], [0.9999227039072511, 1.0000000001094027], [0.9999230759719308, 0.9999985098911937], [0.9999241888045661, 0.9999970340269061], [0.9999260316958701, 0.9999955867298204], [0.9999285869085107, 0.9999941819380366], [0.9999318298475192, 0.9999928331802493], [0.9999357292966486, 0.999991553445468], [0.9999402477184266, 0.9999903550579349], [0.9999453416150325, 0.9999892495584478], [0.9999509619465501, 0.9999882475932298], [0.999957054602593, 0.9999873588114115], [0.9999635609227827, 0.9999865917721185], [0.9999704182610959, 0.9999859538620552], [0.9999775605886645, 0.9999854512243794], [0.9999849191292446, 0.999985088699548], [0.9999924230212524, 0.9999848697787114], [0.9999999999999999, 0.9999847965700978]]

stops_data = pd.read_csv('data/stops.txt', sep=",")
stops_data['stop_id'] = stops_data['stop_id'].apply(lambda x: ':'.join(x.split(':')[:-1])) #combines the two stops in both directions to one stop for both directions
stops_data = stops_data.drop_duplicates(subset=['stop_id'],keep="first")

gtfs_data = pd.read_csv('data/stop_times.zip', sep=",")
gtfs_data = gtfs_data.iloc[:,0:4]
gtfs_data.columns = ['trip_id', 'arrival_time', 'departure_time', 'stop_id']
gtfs_data = gtfs_data[gtfs_data.arrival_time<"23:58:00"]
gtfs_data['stop_id'] = gtfs_data['stop_id'].apply(lambda x: ':'.join(x.split(':')[:-1])) #combines the two stops in both directions to one stop for both directions

start_time = "O"
timedelta_ = None

#with open('dist_data.pickle', 'rb') as f:
    #dist_data = pickle.load(f)

# get part of feed you want #feed.routes
@app.get("/feed")
def load_feed(starting_station: str,starting_time: str,timelimit: str,forced: str): #Steyr Kellaugasse
    
    #timelimit = "00:30:00" #max 3h -> I would recommend this because of Performance reasons and times >=3h are less interesting in my Opinion
    #starting_time = "21:10:00"
    #starting_station = "at:44:43052:0:1" #Kellaugasse Steyr
    result = []
    visited_routes = []
    visited_stops = []
    testrun=execute(starting_station,starting_time,timelimit,result,visited_routes,visited_stops,forced) #starting_station_stop_id, starting_time, timelimit
    return str(testrun) 




#Load all csv sets to the server
#agency
#agency = pd.read_csv('data/agency.txt', sep=",")
#df_agency = agency.iloc[:,0:2]
#@app.post("/data/agency")
#async def load_agency():
#    return parse_csv(df_agency)

#stop times
#stop_times = pd.read_csv('data/stop_times.txt', sep=",")
#df_stop_times = stop_times
#@app.post("/data/stop_times")
#async def load_stop_times():
#    return parse_csv(df_stop_times)

#routes
#routes = pd.read_csv('data/routes.txt', sep=",")
#df_routes = routes
#@app.post("/data/routes")
#async def load_routes():
#    return parse_csv(df_routes)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/marker")
async def get_geo(station_name: str):
    stop_iid = get_id_of_stop(station_name)
    return get_lat_lon_of_stop(stop_iid)

@app.get("/nearest_station")
async def find_nearest_station(lat: str, lon: str):
    return find_closest_station(lat,lon)

###### Python Functions #############################################
def find_closest_station(lat,lon):
    lat = float(lat)
    lon = float(lon)  
    #euclidian distance
    stops_data['distance'] = ((stops_data['stop_lat'] - lat) ** 2 + (stops_data['stop_lon'] - lon) ** 2) ** 0.5
    closest_station = stops_data.loc[stops_data['distance'].idxmin(), 'stop_name']
    return closest_station

def add_minutes(start_time, timelimit):
    early_timelimit = start_time
    print("Start_time_variable",start_time)
    start_time = datetime.strptime(start_time, "%H:%M:%S")
    new_time = start_time + timedelta(minutes=timelimit)
    late_timelimit = new_time.strftime("%H:%M:%S")
    if late_timelimit < early_timelimit or timelimit >= 60*24:
        late_timelimit = '23:59:00'
    return early_timelimit, late_timelimit

def get_useful_data(gtfs_data, start_time, timelimit):             
    t1, t2 = add_minutes(start_time, timelimit)
    dataa = gtfs_data[(gtfs_data.arrival_time>=t1) & (gtfs_data.arrival_time<=t2)]
    #useable_data = data[data.arrival_time<=t2]
    #print("len of data:",dataa)
    return dataa
    
def get_id_of_stop(stop_name):
    return stops_data.stop_id[stops_data.stop_name==stop_name].values[0]

def find_all_routes_that_include_this_station(useful_gtfs_data, stop_id):
    routes = useful_gtfs_data[useful_gtfs_data.stop_id==stop_id]
    return routes

def get_route(trip_id, stop_times):
    return stop_times[stop_times.trip_id==trip_id] 

def time_left(s_time, c_time, timedelta_):
    s_time = datetime.strptime(s_time, '%H:%M:%S')
    c_time = datetime.strptime(c_time, '%H:%M:%S')
    time_used = c_time - s_time
    a_time = datetime.strptime("00:00:00", "%H:%M:%S")
    b_time = a_time + timedelta_ - time_used
    time_left = b_time.strftime("%H:%M:%S")
    return time_left

def next_stops_on_this_route(useful_gtfs_data,pandas_row,start_time,timedelta_,timelimit,visited_routes,visited_stops,result):
    #print(pandas_row["trip_id"],pandas_row["departure_time"],pandas_row["stop_id"])
    #print("---------")
    if pandas_row["trip_id"] not in visited_routes:
        visited_routes.append(pandas_row["trip_id"])
        #print(pandas_row["trip_id"],"route appended")
        #print("all next Stations:",useful_gtfs_data.stop_id[(useful_gtfs_data.trip_id==pandas_row["trip_id"]) & (useful_gtfs_data.departure_time>pandas_row["departure_time"])])
        all_next_stations=useful_gtfs_data[(useful_gtfs_data.trip_id==pandas_row["trip_id"]) & (useful_gtfs_data.departure_time>pandas_row["departure_time"])]
        for index, row in all_next_stations.iterrows():
            if row["stop_id"] not in visited_stops:
                #print(row["stop_id"],"appended")
                visited_stops.append(row["stop_id"])
                result.append([row["stop_id"],time_left(start_time,row["arrival_time"],timedelta_)])
                ##########################
                next_useful_gtfs_data = get_useful_data(useful_gtfs_data,row["departure_time"],timelimit-time_difference(start_time,row["departure_time"]))
                next_starting_points = find_all_routes_that_include_this_station(next_useful_gtfs_data, row["stop_id"]).drop_duplicates(subset=['trip_id'],keep="first") #just use first occurence if bus visits station more than once
                for next_index, next_row in next_starting_points.iterrows():
                    next_stops_on_this_route(next_useful_gtfs_data,next_row,start_time,timedelta_,timelimit,visited_routes,visited_stops,result)
                ##########################
            else:
                #print(row["stop_id"],"not appended")
                pass
    else:
        #print(pandas_row["trip_id"],"route not appended")
        pass
    
def execute(start_station,start_time,timelimit,result,visited_routes,visited_stops,forced):
    timelimit = int(timelimit)

    useful_gtfs_data = get_useful_data(gtfs_data,start_time,timelimit)

    timedelta_ = timedelta(minutes=timelimit)
    s_time = datetime.strptime("00:00:00", "%H:%M:%S")
    n_time = s_time + timedelta_
    l_time = n_time.strftime("%H:%M:%S")
    result.append([get_id_of_stop(start_station),l_time])
    visited_stops.append(get_id_of_stop(start_station))

    starting_points = find_all_routes_that_include_this_station(useful_gtfs_data, visited_stops[0]).drop_duplicates(subset=['trip_id'],keep="first") #just use first occurence if bus visits station more than once
    #print("Starting Points:",starting_points)
    
    if len(starting_points) != 0:
        min_departure_time = datetime.strptime(starting_points["departure_time"].min(), "%H:%M:%S")
        start_time_datetime = datetime.strptime(start_time, "%H:%M:%S")

        time_difference = min_departure_time - start_time_datetime
        min_time_difference = timedelta(minutes=5) # Minutes

        if forced == "not_forced":
            if time_difference >= min_time_difference:
                #print("!!!" + str(min_departure_time.time()))
                return "!!!" + str(min_departure_time.time())

    for index, row in starting_points.iterrows():
        next_stops_on_this_route(useful_gtfs_data,row,start_time,timedelta_,timelimit,visited_routes,visited_stops,result)
        
    testrun_array = np.array(result)
    print(testrun_array)
    geojson = solution_geojson(testrun_array,get_id_of_stop(start_station))
    print(geojson)
    return geojson

def time_difference(start, current):
    start = datetime.strptime(start, "%H:%M:%S")
    current = datetime.strptime(current, "%H:%M:%S")
    difference = current - start
    return int(difference.total_seconds()/60)

def single_geo_circle(stop_id, time_left):
    minutes_left = int(time_left.split(":")[0])*60 + int(time_left.split(":")[1]) + int(time_left.split(":")[0])/60
    if minutes_left < 0:
        raise ValueError("minutes left is less than zero Minutes")
    if minutes_left <= 0.5:
        minutes_left = 0.5
    if minutes_left >= 15:
        minutes_left = 15
    #minutes_left = 10
    lat, lon = get_lat_lon_of_stop(stop_id)
    #print(lat, lon)
    geo_result = [] 
    for i in _factors_1minute_circle_:
        #print(i)
        geo_result.append((((i[0]-1)*minutes_left+1)*lon,((i[1]-1)*minutes_left+1)*lat))
    
    #poly = Polygon([geo_result])
    #return poly
    return geo_result
"""
def solution_geojson(solution_array,starting_station): #np array in this format: [['at:44:43108:0:1', '0:22:00'],['at:44:43108:0:1', '0:22:00'],...]
    geo_list = []
    lat, lon = get_lat_lon_of_stop(starting_station)
    feature = Feature(geometry=Point([lon,lat]))
    geo_list.append(feature)
    for i in range(len(solution_array)):
        poly = Polygon([single_geo_circle(solution_array[i][0], solution_array[i][1])])
        feature = Feature(geometry=poly)
        geo_list.append(feature)
    
    return FeatureCollection(geo_list)
"""
def solution_geojson(solution_array, starting_station):
    geo_list = []
    lat, lon = get_lat_lon_of_stop(starting_station)
    feature = Feature(geometry=Point([lon, lat]))
    geo_list.append(feature)

    poly_list = []
    for i in range(len(solution_array)):
        poly = Polygon(single_geo_circle(solution_array[i][0], solution_array[i][1]))
        poly_list.append(poly)

    merged_poly = cascaded_union(poly_list)
    feature = Feature(geometry=merged_poly)
    geo_list.append(feature)
    
    return FeatureCollection(geo_list)

def get_lat_lon_of_stop(stop_id):
    return stops_data.stop_lat[stops_data.stop_id==stop_id].iloc[0],stops_data.stop_lon[stops_data.stop_id==stop_id].iloc[0]



app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")