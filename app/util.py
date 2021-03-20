# import yfinance as yf
import yahoo_fin.stock_info as si
import csv
import pandas as pd
from pathlib import Path
import dash_core_components as dcc
import dash_html_components as html
import datetime
import random
import plotly.express as px

default_columns = ['Name', 'Symbol', 'Sector', 'Country', 'Industry']
# # override yfinance default table for pandas df

# METHODS TO SET UP MONITORING
def setup_monitoring(state):
    # for use with yfinance
    # df = create_new_dataframe(state, 5)
    # info = extract_dataframe_into_dict(df)
    # tickers = extract_tickers(df)
    tickers = retrieve_random_tickers(5)
    info = gather_company_info(state, tickers)
    state.start()
    state.store_company_info(info)
    state.store_tickers(tickers)

    # pull_data_yfinance(state)
    pull_data_yahoofin(state)

# for use with yahoo_fin library
# returns a LIST of num tickers, randomly selected
def retrieve_random_tickers(num):
    tickers_all = si.tickers_nasdaq()
    tickers_selected = random.sample(tickers_all, 5)
    print('Selected random tickers: ' + str(tickers_selected))
    return list(tickers_selected)

# for use with yahoo_fin library
# returns a dictionary containing info on each selected company, pulled from existing csv
def gather_company_info(state, tickers):
    exchange = state.get_exchange()
    data_file = Path('app/data/exchange/{exchange}.csv'.format(exchange=exchange))
    df = pd.read_csv(data_file)[default_columns]
    res = {}

    for ticker in tickers:
        row = df.loc[df['Symbol'] == ticker]
        # print(row)
        coy_info = {}
        for col_name in default_columns:
            if col_name != 'Symbol':
                if row[col_name] is not None:
                    print(row[col_name])
                    # row[col_name] = row[col_name].astype(str)
                    # coy_info[col_name] = row[col_name].astype(str)
                    coy_info[col_name] = row[col_name].to_string(index=False)
                    # print('----')
        res[ticker] = coy_info
        # print('-------')
        # print(ticker + ' coy info: ' + str(coy_info))

    # print('----')
    # print(res)
    return res

# for use with yahoo_fin library
# pulls data for each ticker, from start to current date
def pull_data_yahoofin(state):
    tickers = state.get_tickers()
    start_date = datetime.datetime.strptime(state.get_start_date(), '%Y-%m-%d').date() - datetime.timedelta(days=1)
    end_date = datetime.datetime.strptime(state.get_today(), '%Y-%m-%d').date() + datetime.timedelta(days=1)

    for ticker in tickers:
        update_df = si.get_data(ticker, start_date=start_date, end_date=end_date, index_as_date=True, interval='1d')
        # state.concat_existing_dataframe(ticker, update_df)
        for date, row in update_df.iterrows():
            state.add_closing_price(ticker, date.date().strftime('%Y-%m-%d'), row['close'])

    state.update_json()

# for use with yahoo_fin library
# pulls data for each ticker and refreshes the date
# note: only allow refresh twice per local session (to avoid excessive data pulling)
def refresh(state):
    # refresh date container
    state.update_current_date()
    pull_data_yahoofin(state)
    

# # for use with yfinance library
# # read data from file and select random rows
# def create_new_dataframe(state, number):
#     exchange = state.get_exchange()
#     data_file = Path('app/data/exchange/{exchange}.csv'.format(exchange=exchange))
#     df = pd.read_csv(data_file)
#     return df[default_columns].sample(5)
    

# # for use with yfinance library
# def extract_dataframe_into_dict(df):
#     res = {}
#     for index, row in df.iterrows():
#         coy_info = {}
#         for col_name in default_columns:
#             if col_name != 'Symbol':
#                 coy_info[col_name] = row[col_name]
#         res[row['Symbol']] = coy_info
#     return res

# # for use with yfinance library
# # extract a list of tickers
# def extract_tickers(df):
#     return df['Symbol'].values.tolist()

# # for use with yfinance library
# def get_closing_prices_yfinance(state):
#     tickers = state.get_tickers()
#     formatted_tickers = " ".join(map(str, tickers))
#     data = yf.download(
#         formatted_tickers,
#         interval='1d',
#         start=state.get_today(),
#         end=state.get_today(),
#         group_by='ticker',
#         threads='True'
#     )
#     return data

# # for use with yfinance library
# def pull_data_yfinance(state):
#     curr_date = state.get_today()
#     # pull new data
#     data = get_closing_prices_yfinance(state)
#     print(data)
#     updates = []
#     dates = data['Date']
#     # check if any new dates
#     for ticker in state.get_tickers():
#         if ticker not in data.values or not data[ticker]['Close'] == data[ticker]['Close']:
#             updates.append('')
#         else:
#             for date in dates:
#                 updates.append(data[ticker]['Close'])
#     print('----UPDATES----')
#     print(updates)
#     # state.add_df_column(curr_date, updates)
#     state.add_df_row(updates)

# # for use with yfinance library
# def refresh(state):
#     # refresh date container
#     state.update_current_date()
#     pull_data_yfinance(state)

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
    if tickers:
        data = state.get_data()
        print(data)
        for ticker in tickers:
            print(ticker)
            print(ticker in data)
            info = data[ticker]
            tab_info = render_tab_info(info)
            # graph = html.Div()
            graph = render_graph(ticker, state)
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
    return None

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
def render_graph(ticker, state):
    df = state.get_dataframe(ticker)
    try:
        fig = px.line(
            df,
            x=['close'],
            y=df.index,
            color=df.index,
        )
        fig.update_layout(
            title='Changes in Closing Price',
            xaxis_title='Date',
            yaxis_title='Closing Price (USD)',
            legend_title='Legend'
        )
        return dcc.Graph(
            figure=fig
        )
    except IndexError:
        return html.H3(
            "Unable to download data, this symbol may have been delisted or there is no existing data for this time period yet"
        )
    except AttributeError:
        return html.H3(
            "No available closing prices yet!"
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