
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
        self.avg_metric_df = pd.DataFrame()
        self.metric_df = pd.DataFrame()
        self.avg_metric_dictionary = {}
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
    
    def round_decimal_place(self,df,roundArray):
        for a in roundArray:
            df[a] = np.round(df[a].astype(float), decimals = 2)
        return df
 
    def update_avg_metric_df(self):
        gOverview = Goverview()
        gValuation = Gvaluation()
        overview = gOverview.screener_view(group='Sector', order='Name')[
            helper.get_goverview_metric()]
        valuation = gValuation.screener_view(group='Sector', order='Name')[
            helper.get_gvaluation_metric()]
        self.avg_metric_df = pd.concat(
            [overview, valuation], axis=1, join='inner')
        self.avg_metric_df = self.avg_metric_df.loc[self.avg_metric_df['Name'] == self.sector]
        return self.avg_metric_df

    def update_avg_metric_dic(self):
        self.update_avg_metric_df()
        self.avg_metric_dictionary.update({
            "pe": str(self.avg_metric_df['P/E'].iat[0]),
            "fpe": str(self.avg_metric_df['Fwd P/E'].iat[0]),
            "pc": str(self.avg_metric_df['P/C'].iat[0]),
            "pb": str(self.avg_metric_df['P/B'].iat[0]),
            "peg": str(self.avg_metric_df['PEG'].iat[0]),
            "div": float(self.avg_metric_df['Dividend'].iat[0])})
        return self.avg_metric_dictionary

    # need to refactor
    def calculate_strength_value(self, df):
        self.update_avg_metric_dic()
        #df["pe"] = df["pe"]
        if self.stock_type == helper.StockType.VALUE.value:
            pe = np.where(df["pe"].replace(np.nan,0) < str(self.avg_metric_dictionary["pe"]), 1, 0)
            fpe = np.where(df["fpe"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["fpe"], 1, 0)
            pb = np.where(df["pb"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pb"], 1, 0)
            peg = np.where(df["peg"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["peg"], 1, 0)
            div = np.where(df["dividend"].replace(np.nan, 0)
                           < self.avg_metric_dictionary["div"], 0, 1)
            beta = np.where(df["beta"].replace(np.nan, 0) < '1', 0, 1)
            df["strength"] = pe + fpe + pb + peg + div + beta

        elif self.stock_type == helper.StockType.GROWTH.value:
            pe = np.where(df["pe"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pe"], 0, 1)
            fpe = np.where(df["fpe"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["fpe"], 0, 1)
            pb = np.where(df["pb"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pb"], 0, 1)
            peg = np.where(df["peg"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["peg"], 0, 1)
            div = np.where(df["dividend"].replace(np.nan, 0)
                           < self.avg_metric_dictionary["div"], 1, 0)
            beta = np.where(df["beta"].replace(np.nan, 0) > '1', 1, 0)
            df["strength"] = pe + fpe + pb + peg + div + beta
        else:
            raise ValueError("Stock Type must be Value or Growth")
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
