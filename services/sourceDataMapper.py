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
from utilities.constant import (AVG_MERIC_SCHEMA, AVG_METRIC_COLUMNS,
                                METRIC_COLUMNS, METRIC_SCHEMA, SECTORS)
from utilities.redis_data import redis_manager

logging.basicConfig(level = logging.INFO)

pd.options.mode.chained_assignment = None

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
            try:
                # Create filter dictionary based on what we have
                filter_dic = {}
                if sector and sector != 'Any':
                    filter_dic["Sector"] = sector
                if index and index != 'Any':
                    filter_dic["Index"] = index
                
                # Only set filter if we have valid filters
                if filter_dic:
                    function.set_filter(filters_dict=filter_dic)
                
                data = function.screener_view()
                if data is None:
                    logging.info(f"No data found for {function}")
                    continue
                data_from_finviz.append(data)
            except Exception as e:
                logging.warning(f"Error fetching data from {function}: {e}")
                continue
        
        if not data_from_finviz:
            return pd.DataFrame()
        
        return self.clean_data(pd.concat(data_from_finviz, axis = 1))
    
    def clean_data(self,df):
        df = df.replace(np.nan,0)
        df = np.round(df, decimals=3)
        return df

    def get_avg_metric_df(self):
        """Get average metrics from Redis or fetch from Finviz"""
        df = redis_manager.get_average_metrics()
        if not df.empty:
            logging.info("Retrieved average metrics from Redis")
            return df
        
        logging.info("Fetching average metrics from Finviz")
        overview = self.g_overview.screener_view(group='Sector', order='Name')
        valuation = self.g_valuation.screener_view(group='Sector', order='Name')
        df = pd.concat([overview, valuation], axis=1, join='inner')
        df = df.T.drop_duplicates().T
        df = df[AVG_METRIC_COLUMNS]
        df = df.applymap(str) # converting all the data to string for keeping data types simple
        data = self.map_to_schema(df, True)
        redis_manager.save_average_metrics(data)
        return data

    def map_to_schema(self, df, is_avg_metric):
        columns = AVG_MERIC_SCHEMA
        if is_avg_metric == False:
            columns = METRIC_SCHEMA
        df.rename(columns=columns, inplace=True)
        # Drop duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        return df        

    def get_data_by_index_sector(self,index,sector):
        """Get stock data by index and sector from Redis or fetch from Finviz"""
        logging.debug(f"Fetching data for {index} and {sector}")
        
        # Try to get from Redis first
        df = redis_manager.get_stock_data(index, sector)
        if not df.empty:
            logging.debug(f"Retrieved data from Redis for {index}:{sector}")
            return df
        
        logging.info(f"Data not found in Redis for {index}:{sector}, fetching from Finviz")
        
        # Handle the case where we want all sectors for a specific index
        if sector == 'Any':
            # First try to get the general cached data for this index
            df = redis_manager.get_stock_data(index, 'Any')
            if not df.empty:
                logging.debug(f"Retrieved general {index} data from Redis")
                return df
            
            # Get data for all sectors
            all_data = []
            for s in SECTORS:
                try:
                    sector_data = self.get_data_from_finviz(s, index)
                    if not sector_data.empty:
                        all_data.append(sector_data)
                except Exception as e:
                    logging.warning(f"Error fetching data for sector {s}: {e}")
                    continue
            
            if all_data:
                df = pd.concat(all_data, ignore_index=True)
            else:
                df = pd.DataFrame()
        else:
            # Get data for specific sector
            df = self.get_data_from_finviz(sector, index)
        
        if not df.empty:
            try:
                df = df[METRIC_COLUMNS]
                df['Sector'] = sector
                df['Index'] = index
                df = df.applymap(str)
                df = self.map_to_schema(df, False)
                redis_manager.save_stock_data(df, index, sector)
                return df
            except KeyError as e:
                logging.error(f"KeyError in get_data_by_index_sector: {e}")
                return pd.DataFrame()
        else:
            logging.warning(f"No stock data found for {index}:{sector}")
            return pd.DataFrame()
                            
    def run_scheduler(self):
        logging.info('Starting Scheduler')
        # Schedule the get_screen_data() function to run every day at 10:25 pm
        schedule.every().day.at('23:02').do(lambda: self.get_avg_metric_df())
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(1)

    def get_data_by_index(self, index):
        """Get all data for an index, using cached general data if available"""
        logging.debug(f"Getting data for {index}")
        
        # First try to get the general cached data for this index
        df = redis_manager.get_stock_data(index, 'Any')
        if not df.empty:
            logging.debug(f"Retrieved general {index} data from Redis with {len(df)} records")
            return df
        
        logging.info(f"General {index} data not found in Redis, fetching individual sectors")
        # Fallback to fetching individual sectors and combining
        combined_data = pd.DataFrame()  # Initialize an empty DataFrame
        for sector in SECTORS:
            df = self.get_data_by_index_sector(index, sector)
            if not df.empty:
                combined_data = pd.concat([combined_data, df], ignore_index=True)  # Combine all DataFrames
        
        # Ensure the combined data has the proper schema
        if not combined_data.empty:
            combined_data = self.map_to_schema(combined_data, False)
            
        
        return combined_data
    

    def get_avg_metric_per_sector(self,sector):
        df = self.get_avg_metric_df()
        if sector != 'Any':
            df = df[df['Sector'] == sector]  # Filter where Sector value is sector
            df = df.drop(columns = ['Sector'])
            df = df.astype(float)
            df = df.squeeze() # to convert it to series 
            self.avg_metric_df = df
        else:
            df = df.drop(columns = ['Sector'])
            df = df.astype(float)
            df = df.mean(axis=0)
            self.avg_metric_df = df.astype(float)
        return df




    



