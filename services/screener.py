import logging

import numpy as np
import pandas as pd

import enums.enum as enum
from services.annualReturn import AnnualReturn
from services.data_fetcher import fetch_stock_data_sync

pd.options.mode.chained_assignment = None  # default='warn'

from utilities.pickle import pickle

logging.basicConfig(level = logging.INFO)

pickle = pickle()
annualReturn = AnnualReturn()

class Screener():

    # init method or constructor
    def __init__(self):
        self.index = 'S&P 500' #default
        self.sector = 'Any'
     
    def get_sp500_data(self):
        """Get S&P 500 data for portfolio building"""
        return self.get_screener_data()

    def get_screener_data(self):
        try:
            # Use the new async data fetcher
            result = fetch_stock_data_sync(self.index, self.sector)
            if result.success and not result.data.empty:
                data = annualReturn.update_with_return_data(result.data)
                return data
            else:
                logging.error(f"Failed to fetch data: {result.error}")
                return pd.DataFrame()
        except Exception as e:
            logging.error(f"Error in get_screener_data: {e}")
            return pd.DataFrame()
    
    def update_key_sector_and_index(self,sector,index):
        self.index = index
        self.sector = sector   
          
    def get_title(self):
        return "{index} {sector} Data".format(sector = self.sector, index =self.index)


    
   
            
