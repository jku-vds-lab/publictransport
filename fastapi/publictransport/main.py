from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import numpy as np 
import pandas as pd
from datetime import datetime, timedelta
from geojson import Polygon, Point, Feature, FeatureCollection
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
    
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

#Load
stops = pd.read_csv('stops.zip', sep=",")
stop_times = pd.read_csv('stop_times.zip', sep=",")

# Remove last three if still complete
if len(stop_times.columns) == 9:
    stop_times = stop_times.iloc[:, :-3]
    
# Remove last if still complete
if len(stops.columns) == 5:
    stops = stops.iloc[:, :-1]

#remove the :1 or :2 at the end of the station to combine both stations for the two directions (or more) to one
if len(stops[stops['stop_name'] == "Mattighofen Trattmannsberg"]['stop_id'].values[0]) > len("at:44:49675:0"):
    stop_times['stop_id'] = stop_times['stop_id'].str.rsplit(pat=":", n=1).str[0]
    stops['stop_id'] = stops['stop_id'].str.rsplit(pat=":", n=1).str[0]
    
#remove duplicates from stops (There are now after combining)
stops = stops.drop_duplicates(subset='stop_id', keep='first')
stop_times = stop_times.drop(['stop_headsign'], axis=1)


"""chunksize = 10 ** 5  # adjust this value based on your available memory and file size

chunks1 = []
for chunk1 in pd.read_csv('stop_times1.zip', chunksize=chunksize):
    
    # Convert 'arrival_time' and 'departure_time' to timedelta
    chunk1['arrival_time'] = pd.to_timedelta(chunk1['arrival_time'])
    chunk1['departure_time'] = pd.to_timedelta(chunk1['departure_time'])

    #Cast them as better dtypes to safe memory
    chunk1["stop_sequence"] =chunk1["stop_sequence"].astype('int16')
    
    chunks1.append(chunk1)
stop_times_1 = pd.concat(chunks1, axis=0)

chunks2 = []
for chunk2 in pd.read_csv('stop_times2.zip', chunksize=chunksize):
    
    # Convert 'arrival_time' and 'departure_time' to timedelta
    chunk2['arrival_time'] = pd.to_timedelta(chunk2['arrival_time'])
    chunk2['departure_time'] = pd.to_timedelta(chunk2['departure_time'])

    #Cast them as better dtypes to safe memory
    chunk2["stop_sequence"] =chunk2["stop_sequence"].astype('int16')
    
    chunks2.append(chunk2)
stop_times_2 = pd.concat(chunks2, axis=0)


#Combine
stop_times = pd.concat([stop_times_1, stop_times_2], ignore_index=True)
stop_times["trip_id"] =stop_times["trip_id"].astype('category')"""

# Remove last three if still complete
if len(stop_times.columns) == 9:
    stop_times = stop_times.iloc[:, :-3]
    
# Remove last if still complete
if len(stops.columns) == 5:
    stops = stops.iloc[:, :-1]

#remove the :1 or :2 at the end of the station to combine both stations for the two directions (or more) to one
if len(stops[stops['stop_name'] == "Steyr Kellaugasse"]['stop_id'].values[0]) > len("at:44:43052:0"):
    stop_times['stop_id'] = stop_times['stop_id'].str.rsplit(pat=":", n=1).str[0]
    stops['stop_id'] = stops['stop_id'].str.rsplit(pat=":", n=1).str[0]
    
#remove duplicates from stops (There are now after combining)
stops = stops.drop_duplicates(subset='stop_id', keep='first')
stop_times = stop_times.drop(['stop_headsign'], axis=1)

# Convert 'arrival_time' and 'departure_time' to timedelta
stop_times['arrival_time'] = pd.to_timedelta(stop_times['arrival_time'])
stop_times['departure_time'] = pd.to_timedelta(stop_times['departure_time'])

#Cast them as better dtypes to safe memory
stop_times["stop_sequence"] =stop_times["stop_sequence"].astype('int16')
stop_times["trip_id"] =stop_times["trip_id"].astype('category')

# Convert lat and lon to float 32
#stops["stop_lat"] = stops["stop_lat"].astype('float32') float32 doens't work - but could be a future improvement
#stops["stop_lon"] = stops["stop_lon"].astype('float32') float32 doens't work - but could be a future improvement

_factors_1minute_circle_ = [[0.9999999999999999, 0.9999847965700978], [1.0000075770935701, 0.9999848697787114], [1.0000150813256343, 0.999985088699548], [1.000022440418435, 0.9999854512243794], [1.0000295834891657, 0.9999859538620552], [1.0000364417330232, 0.9999865917721185], [1.000042949086338, 0.9999873588114115], [1.0000490428633828, 0.9999882475932298], [1.0000546643606987, 0.9999892495584478], [1.0000597594230969, 0.9999903550579349], [1.0000642789658598, 0.999991553445468], [1.0000681794480875, 0.9999928331802493], [1.0000714232926053, 0.9999941819380366], [1.0000739792483688, 0.9999955867298204], [1.0000758226918514, 0.9999970340269061], [1.000076935864502, 0.9999985098911937], [1.0000773080439682, 1.0000000001094027], [1.0000769356474302, 1.0000014903299514], [1.0000758222660504, 1.000002966201167], [1.0000739786302038, 1.0000044135095034], [1.0000714225058345, 1.0000058183164282], [1.0000681785229488, 1.0000071670926647], [1.000064277937909, 1.0000084468484949], [1.00005975833184, 1.0000096452588672], [1.0000546632480742, 1.000010750782106], [1.0000490417721495, 1.0000117527710763], [1.0000429480584312, 1.0000126415757338], [1.0000364408079434, 1.0000134086360757], [1.000029582702461, 1.0000140465645881], [1.000022439800334, 1.000014549217405], [1.0000150808998851, 1.0000149117534871], [1.0000075768765284, 1.0000151306812517], [0.9999999999999999, 1.000015203892205], [0.9999924232382877, 1.0000151306812517], [0.9999849195549682, 1.0000149117534871], [0.9999775612067101, 1.000014549217405], [0.9999704190477078, 1.0000140465645881], [0.9999635618477276, 1.0000134086360757], [0.9999570556303232, 1.0000126415757338], [0.9999509630375695, 1.0000117527710763], [0.9999453427274135, 1.000010750782106], [0.9999402488094227, 1.0000096452588672], [0.9999357303243352, 1.0000084468484949], [0.9999318307724052, 1.0000071670926647], [0.9999285876950565, 1.0000058183164282], [0.9999260323138521, 1.0000044135095034], [0.999924189230238, 1.000002966201167], [0.999923076188936, 1.0000014903299514], [0.9999227039072511, 1.0000000001094027], [0.9999230759719308, 0.9999985098911937], [0.9999241888045661, 0.9999970340269061], [0.9999260316958701, 0.9999955867298204], [0.9999285869085107, 0.9999941819380366], [0.9999318298475192, 0.9999928331802493], [0.9999357292966486, 0.999991553445468], [0.9999402477184266, 0.9999903550579349], [0.9999453416150325, 0.9999892495584478], [0.9999509619465501, 0.9999882475932298], [0.999957054602593, 0.9999873588114115], [0.9999635609227827, 0.9999865917721185], [0.9999704182610959, 0.9999859538620552], [0.9999775605886645, 0.9999854512243794], [0.9999849191292446, 0.999985088699548], [0.9999924230212524, 0.9999848697787114], [0.9999999999999999, 0.9999847965700978]]

stored_shapes = []

######################################################################

# get part of feed you want #feed.routes
@app.get("/feed")
async def load_feed(starting_station: str,starting_time: str,timelimit: str,forced: str): 
    async def event_stream(starting_station: str,starting_time: str,timelimit: str,forced: str):
        start_station = get_id_of_stop(starting_station)
        global stored_shapes
        stored_shapes = []
        for result, end_time in reachable_stations(start_station, starting_time, timelimit, forced):
            if end_time=="No":
                yield result
                return
            np_array = transform_nparray(result, end_time)
            geoshape = solution_geojson(np_array, start_station)
            check_size = str(geoshape)

            while len(check_size) > 60000: #this loop makes sure that no packages are transmitted that are to large to handle for the frontend 
                #print("in check size",len(check_size))
                yield check_size[:59999]
                check_size = check_size[59999:]

            #print("last check size",len(check_size))
            yield check_size
                #time measure

    return StreamingResponse(event_stream(starting_station, starting_time, timelimit, forced))

@app.get("/")
async def root():
    return {"message": "Visit http://127.0.0.1:8000/docs"}

@app.get("/marker")
async def get_geo(station_name: str):
    stop_iid = get_id_of_stop(station_name)
    return get_lat_lon_of_stop(stop_iid)

@app.get("/nearest_station")
async def find_nearest_station(lat: str, lon: str):
    return find_closest_station(lat,lon)

###### Python Functions #############################################


def find_closest_station(lat, lon):
    lat = float(lat)
    lon = float(lon)  

    # approximate conversion factor
    conversion_factor = (111111 + 70000) / 2

    #euclidian distance
    stops['distance'] = (((stops['stop_lat'] - lat) ** 2 + (stops['stop_lon'] - lon) ** 2) ** 0.5) * conversion_factor

    # sort data by distance and select top 5 closest stations
    closest_stations = stops.sort_values('distance').head(5)

    # create the result string
    result_string = ""
    for i in range(5):
        station_lat = closest_stations.iloc[i]['stop_lat']
        station_lon = closest_stations.iloc[i]['stop_lon']
        result_string += f"{closest_stations.iloc[i]['stop_name']};{int(closest_stations.iloc[i]['distance'])} m;{station_lat},{station_lon};"
    
    # remove the last semicolon
    result_string = result_string[:-1]
    return result_string

def get_stop_name(stop_id):
    stop_name = stops[stops['stop_id'] == stop_id]['stop_name'].values[0]
    return stop_name

#show a line
def show_line(trip_id):
    line_trip = stop_times[stop_times['trip_id'] == trip_id]#.values[0]
    return line_trip

def get_id_of_stop(stop_name):
    return stops.stop_id[stops.stop_name==stop_name].values[0]

def transform_nparray(result, end_time):    
    transformed_data = []
    for entry in result:
        time_left = (end_time - entry[1]).seconds // 60  # convert timedelta to minutes
        transformed_data.append([entry[0], f'{time_left // 60:02}:{time_left % 60:02}:00'])

    return np.array(transformed_data)

def single_geo_circle(stop_id, time_left):
    minutes_left = int(time_left.split(":")[0])*60 + int(time_left.split(":")[1]) + int(time_left.split(":")[0])/60
    if minutes_left < 0:
        minutes_left = 0.3
    elif minutes_left <= 0.5:
        minutes_left = 0.5
    elif minutes_left >= 601:
        minutes_left = 0.3
    elif minutes_left >= 13:
        minutes_left = 13
    else:
        pass
    #minutes_left = 10
    lat, lon = get_lat_lon_of_stop(stop_id)
    #print(lat, lon)
    geo_result = [] 
    for i in _factors_1minute_circle_:
        #print(i)
        geo_result.append((((i[0]-1)*minutes_left+1)*lon,((i[1]-1)*minutes_left+1)*lat))
    
    return geo_result

def get_lat_lon_of_stop(stop_id):
    return stops.stop_lat[stops.stop_id==stop_id].iloc[0],stops.stop_lon[stops.stop_id==stop_id].iloc[0]

def reset_stored_shapes():
    global stored_shapes
    stored_shapes = []

def solution_geojson(solution_array, starting_station):
    global stored_shapes
    
    geo_list = []
    lat, lon = get_lat_lon_of_stop(starting_station)
    feature = Feature(geometry=Point([lon, lat]))
    geo_list.append(feature)

    poly_list = []
    for i in range(len(solution_array)):
        poly = Polygon(single_geo_circle(solution_array[i][0], solution_array[i][1]))
        poly_list.append(poly)

    merged_poly = unary_union(poly_list) #unary_union() instead ERROR
    
    # Subtract previously stored shapes from the current one
    for stored_shape in stored_shapes:
        merged_poly = merged_poly.difference(stored_shape)

    # Add the current shape to the list of stored shapes
    stored_shapes.append(merged_poly)
    
    
    feature = Feature(geometry=merged_poly)
    geo_list.append(feature)
    
    return FeatureCollection(geo_list)

def find_all_in_walking_distance(valid_stops, end_time):

    # Add coords to valid_stops
    valid_stops = valid_stops.merge(stops[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']], on='stop_id')
    
    # Define walking speed and calculate distance that can be walked in 10 minutes
    walking_speed = 5.0 # km/h
    walking_distance = (walking_speed / 60) * 5 # distance in km
    
    # Define a scale to convert degrees to kilometers, approximately
    lat_scale = 110.574
    lon_scale = 111.320 * np.cos(np.radians(valid_stops['stop_lat'].mean()))  # Average cosine for simplicity
    
    # Fetch stop coordinates
    stop_coords = valid_stops[['stop_lat', 'stop_lon']].values

    # Transform to kilometers
    stop_coords_km = stop_coords * np.array([lat_scale, lon_scale])
    
    # Create a copy of the stops DataFrame
    stops_km = stops.copy()

    # Convert stop coordinates to kilometers
    stops_km[['stop_lat', 'stop_lon']] *= np.array([lat_scale, lon_scale])

    reachable_stops_info = []

    # Iterate over valid stops
    for index, row in valid_stops.iterrows():
        coords_km = np.array([row['stop_lat'], row['stop_lon']]) * np.array([lat_scale, lon_scale])
        arrival_time = row['arrival_time']

        # Calculate euclidean distances to all stops
        distances = np.sqrt(np.sum((stops_km[['stop_lat', 'stop_lon']].values - coords_km) ** 2, axis=1))

        # Find stops within walking distance
        reachable = stops_km[distances <= walking_distance]

        # Calculate walking times to reachable stops
        walking_times = distances[distances <= walking_distance] / walking_speed  # time in hours

        # Convert walking times to timedelta
        walking_times_td = pd.to_timedelta(walking_times, unit='h')

        # Compute arrival times at reachable stops
        arrival_times_reachable = (arrival_time + walking_times_td).floor('T') #rounding to nearest Minute

        # Create DataFrame with information about reachable stops
        reachable_stops = pd.DataFrame({
            'stop_id': reachable['stop_id'].values,
            'arrival_time': arrival_times_reachable
        })

        # Append to the list
        reachable_stops_info.append(reachable_stops)
    
    # Concatenate all dataframes
    if len(reachable_stops_info) != 0:
        reachable_stops_info = pd.concat(reachable_stops_info)

        # Remove lines from reachable_stops_info that contain a stop id that is already in valid stops 
        reachable_stops_info = reachable_stops_info[~reachable_stops_info['stop_id'].isin(valid_stops['stop_id'])]

        # Remove duplicates from reachable_stops_info according to the stop_id and keep the one that has the earlier arrival time
        reachable_stops_info = reachable_stops_info.sort_values('arrival_time').drop_duplicates('stop_id', keep='first')
        
        return reachable_stops_info
    else: 
        return "nothing found"
    
def reachable_stations(start_station, start_time, travel_time, forced):

    start_time = pd.to_timedelta(start_time)
    travel_time = pd.to_timedelta(str(travel_time) + ' minutes')

    # Calculate the end_time for this trip
    end_time = start_time + travel_time - pd.to_timedelta("00:01:00")
    
    amount_changes = 0 # How often someone had to change bus/train
    reachable_stations = [[[start_station, start_time]]]

    # Cut dataset to the valid time frame between start and end time
    valid_times = (stop_times['departure_time'] >= start_time) & (stop_times['arrival_time'] < end_time)
    reduced_stop_times = stop_times[valid_times]

    # Find all trips that start from the start_station at start_time or after
    start_trips = reduced_stop_times[reduced_stop_times['stop_id'] == start_station]

    # if for forced function
    five_minute_after_start = start_time + pd.to_timedelta('5 minutes')
    if len(start_trips) >= 1:
        if (start_trips['departure_time'] <= five_minute_after_start).any():
            pass
        else:
            if forced == "not_forced":
                next_departure_time = start_trips.loc[start_trips['departure_time'] > five_minute_after_start, 'departure_time'].min()

                # Konvertieren Sie das Timedelta Objekt in das Format "HH:MM:SS"
                total_seconds = int(next_departure_time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                next_departure_time_form = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)

                yield "!!!" + str(next_departure_time_form), "No"
                return


    # Create a dictionary where key is trip_id and value is the stop_sequence of start_station in that trip
    trip_start_sequence = start_trips.set_index('trip_id')['stop_sequence'].to_dict()

    # Find all the stops in these trips that can be reached within the travel_time
    valid_stops = reduced_stop_times[reduced_stop_times['trip_id'].isin(trip_start_sequence.keys())]

    #check if lambda is empty
    if valid_stops.empty:
        return reachable_stations, end_time

    # Filter out stops with a lower stop_sequence in their trip
    valid_stops = valid_stops[valid_stops.apply(lambda row: row['stop_sequence'] > trip_start_sequence.get(row['trip_id'], float('inf')), axis=1)]

    # Sort the DataFrame by 'time_remaining' in descending order and drop duplicates based on 'stop_id'
    valid_stops = valid_stops.sort_values('arrival_time', ascending=True).drop_duplicates('stop_id')
    
    # Convert the DataFrame back to a list of lists
    reachable_stations[amount_changes].extend(valid_stops[['stop_id', 'arrival_time']].values.tolist())
    
    #add start station for walking distance search
    new_row = pd.DataFrame([{'trip_id': "XXX", 'arrival_time': start_time, 'departure_time': start_time, 'stop_id': start_station, 'stop_sequence': 999}])
    valid_stops = pd.concat([valid_stops, new_row], ignore_index=True)
    
    #add all stations that are in walking distance (10min) 
    df_temp = find_all_in_walking_distance(valid_stops[['stop_id', 'arrival_time']] ,end_time)
    if isinstance(df_temp, str):
        pass
    else:
        for row in df_temp.values:
            reachable_stations[amount_changes].append(row.tolist())
    
    #yield reachable_stations First time
    yield reachable_stations[amount_changes], end_time
    
    used_trips = set(trip_start_sequence.keys())
    
    planned_changes = 5
    for i in range(planned_changes):
        
        amount_changes += 1
        next_reachable_stations = pd.DataFrame(columns=['stop_id', 'arrival_time'])

        # For each previously found reachable station...
        count_station = 0
        for station, arrival_time in reachable_stations[amount_changes - 1]: 
            count_station += 1
    
            # Cut dataset to the valid time frame between start and end time
            valid_times = (reduced_stop_times['departure_time'] >= arrival_time) & ~reduced_stop_times['trip_id'].isin(used_trips)
            new_reduced_stop_times = reduced_stop_times[valid_times]
    
            # Find all trips that stop at the new starting station
            start_trips = new_reduced_stop_times[new_reduced_stop_times['stop_id'] == station]
    
            # Create a dictionary where key is trip_id and value is the stop_sequence of new starting station in that trip
            trip_start_sequence = start_trips.set_index('trip_id')['stop_sequence'].to_dict()
            #print(trip_start_sequence)
    
            # Find all the stops in these trips that can be reached within the remaining time
            valid_stops = new_reduced_stop_times[new_reduced_stop_times['trip_id'].isin(trip_start_sequence.keys())]
    
            # Filter out stops with a lower stop_sequence in their trip
            valid_stops = valid_stops[valid_stops.apply(lambda row: row['stop_sequence'] > trip_start_sequence.get(row['trip_id'], float('inf')), axis=1)]
            
            #update used_trips for next iteration
            used_trips.update([trip_id for trip_id, _ in trip_start_sequence.items()])
    
            # Extend the df of next reachable stations
            if len(valid_stops.columns) > 1:
                next_reachable_stations = pd.concat([next_reachable_stations, valid_stops[['stop_id', 'arrival_time']]], ignore_index=True)            
        
        #add all stations that are in walking distance from one of the stops 
        df_temp = find_all_in_walking_distance(next_reachable_stations[['stop_id', 'arrival_time']] ,end_time )
        if isinstance(df_temp, str):
            pass
        else:
            next_reachable_stations = pd.concat([next_reachable_stations, df_temp], ignore_index=True)
            
        #clear double stations - remove the later visit to a station 
        next_reachable_stations.sort_values(['arrival_time'], ascending=[True], inplace=True)
        next_reachable_stations.drop_duplicates(subset='stop_id', keep='first', inplace=True)
        
        # Drop stations from next_reachable_stations that are already in reachable_stations unless they have an earlier arrival_time
        for prev_stations in reachable_stations:
            prev_df = pd.DataFrame(prev_stations, columns=['stop_id', 'arrival_time'])
            merge_df = pd.merge(prev_df, next_reachable_stations, on='stop_id', suffixes=('_prev', '_next'))
            worse_stations = merge_df[merge_df['arrival_time_next'] >= merge_df['arrival_time_prev']]
            next_reachable_stations = next_reachable_stations[~next_reachable_stations['stop_id'].isin(worse_stations['stop_id'])]
        
        # Update reachable_stations 
        reachable_stations.append(next_reachable_stations.values.tolist())

        #yield next_reachable_stations For every loop 
        yield reachable_stations[amount_changes], end_time





app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
