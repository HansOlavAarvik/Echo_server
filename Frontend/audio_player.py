"""
A minimal audio player for Dash that supports continuous playback.
This is a further simplified version to avoid potential issues.
"""
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import os
import glob
import base64
from datetime import datetime
from div import log


## audio player
def get_audio_files():
    """Get list of audio files from the audio_files directory"""
    try:
        # Create directory if it doesn't exist
        os.makedirs("audio_files", exist_ok=True)
        
        # Get all .wav files
        files = glob.glob("audio_files/*.wav")
        if files:
            files.sort(key=os.path.getctime, reverse=True)  # Newest first
        return files
    except Exception as e:
        log(f"Error getting audio files: {e}")
        return []

def format_filename(filename):
    """Format filename for display"""
    basename = os.path.basename(filename)
    name_only = os.path.splitext(basename)[0]
    parts = name_only.split('_')
    if len(parts) >= 3:
        try:
            timestamp = f"{parts[1]}_{parts[2]}"
            timestamp = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            return f"Recording {parts[-1]} - {timestamp}"
        except:
            return basename
    return basename

def get_audio_base64(file_path):
    """Convert audio file to base64 for HTML audio element"""
    try:
        with open(file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('ascii')
            return f"data:audio/wav;base64,{audio_base64}"
    except Exception as e:
        log(f"Error reading audio file {file_path}: {e}")
        return None

def create_audio_player(wrap_func):
    """Create a simple audio player with minimal functionality"""
    return wrap_func(html.Div([
        html.H3("Audio Player"),
        
        # Simple file selector
        html.Div([
            html.Label("Select Recording:"),
            dcc.Dropdown(
                id="audio-files-dropdown",
                options=[],
                value=None,
                placeholder="Select a recording...",
                className="mb-3"
            ),
        ]),
        
        # Simple player
        html.Div([
            html.Audio(
                id="audio-element",
                controls=True,
                src="",
                style={"width": "100%"}
            ),
            
            dbc.Button(
                "Play Selected", 
                id="play-selected-btn", 
                color="primary",
                className="mt-3"
            ),
        ]),
        
        # Update interval
        dcc.Interval(
            id="audio-refresh-interval",
            interval=5000,  # Check for new files every 5 seconds
            n_intervals=0
        )
    ]))

# Flag to prevent multiple registrations
_callbacks_registered = False

def register_callbacks(app):
    """Register callbacks for the audio player"""
    global _callbacks_registered
    
    # Skip if already registered
    if _callbacks_registered:
        log("Audio player callbacks already registered")
        return
        
    try:
        # Update available files dropdown
        @app.callback(
            Output("audio-files-dropdown", "options"),
            Input("audio-refresh-interval", "n_intervals")
        )
        def update_files_list(n_intervals):
            files = get_audio_files()
            return [{"label": format_filename(f), "value": f} for f in files]
        
        # Play selected file
        @app.callback(
            Output("audio-element", "src"),
            Input("play-selected-btn", "n_clicks"),
            State("audio-files-dropdown", "value"),
            prevent_initial_call=True
        )
        def play_selected_file(n_clicks, selected_file):
            if not n_clicks or not selected_file:
                return ""
                
            audio_data = get_audio_base64(selected_file)
            return audio_data if audio_data else ""
        
        # Client-side callback to play audio
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks) {
                    setTimeout(function() {
                        const player = document.getElementById('audio-element');
                        if (player && player.src) {
                            player.play();
                        }
                    }, 300);
                }
                return window.dash_clientside.no_update;
            }
            """,
            Output("audio-element", "playing", allow_duplicate=True),
            Input("play-selected-btn", "n_clicks"),
            prevent_initial_call=True
        )
        
        # Mark callbacks as registered
        _callbacks_registered = True
        log("Audio player callbacks registered successfully")
        
    except Exception as e:
        log(f"Error registering audio player callbacks: {e}")