import pandas as pd
import json
import numpy as np
import threading
from datetime import datetime, timedelta
import os

# Mock the log function that would be imported from div
def log(message):
    print(f"LOG: {message}")

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
            df.to_json(f, date_format='iso')

def add_data(data_dict):
    processed_dict = {}
    if not os.path.exists(DATA_FILE):
        _initialize_if_needed()
    processed_dict[key] = value         
    with _lock:
        _initialize_if_needed()
        try:
            with open(DATA_FILE, 'r') as f:
                df = pd.read_json(f, convert_dates=['timestamp'])
        except Exception as e:
            _initialize_if_needed()

        if 'timestamp' in df.columns:
            if df['timestamp'].dtype == 'object':
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            elif not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                # If timestamp isn't a datetime, convert it
                df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Process the new data
        if processed_dict and 'timestamp' in processed_dict:
            # Convert timestamp to datetime for comparison
            ts = processed_dict['timestamp']
            if isinstance(ts, str):
                ts = pd.to_datetime(ts)
                
            # Find timestamps that are close
            match_found = False
            if not df.empty and 'timestamp' in df.columns:
                # Find any rows within 0.2 seconds of this timestamp
                close_rows = []
                for idx, row_ts in enumerate(df['timestamp']):
                    if pd.api.types.is_datetime64_any_dtype(row_ts) or isinstance(row_ts, datetime):
                        time_diff = abs((ts - row_ts).total_seconds())
                        if time_diff < 0.1:  # Within 0.2 seconds
                            close_rows.append(idx)
                
                # Update the first close row if any exist
                if close_rows:
                    match_found = True
                    idx = close_rows[0]
                    # Update with non-NaN values
                    for key, value in processed_dict.items():
                        if key != 'timestamp' and not pd.isna(value):
                            df.at[idx, key] = value
            
            # If no match was found, add as new row
            if not match_found:
                new_row = pd.DataFrame([processed_dict])
                df = pd.concat([df, new_row], ignore_index=True)
        
        # Keep only recent data (last 100 data points)
        if len(df) > 100:
            df = df.tail(100)

        # Save with explicit date_format to ensure proper serialization
        with open(DATA_FILE, 'w') as f:
            df.to_json(f, date_format='iso', orient='records')

        # For debugging - verify what was saved
        with open(DATA_FILE, 'r') as f:
            log(f"Saved JSON: {f.read()[:100]}...")
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

        log(f"received {len(data)} data from {address}")
        current_time = datetime.now().isoformat()

        # add_data(json_data)
        for key in json_data:
            if not isinstance(json_data[key], list):
                continue
            if key not in KEYS_LIST:
                continue
            values = json_data[key]
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
                log(f"reading: {reading}")
                for other_key in KEYS_LIST:
                    if other_key != key and other_key not in reading:
                        reading[other_key] = np.nan
                add_data(reading)
        prev_time = current_time
        return True
    except Exception as e:
        log(f"Error processing data: {str(e)}")
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

# Convert to JSON string
json_data = json.dumps(test_data).encode('utf-8')

# Process the data
print("Processing test data...")
handle_json_data(json_data, ('test', 12345))

# Show results
print("\nFinal JSON file content:")
with open(DATA_FILE, 'r') as f:
    content = f.read()
    print(content)

# Print as DataFrame for better viewing
print("\nAs DataFrame:")
df = pd.read_json(DATA_FILE, convert_dates=['timestamp'])
print(df)