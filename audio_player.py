"""
Audio player components for the Dash dashboard.
This module contains the audio player component and related callback functions.
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import os
import glob
import base64
import numpy as np
import wave
from datetime import datetime
from div import log

def get_audio_files():
    """Get list of audio files from the audio_files directory"""
    try:
        # Get all .wav files in the audio_files directory
        files = glob.glob("audio_files/*.wav")
        # Sort by creation time (newest first)
        files.sort(key=os.path.getctime, reverse=True)
        return files
    except Exception as e:
        log(f"Error getting audio files: {e}")
        return []

def create_audio_filename_display(filename):
    """Format audio filename for display"""
    # Extract just the filename part without the path
    basename = os.path.basename(filename)
    # Remove the extension
    name_only = os.path.splitext(basename)[0]
    # Format timestamp part if present
    parts = name_only.split('_')
    if len(parts) >= 3:
        try:
            timestamp = f"{parts[1]}_{parts[2]}"
            timestamp = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            return f"Recording {parts[-1]} - {timestamp}"
        except:
            return basename
    return basename

def get_audio_base64_data(file_path):
    """Read audio file and convert to base64 for HTML audio element"""
    try:
        with open(file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('ascii')
            return f"data:audio/wav;base64,{audio_base64}"
    except Exception as e:
        log(f"Error reading audio file {file_path}: {e}")
        return None

def create_audio_player(wrap_func):
    """Create a minimal audio player component"""
    return wrap_func(html.Div([
        html.H3("Audio Player", className="mt-4"),
        
        # Audio file selector
        html.Div([
            html.Label("Select Recording:"),
            dcc.Dropdown(
                id="audio-file-dropdown",
                options=[],  # Will be populated by callback
                value=None,
                placeholder="Select a recording...",
                className="mb-3"
            ),
        ]),
        
        # Audio element
        html.Div([
            html.Audio(
                id="audio-player",
                controls=True,
                src="",
                style={"width": "100%"}
            ),
            
            # Simple control buttons
            html.Div([
                dbc.Button(
                    "Play", 
                    id="audio-play-button", 
                    color="primary", 
                    className="me-2"
                ),
                dbc.Button(
                    "Stop", 
                    id="audio-stop-button", 
                    color="primary", 
                    className="me-2"
                ),
                dbc.Button(
                    "Download", 
                    id="audio-download-button", 
                    color="secondary", 
                    className="me-2"
                ),
            ], className="mt-3 d-flex justify-content-center")
        ], className="mt-3"),
        
        # Hidden div for storing file path
        html.Div(id="selected-audio-path", style={"display": "none"}),
        
        # Download component
        dcc.Download(id="audio-download"),
        
        # Update interval
        dcc.Interval(
            id="audio-files-update-interval",
            interval=10000,  # 10 seconds
            n_intervals=0
        )
    ]))

def register_callbacks(app):
    """Register all callbacks for the audio player"""
    
    @app.callback(
        Output("audio-file-dropdown", "options"),
        Input("audio-files-update-interval", "n_intervals")
    )
    def update_audio_file_list(n_intervals):
        """Update the list of available audio files"""
        files = get_audio_files()
        return [{"label": create_audio_filename_display(f), "value": f} for f in files]

    @app.callback(
        [Output("audio-player", "src"),
         Output("selected-audio-path", "children")],
        Input("audio-file-dropdown", "value"),
        prevent_initial_call=True
    )
    def update_audio_player(selected_file):
        """Update the audio player source when a file is selected"""
        if not selected_file:
            return "", ""
        
        # Get base64 data for audio element
        audio_data = get_audio_base64_data(selected_file)
        return audio_data, selected_file

    @app.callback(
        Output("audio-download", "data"),
        Input("audio-download-button", "n_clicks"),
        State("selected-audio-path", "children"),
        prevent_initial_call=True
    )
    def download_selected_audio(n_clicks, file_path):
        """Download the selected audio file"""
        if not file_path:
            return None
        
        return dcc.send_file(file_path)

    # Simple play and stop functionality
    app.clientside_callback(
        """
        function(n_clicks) {
            if (n_clicks) {
                const player = document.getElementById('audio-player');
                if (player) {
                    player.play();
                }
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("audio-player", "playing", allow_duplicate=True),
        Input("audio-play-button", "n_clicks"),
        prevent_initial_call=True
    )

    @app.callback(
        Output("audio-player", "currentTime", allow_duplicate=True),
        Input("audio-stop-button", "n_clicks"),
        prevent_initial_call=True
    )
    def stop_audio(n_clicks):
        """Stop the audio"""
        # Sets current time to 0 which effectively "stops" it
        return 0