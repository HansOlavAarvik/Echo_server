# from datetime import datetime, timedelta
# import json
# from div import log
# from database import add_data
# import numpy as np


# KEYS_LIST= ["Vibration",
# "Inside_temperature",
# "Outside_temperature",
# "Inside_humidity",
# "Outside_humidity",
# "Time_of_flight"]

# prev_time = None


# def handle_json_data(data, address):
#     global prev_time
#     try:
#         json_data = json.loads(data.decode("utf-8"))
#         current_time = datetime.now().isoformat()

#         for key in json_data:
#             if not isinstance(json_data[key], list):
#                 continue
#             if key not in KEYS_LIST:
#                 continue
#             values = json_data[key]
#             if not values:
#                 continue
#             if key == "Vibration":
#                 process_vibration_data(values)
#             length = len(json_data[key])
#             timestamps = interpolate_timestamps(current_time, length)
#             for i, value in enumerate(values):
#                 reading = {
#                     'timestamp': timestamps[i].isoformat(),
#                     key: value
#                 }
#                 for other_key in KEYS_LIST:
#                     if other_key != key and other_key not in reading:
#                         reading[other_key] = np.nan
#                 add_data(reading)
#         prev_time = current_time
#         return True
#     except Exception as e:
#         return False

# def interpolate_timestamps(time_now, length):
#     global prev_time

#     if isinstance(time_now, str):
#         time_now = datetime.fromisoformat(time_now)
#     if prev_time is None:
#         prev_time = time_now - timedelta(seconds=1)
#     times = []
#     timespan = (time_now - prev_time).total_seconds()
#     avg_interval = (timespan) / length
#     for i in range(length):
#         inter_time = prev_time + timedelta(seconds=avg_interval * (i+1))
#         times.append(inter_time)
#     return times


# def process_vibration_data(data):
#     return

# def process_sound(data):
#     return

from datetime import datetime, timedelta
import json
from div import log
from database import add_data
import numpy as np


KEYS_LIST= ["Vibration",
"Inside_temperature",
"Outside_temperature",
"Inside_humidity",
"Outside_humidity",
"Time_of_flight"]

prev_time = None


def handle_json_data(data, address):
    global prev_time
    try:
        json_data = json.loads(data.decode("utf-8"))
        current_time = datetime.now()
        
        # Find the maximum array length among all sensor types
        max_length = 0
        for key in KEYS_LIST:
            if key in json_data and isinstance(json_data[key], list):
                max_length = max(max_length, len(json_data[key]))
        
        if max_length == 0:
            return True  # No valid arrays found
            
        # Set prev_time if it's None
        if prev_time is None:
            prev_time = current_time - timedelta(seconds=max_length)
            
        # Calculate time interval between readings
        time_interval = (current_time - prev_time) / max_length
        
        # Process each time point
        for i in range(max_length):
            timestamp = prev_time + time_interval * (i + 1)
            
            # Create a reading with all sensor values for this time point
            reading = {
                'timestamp': timestamp.isoformat()
            }
            
            # Add data from each sensor array
            for key in KEYS_LIST:
                if (key in json_data and 
                    isinstance(json_data[key], list) and 
                    json_data[key] and 
                    i < len(json_data[key])):
                    reading[key] = json_data[key][i]
                else:
                    reading[key] = np.nan
                    
            # Add this complete reading to the database
            add_data(reading)
            
        # Update prev_time for next batch
        prev_time = current_time
        return True
    except Exception as e:
        log(f"Error processing JSON data: {str(e)}")
        return False


def process_vibration_data(data):
    return


def process_sound(data):
    return
