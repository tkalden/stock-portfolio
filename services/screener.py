import logging

import numpy as np
import pandas as pd

import enums.enum as enum
from services.annualReturn import AnnualReturn
from services.sourceDataMapper import SourceDataMapperService

pd.options.mode.chained_assignment = None  # default='warn'

from utilities.pickle import pickle

logging.basicConfig(level = logging.INFO)

pickle = pickle() 
SourceDataMapperService = SourceDataMapperService()
annualReturn = AnnualReturn()

class Screener():

    # init method or constructor
    def __init__(self):
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.screener_df = pd.DataFrame()
        self.index = 'S&P 500' #default
        self.sector = 'Any'
     
    def get_sp500_data(self):
        """Get S&P 500 data for portfolio building"""
        return self.get_screener_data()

    def get_screener_data(self):
        if self.sector == 'Any':
            data = annualReturn.update_with_return_data(SourceDataMapperService.get_data_by_index(self.index))
        else:
            data = annualReturn.update_with_return_data(SourceDataMapperService.get_data_by_index_sector(self.index,self.sector))
        return data
    
    def update_key_sector_and_index(self,sector,index):
        self.index = index
        self.sector = sector   
          
    def get_title(self):
        return "{index} {sector} Data".format(sector = self.sector, index =self.index)


    
   
            
