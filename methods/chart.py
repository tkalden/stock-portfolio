import logging

import pandas as pd
from cachetools import TTLCache, cached
from finvizfinance.quote import finvizfinance
from flask import Flask

import enums.enum as enum
import utilities.helper as helper
from methods.redis import redis_cache
from methods.stock import stock
from utilities.pickle import pickle

stock = stock()

class chart():
     # init method or constructor
    def __init__(self):
        self.top_dict = []
 
    def get_chart_data(self,stock_type,base_metric):
        sp_500_data = stock.get_sp500_data()
        df = sp_500_data
        if base_metric == enum.Metric.STRENGTH.value:
            stock.update_avg_metric_dic('Any')
            df = stock.calculate_strength_value(df,stock_type)
        elif base_metric == enum.Metric.DIVIDEND.value:
            df = df.sort_values(by="dividend", ascending=False)
        return self.top_stocks(df,base_metric)
       
    def top_stocks(self,df,base_metric):
        self.top_dict = []
        sectors = helper.get_sector()
        sectors.remove('Any')
        for sector in sectors:
            new_df = df[df['Sector'] == sector].head(5)
            labels = new_df["Ticker"].values.tolist()
            chart_values = pd.DataFrame()
            if base_metric == enum.Metric.STRENGTH.value:
                chart_values = new_df["strength"]
            elif base_metric == enum.Metric.DIVIDEND.value:
                chart_values = new_df["dividend"] 
            values = chart_values.values.tolist()
            self.top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        return self.top_dict
    
    def get_ticker_fundamental(self,ticker):
        logging.info("Getting stock info for %s",ticker);
        if ticker is 'TWTR':
            return None
        stock_info = finvizfinance(ticker);
        cached_data = redis_cache.get(ticker)
        if cached_data:
            # Deserialize the JSON and create a DataFrame
            return cached_data
        else:
            # If not in cache, process the data and store it
            data = stock_info.ticker_fundament();
            # Serialize and store the DataFrame in the cache
            redis_cache.set(ticker, data, ex=86400)  # Cache for 1 day
            return data
    
