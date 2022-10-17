
from cmath import nan
import pandas as pd
import numpy as np
import helper
import bigQuery
import logging
from finvizfinance.group.overview import Overview as Goverview
from finvizfinance.group.valuation import Valuation as Gvaluation
pd.options.mode.chained_assignment = None  # default='warn'

logging.basicConfig(level = logging.INFO)

class stock():
    # init method or constructor
    def __init__(self, sector, stock_type, index):
        self.sector = sector
        self.optimized_df = pd.DataFrame()
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.stock_type = stock_type
        self.index = index
        self.optimal_number_stocks = 0
        self.previous_highest_expected_return = 0
        self.threshold = 0
        self.desired_return = 0
    
    def get_stock_data_by_sector_and_index(self):
        self.metric_df = bigQuery.get_stock_data(self.index, self.sector)
        self.round_decimal_place(self.metric_df,['insider_own','dividend','roi','roe'])
        return self.metric_df

    def update_avg_metric_dic(self):
        if self.sector == 'Any':
            df = bigQuery.get_average_metric()
            df = df.drop(columns = ['Sector'])
            df = df.astype(float)
            df = df.mean(axis=0)
            self.avg_metric_df = df.astype(float)
        else:
           df = bigQuery.get_average_metric_by_sector(self.sector)
           df = df.drop(columns = ['Sector'])
           df = df.astype(float)
           df = df.squeeze() # to convert it to series 
           self.avg_metric_df = df
        return self.avg_metric_df

    def round_decimal_place(self,df,roundArray):
        for a in roundArray:
            df[a] = np.round(df[a].astype(float), decimals = 2)
        return df
 
    # need to refactor
    def calculate_strength_value(self, df):
        attributes = ["dividend","pe","fpe","pb","beta"]
        df["strength"] = 0
        for col in attributes:
            if col == 'beta':
                df["strength"] = df["strength"] - np.where(df[col].isnull(),0,df[col].astype(float))
            else:
                #if any col value is nan then set the difference to 0 
                df[col].replace('None', np.nan, inplace=True)
                df[col].replace('nan', np.nan, inplace=True)
                new_col = np.where(df[col].isnull(), 0, df[col].astype(float) - self.avg_metric_df[col])
                print("COL", df[col])
                print("NEW_COL", new_col)
                if col == 'dividend': 
                    df["strength"] = df["strength"] + new_col
                else:
                    df["strength"] = df["strength"] - new_col
        if self.stock_type == helper.StockType.VALUE.value:
            df["strength"] = df["strength"]
        elif self.stock_type == helper.StockType.GROWTH.value:
            df["strength"] = -1*df["strength"]
        else:
            raise ValueError("Stock Type must be Value or Growth")
        print(df["strength"])
        return df.sort_values(by="strength", ascending=False)

    def calculate_weight_expected_return(self, df):
        strengthArray = df["strength"]
        strengthList = list(map(float, strengthArray))
        weight_array = np.divide(strengthList, sum(strengthList))
        df["weight"] = weight_array
        df["expected_return"] = list(map(float,df["roi"].replace(np.nan, 0))) * df["weight"]
        return df

    def calculate_portfolio_value_distribution(self, investing_amount):
        self.optimized_df['invested_amount'] = np.multiply(
            self.optimized_df['weight'], investing_amount)
        return self.optimized_df['invested_amount']

    def total_share(self):
        self.optimized_df['total_shares'] = np.divide(
            self.optimized_df['invested_amount'], self.optimized_df['price'].astype(float))
        return self.optimized_df

    def optimize_expected_return(self, number_of_stocks):
        df = self.optimized_df.sort_values(by='strength', ascending=False) #we want to remove the lowest strength iteratively till we ge the optimat expected return
        df = self.optimized_df.head(number_of_stocks)
        self.calculate_weight_expected_return(df)
        actual_return = df['expected_return'].replace(np.nan, 0).to_numpy()
        actual_expected_return = sum(actual_return)

        if actual_expected_return > self.desired_return:
            self.previous_highest_expected_return = actual_expected_return
            self.optimal_number_stocks = number_of_stocks
            self.desired_return = actual_expected_return

        elif actual_expected_return > self.previous_highest_expected_return:
            self.previous_highest_expected_return = actual_expected_return
            self.optimal_number_stocks = number_of_stocks

        if number_of_stocks > self.threshold:
            return self.optimize_expected_return(number_of_stocks - 1)
        else:
            self.optimized_df = self.optimized_df.head(
                self.optimal_number_stocks)
            self.optimized_df = self.calculate_weight_expected_return(
                self.optimized_df)
            return

    def top_stocks(self):
        stocks_df = self.update_metric_data_frame
        self.update_avg_metric_df
        stocks_df = self.calculate_strength_value
        return stocks_df

    def build_portfolio(self, df, selected_ticker_list, threshold, desired_return, investing_amount):
        self.metric_df = df
        self.optimized_df = df[df.Ticker.isin(selected_ticker_list)]
        self.optimized_df = self.optimized_df[(self.optimized_df['strength'] > 0) & (self.optimized_df['roi'] > 0)  ]
        print(self.optimized_df)
        self.threshold = threshold
        self.desired_return = desired_return
        self.optimize_expected_return(
            number_of_stocks=len(selected_ticker_list))
        self.calculate_portfolio_value_distribution(investing_amount)
        self.total_share()
        return self.optimized_df

    def remove_empty_element(stock_list):
        while '' in stock_list:
            stock_list.remove('')
