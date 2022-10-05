
import pandas as pd
import numpy as np
import helper
from finvizfinance.group.overview import Overview as Goverview
from finvizfinance.group.valuation import Valuation as Gvaluation
pd.options.mode.chained_assignment = None  # default='warn'
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.valuation import Valuation
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.technical import Technical

foverview = Overview()
fvaluation = Valuation()
fownership = Ownership()
ftechnical = Technical()
fperformance = Performance()
financial = Financial()
ticker = Ticker()



class stock():
    # init method or constructor
    def __init__(self, sector, stock_type, index):
        self.sector = sector
        self.metric_df = pd.DataFrame()
        self.optimized_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.avg_metric_dictionary = {}
        self.stock_type = stock_type
        self.index = index
        self.optimal_number_stocks = 0
        self.previous_highest_expected_return = 0
        self.threshold = 0
        self.desired_return = 0
    
    def get_stock_data(self,page):
        valuation = self.get_metric_data(fvaluation, page)[helper.get_valuation_metric()]
        financial_df = self.get_metric_data(financial, page)[helper.get_financial_metric()]
        technical = self.get_metric_data(ftechnical, page)[helper.get_techical_metric()]
        ownership = self.get_metric_data(fownership, page)[helper.get_ownership_metric()]
        self.metric_df = pd.concat([valuation, financial_df, technical, ownership], join='inner', axis=1)
        return self.metric_df

    def get_metric_data(self, function, page):
        try:
            filter_dic = {"Sector": self.sector, "Index": self.index}
            function.set_filter(filters_dict=filter_dic)
            self.metric_df = function.screener_view(select_page=page)
        except Exception as e:
            print("An exception occurred", e)
            pass
        return self.metric_df

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
            "pe": self.avg_metric_df['P/E'].iat[0],
            "fpe": self.avg_metric_df['Fwd P/E'].iat[0],
            "pc": self.avg_metric_df['P/C'].iat[0],
            "pb": self.avg_metric_df['P/B'].iat[0],
            "peg": self.avg_metric_df['PEG'].iat[0],
            "div": self.avg_metric_df['Dividend'].iat[0]})
        return self.avg_metric_dictionary

    # need to refactor
    def calculate_strength_value(self, df):
        self.update_avg_metric_dic()
        if self.stock_type == helper.StockType.VALUE.value:
            pe = np.where(df["P/E"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pe"], 1, 0)
            fpe = np.where(df["Fwd P/E"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["fpe"], 1, 0)
            pb = np.where(df["P/B"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pb"], 1, 0)
            peg = np.where(df["PEG"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["peg"], 1, 0)
            div = np.where(df["Dividend"].replace(np.nan, 0)
                           < self.avg_metric_dictionary["div"], 0, 1)
            beta = np.where(df["Beta"].replace(np.nan, 0) < 1, 0, 1)
            df["Strength"] = pe + fpe + pb + peg + div + beta

        elif self.stock_type == helper.StockType.GROWTH.value:
            pe = np.where(df["P/E"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pe"], 0, 1)
            fpe = np.where(df["Fwd P/E"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["fpe"], 0, 1)
            pb = np.where(df["P/B"].replace(np.nan, 0) <
                          self.avg_metric_dictionary["pb"], 0, 1)
            peg = np.where(df["PEG"].replace(np.nan, 0) <
                           self.avg_metric_dictionary["peg"], 0, 1)
            div = np.where(df["Dividend"].replace(np.nan, 0)
                           < self.avg_metric_dictionary["div"], 1, 0)
            beta = np.where(df["Beta"].replace(np.nan, 0) < 1, 1, 0)
            df["Strength"] = pe + fpe + pb + peg + div + beta
        else:
            raise ValueError("Stock Type must be Value or Growth")
        return df.sort_values(by="Strength", ascending=False)

    def calculate_weight_expected_return(self, df):
        strengthArray = df["Strength"]
        strengthList = list(map(float, strengthArray))
        weight_array = np.divide(strengthList, sum(strengthList))
        df["Weight"] = weight_array
        df["Expected Return"] = df["ROI"].replace(np.nan, 0) * df["Weight"]
        return df

    def calculate_portfolio_value_distribution(self, investing_amount):
        self.optimized_df['Invested Amount'] = np.multiply(
            self.optimized_df['Weight'], investing_amount)
        return self.optimized_df['Invested Amount']

    def total_share(self):
        self.optimized_df['Total Shares'] = np.divide(
            self.optimized_df['Invested Amount'], self.optimized_df['Price'])
        return self.optimized_df

    def optimize_expected_return(self, number_of_stocks):
        df = self.optimized_df.head(number_of_stocks)
        self.calculate_weight_expected_return(df)
        actual_return = df['Expected Return'].replace(np.nan, 0).to_numpy()
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

    def top_stocks(self, df):
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
