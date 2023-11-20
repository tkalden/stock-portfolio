import json
import logging

import numpy as np
import pandas as pd

import enums.enum as enum
import utilities.bigQuery as bigQuery
import utilities.helper as helper
from methods.redis import redis_cache

pd.options.mode.chained_assignment = None  # default='warn'
from cachetools import TTLCache, cached

from utilities.pickle import pickle

logging.basicConfig(level=logging.INFO)

CACHED_DATA_LOG = "Cached data for %s"


class stock():

    # init method or constructor
    def __init__(self):
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.index = 'S&P 500'  # default
        self.sector = ''

    def get_stock_data_by_sector_and_index(self, index, sector):
        logging.info("Getting stock data for %s and %s", index,sector)
        cache_name = 'stock_data_' + index + '_' + sector
        cached_data = redis_cache.get(cache_name)
        if cached_data:
            self.cache_found_logging(cache_name)
            # Deserialize the JSON and create a DataFrame
            self.metric_df =  pd.read_json(cached_data.decode('utf-8'), orient='split')
            return self.metric_df
        else:
            self.update_stock_data(index, sector)
            self.cache_data_logging(cache_name)
            redis_cache.set(cache_name, self.metric_df.to_json(orient='split'), ex=86400)  # Cache for 1 day
            # the dataTable throws invalid json if the dtype is not string. Workaround solution for now
            return self.metric_df
    
    def update_stock_data(self, index, sector):
        self.index = index
        self.sector = sector
        self.metric_df = bigQuery.get_stock_data(index, sector)
        helper.round_decimal_place(self.metric_df, ['insider_own', 'dividend', 'roi', 'roe'])
        self.metric_df = self.combine_with_return_data(self.metric_df)
        self.metric_df = self.metric_df.drop_duplicates()
        self.metric_df = self.metric_df.replace(np.nan, 0)
        self.metric_df = self.metric_df.applymap(str)
    
    def cache_data_logging(self,cache_name):
        logging.info(CACHED_DATA_LOG, cache_name + " is not available. Caching it now")
    
    def cache_found_logging(self,cache_name):
        logging.info(CACHED_DATA_LOG, cache_name + " is found in cache")

    # if there is metric_df data then return it else call get_stock_data_by_sector_and_index
    def get_screener_data(self):
        logging.info("screener data %s", self.metric_df)
        return self.metric_df.fillna(0)

    def update_avg_metric_dic(self, sector):
        if sector == 'Any':
            df = bigQuery.get_average_metric()
            df = df.drop(columns=['Sector'])
            df = df.astype(float)
            df = df.mean(axis=0)
            self.avg_metric_df = df.astype(float)
        else:
            df = bigQuery.get_average_metric_by_sector(sector)
            df = df.drop(columns=['Sector'])
            df = df.astype(float)
            df = df.squeeze()  # to convert it to series
            self.avg_metric_df = df
        return self.avg_metric_df

    # we can use return_risk_ratio as a multiplier instead of addition. There is a possibility
    # of calculating the coefficient of each of these attributes so that we give more weights to more relevant attribute

    def calculate_strength_value(self, df, stock_type):
        cache_name = stock_type + '_strength_data'
        logging.info("Calculating strength value for %s", stock_type)
        if stock_type not in [enum.StockType.VALUE.value, enum.StockType.GROWTH.value]:
            raise ValueError("Stock Type must be Value or Growth")
        cached_data = redis_cache.get(cache_name)
        if cached_data:
            self.cache_found_logging(cache_name)
            # Deserialize the JSON and create a DataFrame
            return pd.read_json(cached_data.decode('utf-8'), orient='split')
        else:
            attributes = ["dividend", "pe", "fpe", "pb", "beta", "return_risk_ratio"]
            df["strength"] = 0
            for col in attributes:
                df[col].replace('nan', np.nan, inplace=True)
                df[col].replace('None', np.nan, inplace=True)
                if col == 'beta':
                    self.calculate_strength_for_beta(df)
                elif col == 'return_risk_ratio':
                    self.calculate_strength_for_return_risk_ratio(df)
                else:
                    self.calculate_strength_for_attribute(df, col)

            if stock_type == enum.StockType.GROWTH.value:
                df["strength"] = -1 * df["strength"]

            df = df.replace(np.nan, 0)
            df = np.round(df, decimals=3)
            df = df.sort_values(by=["strength", "expected_annual_return"], ascending=[False, False])
            self.print_logging(stock_type + '_strength_data');
            redis_cache.set(cache_name, df.to_json(orient='split'), ex=86400)  # Cache for 1 day
            return df

    def calculate_strength_for_beta(self, df):
        df["strength"] = df["strength"] - np.where(df["beta"].isnull(), 0, df["beta"].astype(float))

    def calculate_strength_for_return_risk_ratio(self, df):
        df["strength"] = df["strength"] + np.where(df["return_risk_ratio"].isnull(), 0, df["return_risk_ratio"].astype(float))

    def calculate_strength_for_attribute(self, df, attribute):
        new_col = np.where(df[attribute].isnull(), 0, df[attribute].astype(float) - self.avg_metric_df[attribute])
        new_col = np.divide(1, self.avg_metric_df[attribute]) * new_col  # percentage change
        if attribute == 'dividend':
            df["strength"] = df["strength"] + new_col
        else:
            df["strength"] = df["strength"] - new_col

    def get_risk_tolerance_data(self, risk_tolerance, df):
        if risk_tolerance == enum.RiskEnum.HIGH.value:
            df = df[df['expected_annual_risk'].astype(float) > .7]
        elif risk_tolerance == enum.RiskEnum.MEDIUM.value:
            df = df[(df['expected_annual_risk'].astype(float) > .4) & (df['expected_annual_risk'].astype(float) < .6)]
        elif risk_tolerance == enum.RiskEnum.LOW.value:
            df = df[(df['expected_annual_risk'].astype(float) > .15) & (df['expected_annual_risk'].astype(float) < .4)]
        return df

    def combine_with_return_data(self, df):
        return_rate = bigQuery.get_annual_return()
        combined_data = pd.merge(df, return_rate, on='Ticker', how='inner')
        combined_data = np.round(combined_data, decimals=3)
        return combined_data

    def update_strength_data(self, sector, index, stock_type):
        sector_index_data = self.get_stock_data_by_sector_and_index(index, sector)
        self.update_avg_metric_dic(sector)
        strength_calculated_df = self.calculate_strength_value(sector_index_data, stock_type)
        strength_calculated_df = strength_calculated_df.fillna(0)
        return strength_calculated_df

    def get_sp500_data(self):  # need to research whether storing the value in class is more effecient vs using pickle
        return self.get_stock_data_by_sector_and_index(sector='Any', index='S&P 500')

    def get_title(self):
        return "{index} {sector} Data".format(sector=self.sector, index=self.index)

    import json

    def is_valid_json(self,json_string):
        try:
            json.dumps(json_string)
            return True
        except json.JSONDecodeError:
            return False