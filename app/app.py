import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from state import State
import datetime
from util import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# initialise variables
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
state = State('nasdaq') # load state from store
# main app layout
app.layout = html.Div(
    id='container-main',
    children=
    [
        html.Div(
            # title of app
            id='container-headings',
            children=[
                html.H1("Random Stock Monitor"),
            ]
        ),
        html.Div(
            id='container-info',
            children=[
                html.H1(
                    'Click Begin to start monitoring!'
                )
            ]
        ),
        html.Div(
            id='container-dates',
        ),
        html.Div(
                id='container-buttons',
                children=
                [
                html.Button(
                    "Refresh Data",
                    id='button-refresh',
                    n_clicks=0,
                ),
                html.Button(
                    "Begin Monitoring",
                    id="button-begin",
                    n_clicks=0,
                ),
                html.Button(
                    "Stop Monitoring",
                    id='button-stop',
                    n_clicks=0,
                ),
                html.Button(
                    "Clear",
                    id="button-clear",
                    n_clicks=0,
                ),
                dcc.ConfirmDialog(
                    id="confirm-reset",
                    message="Are you sure you want to reset the monitoring?"
                )
            ]
        ),
        # main data tabs
        html.Div(
            id="container-tabs",
        )   
    ]
)

# begin button callback
@app.callback(
    [
        Output('container-tabs', 'children'),
        Output('container-info', 'children'),
        Output('container-dates', 'children')
    ],
    [
        Input('button-begin', 'n_clicks'),
        Input('button-stop', 'n_clicks'),
        Input('button-refresh', 'n_clicks'),
    ],
)
def button_click(begin, stop, refresh):
    global state
    ctx = dash.callback_context

    if not ctx.triggered and not state.is_monitoring():
        raise PreventUpdate
    elif ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'button-begin':
            begin_button()
        elif button_id == 'button-stop':
            stop_button()
        elif button_id == 'button-refresh':
            refresh_button()

    # render top level monitoring information
    info = render_app_info(state)
    # render all tabs and corresponding info
    tabs = render_tabs(state)
    dates = render_dates(state)
    
    return tabs, info, dates
        
def begin_button():
    global state
    if not state.is_monitoring():
        # set up the state if begin is first clicked
        setup_monitoring(state)

# refresh button callback
def refresh_button():
    global state
    if not state.is_monitoring():
        raise PreventUpdate
    refresh(state)

# stop button callback
def stop_button():
    if not state.is_monitoring():
        raise PreventUpdate

    stop(state)

# clear button callback
@app.callback(
    [
        Output('container-main', 'children'),
    ],
    [
        Input('button-clear', 'n_clicks'),
    ],
)
def clear_button(n_clicks):
    global state
    # can only be clicked once monitoring has stopped
    if n_clicks == 0 or state.is_monitoring():
        raise PreventUpdate

    default = render_default_layout()

    clear(state)
    return [default]

if __name__ == '__main__':
    app.run_server(debug=True)