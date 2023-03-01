import numpy as np 
import pandas as pd
import gtfs_kit as gk
from datetime import datetime, timedelta
import time
import json

#FMT = '%H:%M:%S'

#agency = pd.read_csv('data/agency.txt', sep=",")
#agency = agency.iloc[:,0:2]

def parse_csv(df):
    res = df.to_json(orient="records")
    parsed = json.loads(res)
    return parsed