import logging

import numpy as np
import pandas as pd

import enums.enum as enum
import utilities.helper as helper
from methods.annualReturn import get_annual_return_data
from methods.sourceDataMapper import SourceDataMapperService
from utilities.redis import (check_data_from_redis, fetch_data_from_redis,
                             save_data_to_redis)

pd.options.mode.chained_assignment = None  # default='warn'

from utilities.pickle import pickle

logging.basicConfig(level = logging.INFO)

pickle = pickle() 
SourceDataMapperService = SourceDataMapperService()

class stock():

    # init method or constructor
    def __init__(self):
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.screener_df = pd.DataFrame()
        self.index = 'S&P 500' #default
        self.sector = 'Any'
        self.sp500_data = pd.DataFrame()
        self.key = 'SP_500_Any_screen_data' #default
     
    def update_with_return_data(self,df):
        helper.round_decimal_place(df,['insider_own','dividend','roi','roe'])
        #df = self.combine_with_return_data(df)  need to investigate why this is not working
        df = df.drop_duplicates()
        df  = df.replace(np.nan,0)
        df = df.applymap(str)
         #the dataTable throws invalid json if the dtype is not string. Workaround solution for now
        return df

    def get_screener_data(self):
        if check_data_from_redis(self.key):
            return fetch_data_from_redis(self.key)
        data = self.update_with_return_data(SourceDataMapperService.get_data_by_index_sector(self.index,self.sector))
        save_data_to_redis(data,self.key)
        return data

    def update_avg_metric_dic(self,sector):
        df = SourceDataMapperService.get_avg_metric_df()
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
        self.avg_metric_df = df
        return self.avg_metric_df
 
   # we can use return_risk_ratio as a multiplier instead of addition. There is a possibility 
   #of calculating the coefficient of each of these attributes so that we give more weights to more relevant attribute
   # apply AI or ML to calculate the coefficient
    def calculate_strength_value(self, df, stock_type):
        logging.info(f"Calculating strength value for {stock_type} Stock")     
        attributes = ["dividend","pe","fpe","pb","beta" ] #,"return_risk_ratio"] remove after annaul return is fixed
        df["strength"] = 0
        for col in attributes:
            df[col].replace('nan', np.nan, inplace=True)
            df[col].replace('None', np.nan, inplace=True)
            if col == 'beta':
                df["strength"] = df["strength"] - np.where(df[col].isnull(),0,df[col].astype(float))
            elif col == 'return_risk_ratio':
                df["strength"] = df["strength"] + np.where(df[col].isnull(),0,df[col].astype(float))
            else:
                new_col = np.where(df[col].isnull(), 0, df[col].astype(float) - self.avg_metric_df[col])
                new_col = np.divide(1,self.avg_metric_df[col])*new_col #percentage change 
                if col == 'dividend' : 
                    df["strength"] = df["strength"] + new_col
                else:
                    df["strength"] = df["strength"] - new_col
        if stock_type == enum.StockType.VALUE.value:
            df["strength"] = df["strength"]
        elif stock_type == enum.StockType.GROWTH.value:
            df["strength"] = -1* df["strength"]
        else:
            raise ValueError("Stock Type must be Value or Growth")
        df = df.replace(np.nan,0)
        df = np.round(df, decimals=3) 
        df = df.sort_values(by=["strength"] , ascending=[False])   
        return df
    
    def get_risk_tolerance_data(self,risk_tolerance,df):
        if risk_tolerance == enum.RiskEnum.HIGH.value:
            df = df[df['expected_annual_risk'].astype(float) > .7]
        elif risk_tolerance == enum.RiskEnum.MEDIUM.value:
            df = df[(df['expected_annual_risk'].astype(float) > .4) &(df['expected_annual_risk'].astype(float) < .6)]
        elif risk_tolerance == enum.RiskEnum.LOW.value:
            df = df[(df['expected_annual_risk'].astype(float) > .15) &(df['expected_annual_risk'].astype(float) < .4)]
        return df

    # we can cache this data 
    def combine_with_return_data(self,df):
        return_rate = get_annual_return_data()
        combined_data = pd.merge(df, return_rate, on='Ticker', how='inner')
        combined_data = np.round(combined_data, decimals=3)
        return combined_data
    
    def update_strength_data(self,sector,index,stock_type):
        sector_index_data = SourceDataMapperService.get_data_by_index_sector(sector,index)
        sector_index_data = self.update_with_return_data(sector_index_data)
        self.update_avg_metric_dic(sector)
        strength_calculated_df = self.calculate_strength_value(sector_index_data,stock_type)
        #strength_calculated_df  = strength_calculated_df.fillna(0)
        return strength_calculated_df
    
    def update_key_sector_and_index(self,sector,index):
        index_key = index.replace(" ", "_")
        sector_key = sector.replace(" ", "_")
        self.key = f"{index_key}_{sector_key}_screen_data"
        self.index = index
        self.sector = sector
          
    def get_title(self):
        return "{index} {sector} Data".format(sector = self.sector, index =self.index)


    
   
            
