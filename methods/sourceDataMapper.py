import logging
import time
from time import sleep

import numpy as np
import pandas as pd
import schedule

from finvizfinance.group.overview import Overview as Goverview
from finvizfinance.group.valuation import Valuation as Gvaluation
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.valuation import Valuation
from utilities.constant import AVG_METRIC_COLUMNS, COLUMNS, INDEX, SECTORS
from utilities.redis import (check_data_from_redis, fetch_data_from_redis,
                             save_data_to_redis)

logging.basicConfig(level = logging.INFO)

pd.options.mode.chained_assignment = None  # default='warn'

class SourceDataMapperService:

    def __init__(self):
        self.g_overview = Goverview()
        self.g_valuation = Gvaluation()
        self.f_valuation = Valuation()
        self.f_ownership = Ownership()
        self.f_technical = Technical()
        self.f_performance = Performance()
        self.financial = Financial()
        self.ticker = Ticker()

    def get_data_from_finviz(self,sector, index):
        data_from_finviz = []
        for function in [self.f_valuation, self.financial, self.f_technical, self.f_ownership]:
            sleep(1)  # Adding sleep
            filter_dic = {"Sector": sector, "Index": index}
            function.set_filter(filters_dict=filter_dic)
            data = function.screener_view()
            if data is None:
                logging.info(f"No data found for {function}")
                return pd.DataFrame()
            data_from_finviz.append(data) 
        data_from_finviz = pd.concat(data_from_finviz, axis = 1)
        return self.clean_data(data_from_finviz)
    
    def clean_data(self,df):
        df = df.replace(np.nan,0)
        df = np.round(df, decimals=3)
        return df.T.drop_duplicates().T

    def get_avg_metric_df(self):
        key = 'avg_metric'
        if check_data_from_redis(key):  # Check if the value already exists in Redis
            logging.info(f"Skipping {key} as it already exists in Redis")
            return fetch_data_from_redis(key)
        overview = self.g_overview.screener_view(group='Sector', order='Name')
        valuation = self.g_valuation.screener_view(group='Sector', order='Name')
        df = pd.concat([overview, valuation], axis=1, join='inner')
        df = df.T.drop_duplicates().T
        df = df[AVG_METRIC_COLUMNS]
        df=df.applymap(str) # converting all the data to string for keeping data types simple
        data = self.map_to_schema(df,True)
        save_data_to_redis (data, key)
        return data

    def map_to_schema(self, df, is_avg_metric):
        columns = {"P/E": "pe", 
                    "Fwd P/E" : "fpe",
                    "P/B": "pb", 
                    "P/C":"pc", 
                    "Dividend":"dividend", 
                    "PEG" : "peg"}
        if is_avg_metric == False:
            columns.update({"Insider Own" : "insider_own", 
                    "ROI":"roi",
                    "ROE":"roe",
                    "Beta" : "beta",
                    "Price" :"price"})
        else:
            columns.update({"Name":"Sector"})
        df.rename(columns=columns, inplace=True)
        
        # Drop duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        
        return df        

    def get_all_data(self):
        key = 'any-sector-index'
        if check_data_from_redis(key):
                return fetch_data_from_redis(key)
        dfs = []  # List to hold DataFrames
        for index in INDEX:
            for sector in SECTORS:
                dfs.append(self.get_data_by_index_sector(index,sector))
        combined_data = pd.concat(dfs)  # Combine all DataFrames
        save_data_to_redis(combined_data, key) # need to check if i can make this indepedent so the return is not blocked by this


    def get_data_by_index_sector(self,index,sector):
        logging.info(f"Fetching data for {index} and {sector}")
        index_key = index.replace(" ", "_")
        sector_key = sector.replace(" ", "_")
        key = f"{index_key}_{sector_key}"
        if check_data_from_redis(key):
            return fetch_data_from_redis(key)
        logging.info(f"Data not found in Redis for key {key}")
        df = self.get_data_from_finviz(sector, index)
        if not df.empty:
            df = df[COLUMNS]
            df["Sector"] = sector
            df["Index"] = index
            df = df.applymap(str)
        df = self.map_to_schema(df, False)
        save_data_to_redis(df, key) # need to check if i can make this indepedent so the return is not blocked by this
        return df
                            
    def run_scheduler(self):
        logging.info('Starting Scheduler')
        # Schedule the get_screen_data() function to run every day at 10:25 pm
        schedule.every().day.at('23:02').do(lambda: self.get_avg_metric_df())
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_data_by_index(self, index):
        logging.info(f"Fetching data for {index}")
        key=index.replace(" ", "_")
        combined_data = pd.DataFrame()  # Initialize an empty DataFrame
        if check_data_from_redis(key):
            return fetch_data_from_redis(key)
        logging.info("Data not found in Redis for key {key}")
        for sector in SECTORS:
            df = self.get_data_by_index_sector(index, sector)
            combined_data = pd.concat([combined_data, df])  # Combine all DataFrames
        save_data_to_redis(self.map_to_schema(combined_data, False), key=key)  # need to check if i can make this independent so the return is not blocked by this
        return combined_data
    






    



