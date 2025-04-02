import pandas as pd

sensor_dataframe = pd.DataFrame(columns=[
    'timestamp', 
    'Inside_temperature', 
    'Outside_temperature',
    'Inside_humidity',
    'Outside_humidity',
    'Time_of_flight',
    'Vibration'
])

def recent_data():
    return sensor_dataframe