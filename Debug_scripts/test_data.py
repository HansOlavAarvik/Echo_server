import pandas as pd
import json
import numpy as np
import threading
from datetime import datetime, timedelta
import os
from time import sleep

# Setup variables
DATA_FILE = "test_sensor_data.json"
_lock = threading.Lock()
prev_time = None

# Keys list
KEYS_LIST = [
    "Vibration",
    "Inside_temperature",
    "Outside_temperature",
    "Inside_humidity",
    "Outside_humidity",
    "Time_of_flight"
]

def _initialize_if_needed():
        df = pd.DataFrame(columns=[
            'timestamp', 
            'Inside_temperature', 
            'Outside_temperature',
            'Inside_humidity',
            'Outside_humidity',
            'Time_of_flight',
            'Vibration'
        ])
        with open(DATA_FILE, 'w') as f:
            df.to_json(f, date_format='iso',orient='records')

def add_data(data_dict):
    with _lock:
        df = open_file()
        new_row = pd.DataFrame([data_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        df = group_by_timestamp(df)
        save_to_file(df)


def open_file():
    try:
        with open(DATA_FILE, 'r') as f:
            return pd.read_json(f, convert_dates=['timestamp'])
    except Exception as e:
        _initialize_if_needed()
        with open(DATA_FILE, 'r') as f:
            return pd.read_json(f, convert_dates=['timestamp'])

def save_to_file(df):     
        if len(df) > 100:
            df = df.tail(100)
        with open(DATA_FILE, 'w') as f:
            df.to_json(f, date_format='iso', orient='records')

def group_by_timestamp(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.floor('s')

    merged_df = df.groupby('timestamp', as_index=False).agg({
        'Inside_temperature': 'mean',
        'Outside_temperature': 'mean',
        'Inside_humidity': 'mean',
        'Outside_humidity': 'mean',
        'Time_of_flight': 'mean',
        'Vibration': 'mean'
    })
    return merged_df

def interpolate_timestamps(time_now, length):
    global prev_time

    if isinstance(time_now, str):
        time_now = datetime.fromisoformat(time_now)
    if prev_time is None:
        prev_time = time_now - timedelta(seconds=1)
    times = []
    timespan = (time_now - prev_time).total_seconds()
    avg_interval = (timespan) / length
    for i in range(length):
        inter_time = prev_time + timedelta(seconds=avg_interval * (i+1))
        times.append(inter_time)
    return times

def process_vibration_data(data):
    return
def process_sound(data):
    return
def handle_json_data(data, address):
    global prev_time
    try:
        json_data = json.loads(data.decode("utf-8"))
        current_time = datetime.now().isoformat()

        for key in json_data:
            if not isinstance(json_data[key], list):
                continue
            if key not in KEYS_LIST:
                continue
            values = json_data[key]
            #print("\nvalues: ",values)
            if not values:
                continue
            if key == "Vibration":
                process_vibration_data(values)
            length = len(json_data[key])
            timestamps = interpolate_timestamps(current_time, length)
            for i, value in enumerate(values):
                reading = {
                    'timestamp': timestamps[i].isoformat(),
                    key: value
                }
                #print("\nreading", reading)

                for other_key in KEYS_LIST:
                    if other_key != key and other_key not in reading:
                        reading[other_key] = np.nan
                add_data(reading)
        print(f"\ntime now:{current_time}")
        print(f"\nprev_time:{prev_time}")
        prev_time = current_time
        return True
    except Exception as e:
        return False

# Test data
test_data = {
    "Vibration": [],
    "Inside_temperature": [19, 18, 17],
    "Outside_temperature": [9, 8, 7],
    "Inside_humidity": [15, 14, 13],
    "Outside_humidity": [10, 12, 9, 11, 8, 10],
    "Time_of_flight": [-2, -3, -4]
}
test_data2 = {
    "Vibration": [],
    "Inside_temperature": [12, 13, 14],
    "Outside_temperature": [2, 4, 6],
    "Inside_humidity": [15, 14, 13],
    "Outside_humidity": [10, 12, 9, 11, 8, 10],
    "Time_of_flight": [-2, -3, -4]
}
# Convert to JSON string
json_data = json.dumps(test_data).encode('utf-8')

# Process the data
print("Processing test data...")
handle_json_data(json_data, ('test', 12345))
sleep(2)
json_data2 = json.dumps(test_data2).encode('utf-8')
handle_json_data(json_data2, ('test', 12345))
# Show results
print("\nFinal JSON file content:")
with open(DATA_FILE, 'r') as f:
    content = f.read()
    print(content)

# Print as DataFrame for better viewing
print("\nAs DataFrame:")
df = pd.read_json(DATA_FILE, convert_dates=['timestamp'])
print(df)