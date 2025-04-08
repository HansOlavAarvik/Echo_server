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

def recent_data(minutes=5):
    from div import log
    try:
        with _lock:
            _initialize_if_needed()
            try:
                with open(DATA_FILE, 'r') as f:
                    content = f.read()
                    if not content or content == '[]':
                        return pd.DataFrame(columns=[
                            'timestamp', 
                            'Inside_temperature', 
                            'Outside_temperature',
                            'Inside_humidity',
                            'Outside_humidity',
                            'Time_of_flight',
                            'Vibration'
                        ])
                    df = pd.read_json(content, convert_dates=['timestamp'])
                
                # Ensure timestamp is a datetime
                if 'timestamp' in df.columns and len(df) > 0:
                    # Convert timestamps if they're not already datetime
                    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Filter to only show recent data
                    now = pd.Timestamp.now()
                    cutoff = now - pd.Timedelta(minutes=minutes)
                    # Only filter if we have data with proper timestamps
                    if not df.empty and not all(pd.isna(df['timestamp'])):
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
    except Exception as e:
        log(f"Error in recent_data: {str(e)}")
        return pd.DataFrame()