import pandas as pd
import json
from datetime import datetime
from database import sensor_dataframe

def handle_json_data(data, address):
    sensor_data =json.loads(data.decode("utf-8"))
    print(f"recieved {len(data)} data from {address}")
    global sensor_dataframe
    sensor_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") ## add timestamp
    sensor_dataframe = pd.concat([sensor_dataframe, pd.DataFrame([sensor_data])], ignore_index=True) #add json data
    if len(sensor_dataframe) > 100:
        sensor_dataframe = sensor_dataframe.iloc[-100:]
    return True