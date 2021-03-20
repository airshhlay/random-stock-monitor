import datetime
from pathlib import Path
from json.decoder import JSONDecodeError
import json
import pickle
import pandas as pd
# maintains the state of monitoring
class State():
    def __init__(self, exchange):
        # paths of required files
        # self.df_path = Path('app/storage/{}-dataframe.txt'.format(exchange))
        self.json_path = Path('app/storage/{}.json'.format(exchange))
        # one pickle file for each ticker
        self.pickle_pathstr = 'app/storage/closing_prices/{}.txt'
        self.exchange = exchange

        # individual dataframes for each ticker
        self.individual_df = {} 

        self.data = {}
        self.df = None

        self.load_json()
        self.load_pickles()

        # update the current date when the app is loaded
        self.update_current_date()
        self.update_json()

    # GETTER METHODS
    def get_days_monitored(self):
        if self.data['start-date'] and self.data['current-date']:
            return get_today() - self.start_date
        else:
            return None

    def get_tickers(self):
        if 'tickers' in self.data:
            return self.data['tickers']
        else:
            return None
        
    def get_exchange(self):
        return self.exchange
            
    def get_dataframe(self, ticker):
        if ticker in self.individual_df:
            return self.individual_df[ticker]
        else:
            return None # no closing price avail yet

    def get_data(self):
        return self.data

    def get_today(self):
        return datetime.date.today().strftime('%Y-%m-%d')

    def get_start_date(self):
        return self.data['start-date']

    def is_monitoring(self):
        if 'monitoring' not in self.data:
            return False
        else:
            return self.data['monitoring']

    # UPDATE AND STORING METHODS
    # load the json file from storage
    def load_json(self):
        if self.json_path.is_file():
            # file exists
            try:
                with open(self.json_path, 'r') as f:
                    self.data = json.load(f)
            except JSONDecodeError:
                # empty file
                pass
        else:
            # create new file
            f = open(self.json_path, 'x')

    # load the inidividual closing price dataframes for each ticker
    def load_pickles(self):
        tickers = self.get_tickers()
        if tickers:
            for ticker in tickers:
                pickle_path = Path(self.pickle_pathstr.format(ticker))
                if pickle_path.is_file():
                    self.individual_df[ticker] = pd.read_pickle(pickle_path)
                else:
                    # make wide table
                    self.individual_df[ticker] = pd.DataFrame(columns=['close']).T 


    def update_current_date(self):
        self.data['current-date'] = self.get_today()

    def update_json(self):
        with open(self.json_path, 'w') as f:
            # print(self.data)
            json.dump(self.data, f)

    # def update_pickle(self):
    #     self.df.to_pickle(self.df_path)
    
    def update_pickles(self):
        tickers = self.get_tickers()
        if tickers:
            for ticker in ticker:
                if ticker in self.individual_df:
                    pickle_path = Path(self.pickle_pathstr.format(ticker))
                    df = self.individual_df[ticker]
                    df.to_pickle(pickle_path)
                else:
                    # print(ticker + ' is not in current dictionary')
                    pass

    def update_pickle(self, ticker):
        if ticker in self.individual_df:
            pickle_path = Path(self.pickle_pathstr.format(ticker))
            df = self.individual_df[ticker]
            df.to_pickle(pickle_path)
        else:
            print(ticker + ' is not in current dictionary')

    def store_tickers(self, tickers):
        self.data['tickers'] = tickers

    # def store_dataframe(self, df):
    #     self.df = df
    #     self.update_pickle()

    def store_company_info(self, info):
        self.data.update(info)

    def add_closing_price(self, ticker, date, closing_price):
        if ticker in self.individual_df:
            row_df = pd.DataFrame([closing_price], index=date)
            updated_df = self.concat_existing_dataframe(ticker, row_df)
            print('updated: ', str(updated_df))
            update_pickle(ticker)
        else:
            print(ticker + ' is not in current dictionary')

    def concat_existing_dataframe(self, ticker, update_df):
        if ticker in self.individual_df:
            existing_df = self.individual_df[ticker]
            updated_df = pd.concat([existing_df, update_df], axis=1)
            update_pickle(ticker)
        else:
            print(ticker + ' is not in current dictionary')

    # START AND STOP METHODS
    def start(self):
        self.data['monitoring'] = True
        self.data['start-date'] = self.get_today()
        self.update_json()
        
    def stop(self):
        self.data['monitoring'] = False
        self.update_json()
        # add methods to save data (make it downloadable)
    
    def clear(self):
        self.data = {}
        if self.json_path.is_file():
            Path.unlink(self.json_path)
        if Path(self.pickle_pathstr).is_file():
            Path.unlink(self.pickle_pathstr)