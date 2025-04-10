
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
        for i in range(max_length):# Process each reading
            reading = {'timestamp': timestamps[i].isoformat()}# Create reading object with timestamp
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
        value = data[key][index]
        scaled_value = scale_if_needed(key, value)
        return value ##scaled_value
    else:
        return np.nan
    
def scale_if_needed(key, value):
    """Scale sensor values as all values are sent from microcontroller as 16bit int"""
    # Check for None or np.nan first
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
        
    # Now we know value is a number and not None
    if key == "Time_of_flight":
        return value/10
    elif key in ["Inside_temperature", "Outside_temperature"]:
        return value/100 
    elif key in ["Inside_humidity", "Outside_humidity"]:
        return value/100
    else:
        return value

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
    if buffer_counter >= 40:
        buffer_counter = 0
        calculate_db()
    if len(audio_buffer) >= max_buffer_size:
        #log("saving audio data")
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
        # Make sure there is enough data
        if len(audio_buffer) < 1000:
            #log("Not enough audio samples for dB calculation")
            return np.nan
        time = datetime.now()
        samples = np.frombuffer(audio_buffer[-1000:], np.int16)
        max_amplitude = 2**15-1
        squared = np.square(samples.astype(np.float64))
        rms = np.sqrt(np.mean(squared))

        if rms <= 0 or rms < 1e-10:
            #log(f"Audio signal too quiet for dB calculation (RMS: {rms})")
            db = -60.0  # very low db == silence
        else:
            db = 20 * math.log10(rms / max_amplitude)
            #log(f"Calculated dB level: {db}")
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
    


# Add this function to get audio file metadata
def get_audio_metadata(file_path):
    """Get metadata from an audio file"""
    try:
        with wave.open(file_path, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            duration = n_frames / framerate
            
            return {
                "channels": channels,
                "sample_width": sample_width,
                "framerate": framerate,
                "n_frames": n_frames,
                "duration": duration,
                "file_size": os.path.getsize(file_path)
            }
    except Exception as e:
        log(f"Error getting audio metadata: {e}")
        return {}


    ### future work, automatic cleanup of audio files
    # def cleanup_old_audio_files(max_files=100, max_age_days=7):
    # """Delete old audio files to prevent filling up disk space"""
    # try:
    #     files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
        
    #     # Sort by creation time (oldest first)
    #     files.sort(key=os.path.getctime)
        
    #     # Delete files exceeding the maximum count
    #     if len(files) > max_files:
    #         files_to_delete = files[:len(files) - max_files]
    #         for file in files_to_delete:
    #             os.remove(file)
    #             log(f"Deleted old audio file: {file}")
        
    #     # Delete files older than max_age_days
    #     cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    #     for file in files:
    #         if os.path.getctime(file) < cutoff_time:
    #             os.remove(file)
    #             log(f"Deleted aged audio file: {file}")
    # except Exception as e:
    #     log(f"Error cleaning up audio files: {e}")
