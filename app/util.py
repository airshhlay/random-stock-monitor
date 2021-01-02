import yfinance as yf
import csv
import pandas as pd
from pathlib import Path
import dash_core_components as dcc
import dash_html_components as html
import datetime
import plotly.express as px

default_columns = ['Name', 'Symbol', 'Sector', 'Country', 'Industry']
# # override yfinance default table for pandas df

# METHODS TO SET UP MONITORING
def setup_monitoring(state):
    df = create_new_dataframe(state, 5)
    info = extract_dataframe_into_dict(df)
    tickers = extract_tickers(df)

    state.start()
    state.store_company_info(info)
    state.store_tickers(tickers)

    pull_data(state)

# read data from file and select random rows
def create_new_dataframe(state, number):
    exchange = state.get_exchange()
    data_file = Path('app/data/exchange/{exchange}.csv'.format(exchange=exchange))
    df = pd.read_csv(data_file)
    return df[default_columns].sample(5)

def extract_dataframe_into_dict(df):
    res = {}
    for index, row in df.iterrows():
        coy_info = {}
        for col_name in default_columns:
            if col_name != 'Symbol':
                coy_info[col_name] = row[col_name]
        res[row['Symbol']] = coy_info
    return res

# extract a list of tickers
def extract_tickers(df):
    return df['Symbol'].values.tolist()

# YFINANCE METHODS
def get_closing_prices(state):
    tickers = state.get_tickers()
    formatted_tickers = " ".join(map(str, tickers))
    data = yf.download(formatted_tickers, interval='1d', start=state.get_today(), end=state.get_today(), group_by='ticker', threads='True')
    return data

def pull_data(state):
    curr_date = state.get_today()
    # pull new data
    data = get_closing_prices(state)
    print(data)
    updates = []
    updates.append(curr_date)
    # check if any new dates
    for ticker in state.get_tickers():
        if ticker not in data.values or not data[ticker]['Close'] == data[ticker]['Close']:
            updates.append('')
        elif data[ticker]['Close'] != curr_date:
            updates.append('')
        else:
            updates.append(data[ticker]['Close'])
    print('----UPDATES----')
    print(updates)
    # state.add_df_column(curr_date, updates)
    state.add_df_row(updates)

def refresh(state):
    # refresh date container
    state.update_current_date()
    pull_data(state)

def stop(state):
    state.stop()

def clear(state):
    state.clear()

# RENDER FUNCTIONS
# returns current monitoring state, what is being monitored etc
def render_app_info(state):
    return [
        html.H5("Is Monitoring: {monitoring}".format(monitoring=state.is_monitoring())),
        html.H3("Current Tickers:{tickers}".format(tickers=state.get_tickers())),

        html.H3("Current Stock Exchange:{stock_exchange}".format(stock_exchange=state.get_exchange())),
    ]

def render_dates(state):
    return [
        html.H5("Start Date: {date}".format(date=state.get_start_date())),

        html.H5("Current Date: {date}".format(date=state.get_today())),
    ]

def render_tabs(state):
    tabs = []
    tickers = state.get_tickers()
    ticker_index = 0
    for ticker in tickers:
        info = state.get_data()[ticker]
        tab_info = render_tab_info(info)
        # graph = html.Div()
        graph = render_graph(ticker_index, state)
        ticker_index += 1
        tab = dcc.Tab(
            id=ticker,
            label=ticker,
            children=[
                tab_info,
                graph,
            ]
        )
        tabs.append(tab)
    return [dcc.Tabs(tabs)]

# returns the container containing the name, country, sector and other basic info of the chosen stock
def render_tab_info(info):
    return html.Div(
        id='container-tab-info',
        children=[
            html.H5('Name: {}'.format(info['Name'])),
            html.H5('Country: {}'.format(info['Country'])),
            html.H5('Sector: {}'.format(info['Sector'])),
            html.H5('Industry: {}'.format(info['Industry'])),
        ]
    )

# returns the graph containing the stock price info
def render_graph(index, state):
    df = state.get_dataframe()
    try:
        row = df.iloc[:,index]
        fig = px.line(df, x=df.columns, y=df.columns, title='Change in Closing Price')
        return dcc.Graph(
            figure=fig
        )
    except IndexError:
        return html.H3(
            "Unable to download data, this symbol may have been delisted or there is no existing data for this time period yet"
        )
    
def render_default_layout():
    return [
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