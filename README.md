# Server for ECHO environment monitor device

## Description

Server application for environment monetoring device. Device sends data via UDP to static IP.
Sends following data:
-Audio 32018hz
-Temperature (two sensors) 1hz
-Humidity  (two sensors) 1hz
-Vibration 400hz
-Tof 1hz
-Status 1hz

Server displays data on graphs and has a integrated audio player. Displays simple analasys of audio. It also stores readings in a database.


## installation

- Make sure have installed python 3.9 or newer, you can check python version by running:
```powershell
 python --version
```

- Install potery
```powershell
pip install poetry
```
- Navigate to Echo_server/
- Install dependencies with poetry:
```powershell
poetry install
```
- run server with
```powershell
poetry run python main.py
```

## To do
### High prio
- Display Tof data
- Record alarm threshold
- Function for sending threshold
- Display audio frequency analasys
- Add timeline
### Low prio
- Integrate continious audio player
- Take status signal

