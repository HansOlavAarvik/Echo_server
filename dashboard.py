import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
import asyncio
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from datetime import datetime
from database import recent_data
from div import log_setup, log
log_setup()

app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
    requests_pathname_prefix="/dashboard/",
    assets_folder="assets",
    serve_locally=True,
    suppress_callback_exceptions=True
)
server = app.server
### dashboard components
def create_interval():
    return dcc.Interval(
        id="interval-component",
        interval=1000,
        n_intervals=0
    )
def wrap(*input):
     return dbc.Row([
                dbc.Col([
                     *input
                ])
            ])
def colwrap(*input):
     return dbc.Col([
                     *input
                ])
def rowwrap(*input):
          return dbc.Row([
                     *input
                ])
def create_header():
    return html.Div([
        html.H1("ECHO Monitor Dashboard")
    ])
def create_device_selector():
     return wrap(html.Div([
                dcc.Dropdown(
               id="device_dropdown",
                options=[
                {'label': 'Device 001', 'value': 'dev001'},
                {'label': 'Device 002', 'value': 'dev002'},
                {'label': 'Device 003', 'value': 'dev003'}
            ],
            value='dev001'
               )
     ]))
def create_temp():
    return wrap(html.Div([
        html.H3("Temperature"),
        dcc.Graph(id="temperature_graph",className="mt-4")
    ]))
def create_humid():
    return  wrap(html.Div([
                html.H3("Humidity",className="mt-4"),
                dcc.Graph(id="humidity_graph")
    ]) 
    )
def create_acoustics():
        return wrap(html.Div([
             dbc.Card([
                dbc.CardBody([
                html.H4("Acoustics",className="card-title"),
                html.P("info",className="card-text",),
                dbc.Button("Play", color="primary", className="me-2"),
                dbc.Button("Pause", color="primary", className="me-2"),
                dbc.Button("Stop", color="primary", className="me-2")
            ])
        ])
    ]))
def create_vib():
    return wrap(html.Div([
        html.H3("Vibration"),
        dcc.Graph(id="vibration_graph")
    ]))
def create_tof():
    return wrap(html.Div([
        dbc.Card(
            dbc.CardBody([
                html.H4("Door status", className="card-title"),
                html.P("info",className="card-text",),
                dbc.Button("Click here", color="primary"),
        ])
    )
    ]))

### common graph layout
def graph_layout():
    return {"height": 300,
             "margin": {"t": 10, "b": 30, "l": 10, "r": 10}
             }
### fetch data and draw graph
def create_dummy_graph(y_reading):
    dummy_df = pd.DataFrame({
        'timestamp': [
            (datetime.now() - pd.Timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ],
        y_reading: [0, 0]
    })
    
    # Use graph_objects directly instead of express to avoid the Plotly error
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dummy_df['timestamp'], y=dummy_df[y_reading], mode='lines'))
    
    fig.update_layout(
        annotations=[{
            'text': f"No data available for {y_reading}",
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper',
            'x': 0.5,
            'y': 0.5
        }],
        **graph_layout()
    )
    return fig

def create_sensor_graph(y_reading,y_reading_secondary = None):
    data = recent_data()
    #log(data)
    if data.empty:
        return create_dummy_graph(y_reading)
    if y_reading not in data.columns:
        log(f"Missing required column: {y_reading} or timestamp")
        return create_dummy_graph(y_reading)
    if "timestamp" not in data.columns:
         log(f"Missing required column: {y_reading} or timestamp")
         return create_dummy_graph(y_reading)   
    if y_reading_secondary is not None:
        fig = create_multi_plot_graph(y_reading,y_reading_secondary, data)
    else:
        fig = create_single_plot_graph(y_reading, data)
    return fig
             
def create_multi_plot_graph(y_reading,y_reading_secondary,data):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    y1_min, y1_max = min(data[y_reading]), max(data[y_reading])
    y2_min, y2_max = min(data[y_reading_secondary]), max(data[y_reading_secondary])
    y_min = min(y1_min, y2_min)
    y_max = max(y1_max, y2_max)
    y_range = [y_min - 0.1 * (y_max - y_min), y_max + 0.1 * (y_max - y_min)]

    
    fig.add_trace(
        go.Scatter(
            x=data["timestamp"], 
            y=data[y_reading], 
            mode='lines+markers',
            name=y_reading
        ),
        secondary_y=False
    )
    fig.add_trace(go.Scatter(
        x=data["timestamp"], 
        y=data[y_reading_secondary], 
        mode='lines+markers',
        name=y_reading_secondary
        ),secondary_y=True
    )
    fig.update_yaxes(title_text=y_reading,range=y_range, secondary_y=False)
    fig.update_yaxes(title_text=y_reading_secondary,range=y_range, secondary_y=True)
    fig.update_layout(**graph_layout())
    return fig   
def create_single_plot_graph(y_reading,data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x=data["timestamp"], 
            y=data[y_reading], 
            mode='lines+markers',
            name=y_reading
    ))
    fig.update_layout(**graph_layout())
    return fig

### callback functions
@callback(
    Output('temperature_graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_temperature_graph(n_intervals):
    return create_sensor_graph("Inside_temperature","Outside_temperature")
@callback(
    Output('humidity_graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_humidity_graph(n_intervals):
    return create_sensor_graph("Inside_humidity","Outside_humidity")
@callback(
    Output('vibration_graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_vibration_graph(n_intervals):
    return create_sensor_graph("Vibration")


### layout 
app.layout = dbc.Container([
    create_header(),
    create_device_selector(),
    create_temp(),
    create_humid(),
    create_vib(),
    create_tof(),
    create_acoustics(),
    create_interval()
], fluid=True)



