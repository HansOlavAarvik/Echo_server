import pandas as pd
from datetime import datetime
import os
import json
import threading
from div import log
from io import StringIO

# Use a file as a shared data store for "slow" sensor data like temp, humid, tof
DATA_FILE = "sensor_data.json"
_lock = threading.Lock() #lock for single thread use of dataframe

COLUMNS = [
    'timestamp', 
    'Inside_temperature', 
    'Outside_temperature',
    'Inside_humidity',
    'Outside_humidity',
    'Time_of_flight',
    'Vibration',
    'DB'
]

def _initialize_if_needed():
    """Create the data file if it doesn't exist"""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        with open(DATA_FILE, 'w') as f:
            df.to_json(f, date_format='iso')

def add_data(data_dict):
    with _lock:
        df = open_file()
        new_row = pd.DataFrame([data_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        df = group_by_timestamp(df)
        save_to_file(df)
    return True

def open_file():
    _initialize_if_needed()
    try:
        with open(DATA_FILE, 'r') as f:
            content = f.read()
            if not content or content == '[]':
                return pd.DataFrame(columns=COLUMNS)
            # Check if the content appears to be valid JSON
            try:
                json_data = json.loads(content)
                #(f"JSON parsed successfully, contains {len(json_data)} records")
            except json.JSONDecodeError as je:
                log(f"JSON parsing error: {str(je)}")
            
            try:
                df = pd.read_json(StringIO(content), convert_dates=['timestamp'])

            except Exception as e:
                log(f"Error in pd.read_json: {str(e)}")
                # Alternative: try manual JSON parsing
                log("Attempting manual JSON parsing")
                json_data = json.loads(content)
                df = pd.DataFrame(json_data)
                log(f"Manual parsing created DataFrame with shape: {df.shape}")
 
            if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df    
    except Exception as e:
        log(f"Error opening data file: {str(e)}")
        return pd.DataFrame(columns=COLUMNS)
    
def save_to_file(df):     
        if len(df) > 100:
            df = df.tail(100)
        with open(DATA_FILE, 'w') as f:
            df.to_json(f, date_format='iso', orient='records')

def group_by_timestamp(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=COLUMNS)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.floor('s') #round time to nearest second
    try:
        aggregations = {col: 'mean' for col in df.columns if col != 'timestamp'}
        merged_df = df.groupby('timestamp', as_index=False).agg(aggregations)
        return merged_df
    except Exception as e:
        log(f"Error in grouping data: {str(e)}")
        return df

def recent_data(minutes=5):
    """Get data from the last N minutes"""
    try:
        with _lock:
            df = open_file()
            if df is None:
                log("DataFrame is None, returning empty DataFrame")
                return pd.DataFrame(columns=COLUMNS)
            if df.empty:
                return df
            now = pd.Timestamp.now() # Filter for recent data
            cutoff = now - pd.Timedelta(minutes=minutes)
            if not df.empty and 'timestamp' in df.columns:
                df = df[df['timestamp'] >= cutoff]
            
            #log(f"Returning dataframe with {len(df)} rows")
            return df
    except Exception as e:
        #log(f"Error in recent_data: {str(e)}")
        return pd.DataFrame(columns=COLUMNS)