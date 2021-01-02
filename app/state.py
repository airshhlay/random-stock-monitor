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
        self.df_path = Path('app/storage/{}-dataframe.txt'.format(exchange))
        self.json_path = Path('app/storage/{}.json'.format(exchange))

        self.exchange = exchange

        self.data = {}
        self.df = None

        self.load_json()
        self.load_pickle()

        # update the current date when the app is loaded
        self.update_current_date()
        self.update_json()

        print(type(self.df))

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
            
    def get_dataframe(self):
        return self.df

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

    def load_pickle(self):
        if self.df_path.is_file():
            self.df = pd.read_pickle(self.df_path)
        elif self.get_tickers():
            self.df = pd.DataFrame({
            }).T
            print(self.df)
            print('----')

    def update_current_date(self):
        self.data['current-date'] = self.get_today()

    def update_json(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.data, f)

    def update_pickle(self):
        self.df.to_pickle(self.df_path)

    def store_tickers(self, tickers):
        self.data['tickers'] = tickers
        self.update_json()

    def store_dataframe(self, df):
        self.df = df
        self.update_pickle()

    def store_company_info(self, info):
        self.data.update(info)

    def add_df_column(self, col_name, data):
        self.df[col_name] = data
        self.update_pickle()

    def add_df_row(self, update):
        self.df.append(update)
        self.update_pickle()

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
        if self.df_path.is_file():
            Path.unlink(self.df_path)