import pandas as pd
import numpy as np
import utilities.helper as helper
import utilities.bigQuery as bigQuery
import enums.enum as enum
import logging
pd.options.mode.chained_assignment = None  # default='warn'
from utilities.pickle import pickle
from cachetools import cached, TTLCache


logging.basicConfig(level = logging.INFO)

pickle = pickle() 
cache = TTLCache(maxsize=1000, ttl=86400)

class stock():

    # init method or constructor
    def __init__(self):
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.screener_df = pd.DataFrame()
        self.index = 'S&P 500' #default
        self.sector = ''
        self.sp500_data = pd.DataFrame()
     
    def get_stock_data_by_sector_and_index(self,index,sector):
        self.index = index
        self.sector = sector
        self.metric_df = bigQuery.get_stock_data(index, sector)
        helper.round_decimal_place(self.metric_df,['insider_own','dividend','roi','roe'])
        self.metric_df = self.combine_with_return_data(self.metric_df)
        self.metric_df = self.metric_df.drop_duplicates()
        self.metric_df  = self.metric_df.replace(np.nan,0)
        self.metric_df = self.metric_df.applymap(str)
         #the dataTable throws invalid json if the dtype is not string. Workaround solution for now
        return self.metric_df

    def save_screener_data(self,df):
        self.screener_df = df

    def get_screener_data(self):
        if self.screener_df.empty:
            return self.cache_sp500_data()
        return self.screener_df

    def update_avg_metric_dic(self,sector):
        if sector == 'Any':
            df = bigQuery.get_average_metric()
            df = df.drop(columns = ['Sector'])
            df = df.astype(float)
            df = df.mean(axis=0)
            self.avg_metric_df = df.astype(float)
        else:
           df = bigQuery.get_average_metric_by_sector(sector)
           df = df.drop(columns = ['Sector'])
           df = df.astype(float)
           df = df.squeeze() # to convert it to series 
           self.avg_metric_df = df
        return self.avg_metric_df
 
   # we can use return_risk_ratio as a multiplier instead of addition. There is a possibility 
   #of calculating the coefficient of each of these attributes so that we give more weights to more relevant attribute
    def calculate_strength_value(self, df, stock_type):
        attributes = ["dividend","pe","fpe","pb","beta","return_risk_ratio"]
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
        df = df.sort_values(by=["strength","expected_annual_return"], ascending=[False,False])
        return df
    
    def get_risk_tolerance_data(self,risk_tolerance,df):
        if risk_tolerance == enum.RiskEnum.HIGH.value:
            df = df[df['expected_annual_risk'].astype(float) > .7]
        elif risk_tolerance == enum.RiskEnum.MEDIUM.value:
            df = df[(df['expected_annual_risk'].astype(float) > .4) &(df['expected_annual_risk'].astype(float) < .6)]
        elif risk_tolerance == enum.RiskEnum.LOW.value:
            df = df[(df['expected_annual_risk'].astype(float) > .15) &(df['expected_annual_risk'].astype(float) < .4)]
        return df

    def combine_with_return_data(self,df):
        return_rate = bigQuery.get_annual_return()
        combined_data = pd.merge(df, return_rate, on='Ticker', how='inner')
        combined_data = np.round(combined_data, decimals=3)
        return combined_data
    
    def update_strength_data(self,sector,index,stock_type):
        sector_index_data = self.get_stock_data_by_sector_and_index(index,sector)
        self.update_avg_metric_dic(sector)
        strength_calculated_df = self.calculate_strength_value(sector_index_data,stock_type)
        strength_calculated_df  = strength_calculated_df.fillna(0)
        return strength_calculated_df

    @cached(cache)
    def cache_sp500_data(self): # need to research whether storing the value in class is more effecient vs using pickle
        #if self.sp500_data.empty:
        self.sp500_data = self.get_stock_data_by_sector_and_index(sector = 'Any', index='S&P 500')
        return self.sp500_data
    
    def get_title(self):
        return "{index} {sector} Data".format(sector = self.sector, index =self.index)


    
   
            
