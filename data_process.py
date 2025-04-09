
from datetime import datetime, timedelta
import json
from div import log
from database import add_data
import numpy as np
import wave
import os
import math


KEYS_LIST= ["Vibration",
"Inside_temperature",
"Outside_temperature",
"Inside_humidity",
"Outside_humidity",
"Time_of_flight",
"DB"]

prev_time = None


def handle_json_data(data, address):
    """Process incoming JSON sensor data and add to database"""
    try:
        json_data = json.loads(data.decode("utf-8"))# parse JSON data
        current_time = datetime.now()
        max_length, timestamps = calculate_timestamps(json_data, current_time) 
        if max_length == 0:
            return True  # No data to process
        # Process each reading
        for i in range(max_length):
            # Create reading object with timestamp
            reading = {'timestamp': timestamps[i].isoformat()}
            for key in KEYS_LIST: # Extract values for each sensor key and add to timestamp
                reading[key] = validate_and_extract(json_data, key, i)
            add_data(reading)   
        return True   
    except Exception as e:
        log(f"Error processing JSON data: {str(e)}")
        return False
    
def calculate_timestamps(json_data, current_time):
    """
    Calculate timestamps for sensor readings based on array lengths.
    
    Args:
        json_data: Dictionary of sensor readings
        current_time: Current time
        
    Returns:
        Tuple of (max_length, list_of_timestamps)
    """
    global prev_time
    max_length = 0
    for key in KEYS_LIST:
        if key in json_data and isinstance(json_data[key], list):
            max_length = max(max_length, len(json_data[key]))
    if max_length == 0:
        return 0, []  # No data to process
    if prev_time is None:# initialize prev_time if first data
        prev_time = current_time - timedelta(seconds=max_length)
    time_interval = (current_time - prev_time) / max_length

    timestamps = [prev_time + time_interval * (i + 1) for i in range(max_length)]
    prev_time = current_time #update previtme for next data
    return max_length, timestamps
    
def validate_and_extract(data, key, index):
    if (key in data and 
        isinstance(data[key], list) and
                    data[key] and                   
                    index < len(data[key])):
        return data[key][index]
    else:
        return np.nan
    
def handle_audio_data(data,adress):
    add_audio_chunk(data)
    return

def process_vibration_data(data):
    return



audio_buffer = bytearray()
file_counter = 0
base_filename = "audio_recording"
max_buffer_size = 32018 * 2 * 10
buffer_counter = 0
def add_audio_chunk(chunk):
    global audio_buffer, buffer_counter
    audio_buffer.extend(chunk)
    buffer_counter += 1
    if buffer_counter >= 10:
        buffer_counter = 0
        calculate_db()
    if len(audio_buffer) >= max_buffer_size:
        log("saving audio data")
        save_buffer()
def save_buffer():
    global audio_buffer, file_counter
    if len(audio_buffer)<= 0:
        return "no audio to save"
    os.makedirs("audio_files", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("audio_files",f"{base_filename}_{timestamp}_{file_counter}.wav")

    audio_array = np.frombuffer(audio_buffer,dtype=np.int16)
    with  wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16 bits
        wav_file.setframerate(32018)  # sample rate
        wav_file.writeframes(audio_array.tobytes())
    file_counter += 1
    audio_buffer = bytearray()
def calculate_db():
    global audio_buffer
    try:
        # Make sure we have enough data
        if len(audio_buffer) < 1000:
            log("Not enough audio samples for dB calculation")
            return np.nan
        time = datetime.now()
        samples = np.frombuffer(audio_buffer[-1000:], np.int16)
        max_amplitude = 2**15-1
        squared = np.square(samples.astype(np.float64))
        rms = np.sqrt(np.mean(squared))

        if rms <= 0 or rms < 1e-10:
            log(f"Audio signal too quiet for dB calculation (RMS: {rms})")
            db = -60.0  # very low db == silence
        else:
            db = 20 * math.log10(rms / max_amplitude)
            log(f"Calculated dB level: {db}")
        db_data = {
            'timestamp': time.isoformat()
        }
        for key in KEYS_LIST:
            if key == 'DB':
                db_data[key] = db
            else:
                db_data[key] = np.nan
        return add_data(db_data)
    except Exception as e:
        log(f"Error calculating dB level: {str(e)}")
        return np.nan