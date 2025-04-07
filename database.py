import pandas as pd
from datetime import datetime
import os
import json
import threading

# Use a file as a shared data store that works across process boundaries
DATA_FILE = "sensor_data.json"
_lock = threading.Lock() #lock for single thread use of dataframe

def _initialize_if_needed():
    """Create the data file if it doesn't exist"""
    if not os.path.exists(DATA_FILE):
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
    """Add a row of data to the dataframe and save to file"""
    from div import log
    processed_dict = {}
    for key, value in data_dict.items():
        if isinstance(value, list) and key != 'timestamp':
            # Skip lists entirely
            pass
        else:
            processed_dict[key] = value
    with _lock:
        _initialize_if_needed()
        
        # Read existing data
        try:
            with open(DATA_FILE, 'r') as f:
                df = pd.read_json(f, convert_dates=['timestamp'], orient='records')

        except Exception as e:
            # If file is corrupted or empty, create a new dataframe
            df = pd.DataFrame(columns=[
                'timestamp', 
                'Inside_temperature', 
                'Outside_temperature',
                'Inside_humidity',
                'Outside_humidity',
                'Time_of_flight',
                'Vibration'
            ])
            log(f"Creating new dataframe: {str(e)}")
        
        if processed_dict:  # Only add if we have data after filtering lists
            new_row = pd.DataFrame([processed_dict])
            df = pd.concat([df, new_row], ignore_index=True)

        # Convert timestamp to datetime if it's a string
        if 'timestamp' in df.columns and df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'timestamp' in df.columns and df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Keep only recent data (last 100 data points)
        if len(df) > 100:
            df = df.tail(100)

        with open(DATA_FILE, 'w') as f:
            df.to_json(f, date_format='iso')

def recent_data(minutes=5):
    from div import log
    with _lock:
        _initialize_if_needed()
        try:
            with open(DATA_FILE, 'r') as f:
                df = pd.read_json(f, convert_dates=['timestamp'])
            
            # Ensure timestamp is a datetime
            if 'timestamp' in df.columns:
                if df['timestamp'].dtype == 'object':
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Filter to only show recent data
                now = pd.Timestamp.now()
                cutoff = now - pd.Timedelta(minutes=minutes)
                # Only filter if we have data with proper timestamps
                if not all(df['timestamp'].dt.year == 1970):
                    df = df[df['timestamp'] >= cutoff]
            
            log(f"Returning dataframe with {len(df)} rows")
            log(df)
            return df
        except Exception as e:
            log(f"Error reading data: {str(e)}")
            # Return empty dataframe on error
            return pd.DataFrame(columns=[
                'timestamp', 
                'Inside_temperature', 
                'Outside_temperature',
                'Inside_humidity',
                'Outside_humidity',
                'Time_of_flight',
                'Vibration'
            ])