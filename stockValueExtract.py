
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
    def __init__(self):
        self.optimized_df = pd.DataFrame()
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.top_dict = []
        self.optimal_number_stocks = 0
        self.previous_highest_expected_return = 0
        self.threshold = 0
        self.desired_return = 0
    
    def get_stock_data_by_sector_and_index(self,index,sector):
        self.metric_df = bigQuery.get_stock_data(index, sector)
        self.round_decimal_place(self.metric_df,['insider_own','dividend','roi','roe'])
        return self.metric_df

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

    def round_decimal_place(self,df,roundArray):
        for a in roundArray:
            df[a] = np.round(df[a].astype(float), decimals = 2)
        return df
 
    # need to refactor
    def calculate_strength_value(self, df, stock_type):
        attributes = ["dividend","pe","fpe","pb","beta"]
        df["strength"] = 0
        for col in attributes:
            df[col].replace('nan', np.nan, inplace=True)
            df[col].replace('None', np.nan, inplace=True)
            if col == 'beta':
                df["strength"] = df["strength"] - np.where(df[col].isnull(),0,df[col].astype(float))
            else:
                new_col = np.where(df[col].isnull(), 0, df[col].astype(float) - self.avg_metric_df[col])
                if col == 'dividend': 
                    df["strength"] = df["strength"] + new_col
                else:
                    df["strength"] = df["strength"] - new_col
        if stock_type == helper.StockType.VALUE.value:
            df["strength"] = df["strength"]
        elif stock_type == helper.StockType.GROWTH.value:
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

    def optimize_expected_return(self, number_of_stocks, threshold,desired_return):
        df = self.optimized_df.sort_values(by='strength', ascending=False) #we want to remove the lowest strength iteratively till we ge the optimat expected return
        df = self.optimized_df.head(number_of_stocks)
        self.calculate_weight_expected_return(df)
        actual_return = df['expected_return'].replace(np.nan, 0).to_numpy()
        actual_expected_return = sum(actual_return)

        if actual_expected_return > desired_return:
            self.previous_highest_expected_return = actual_expected_return
            self.optimal_number_stocks = number_of_stocks
            self.desired_return = actual_expected_return

        elif actual_expected_return > self.previous_highest_expected_return:
            self.previous_highest_expected_return = actual_expected_return
            self.optimal_number_stocks = number_of_stocks

        if number_of_stocks > threshold:
            return self.optimize_expected_return(number_of_stocks - 1,threshold,desired_return)
        else:
            self.optimized_df = self.optimized_df.head(
                self.optimal_number_stocks)
            self.optimized_df = self.calculate_weight_expected_return(
                self.optimized_df)
            return

    def top_stocks(self,strength_df):
        for sector in helper.get_sector():
            df = strength_df[strength_df['Sector'] == sector].head(5)
            labels = df["Ticker"].values.tolist()
            values = df["strength"]
            weight_values = np.divide(1,np.sum(values)) * values
            weight_values = weight_values.values.tolist()
            self.top_dict.append({"id": sector, "values":weight_values, "labels":labels, "title": sector})
        return self.top_dict

    def build_portfolio(self, df, selected_ticker_list, threshold, desired_return, investing_amount):
        self.metric_df = df
        self.optimized_df = df[df.Ticker.isin(selected_ticker_list)]
        self.optimized_df = self.optimized_df[(self.optimized_df['strength'] > 0) & (self.optimized_df['roi'] > 0)  ]
        self.threshold = threshold
        self.desired_return = desired_return
        self.optimize_expected_return(
            number_of_stocks=len(selected_ticker_list),threshold = threshold, desired_return = desired_return)
        self.calculate_portfolio_value_distribution(investing_amount)
        self.total_share()
        return self.optimized_df

    def checkFile(self,fileName):
     result = True
     try:
         pd.read_pickle(fileName)
     except:
        result = False
     return result
    
    def get_chart_data(self,fileName):
        df = pd.DataFrame()
        if self.checkFile(fileName):
            df = pd.read_pickle(fileName)
        else:
            stocks_df = self.get_stock_data_by_sector_and_index('S&P 500','Any')
            self.update_avg_metric_dic('Any')
            df = self.calculate_strength_value(stocks_df,'Value')
            df.to_pickle(fileName)     
        return self.top_stocks(df)

    def update_strength_data(self,sector,index,stock_type):
        combined_data = self.get_stock_data_by_sector_and_index(index,sector)
        self.update_avg_metric_dic(sector)
        strength_calculated_df = self.calculate_strength_value(
            combined_data,stock_type)
        strength_calculated_df = np.round(strength_calculated_df, decimals=2)
        strength_calculated_df.reset_index(drop=True, inplace=True)
        strength_calculated_df  = strength_calculated_df.fillna(0)
        #need to think about how to cache this in the production
        strength_calculated_df.to_pickle("./stock.pkl")
        ticker_lists = strength_calculated_df["Ticker"].to_list()
        return ticker_lists

    def cache_portfolio(self,expected_return_value, threshold, investing_amount,selected_ticker_lists):
        logging.info("Optimizing the stock data")
        portfolio = self.build_portfolio(df=pd.read_pickle("./stock.pkl"), selected_ticker_list=selected_ticker_lists, desired_return=np.divide(int(
                    expected_return_value), 100), threshold=int(threshold), investing_amount=int(investing_amount))
        portfolio = np.round(portfolio, decimals=2)
        portfolio.to_pickle("./portfolio.pkl")

    def validate_input(self, selected_ticker_lists, expected_return_value, threshold, investing_amount):
        message = ""
        if len(selected_ticker_lists) == 0:
            message = 'The stock list should not be null'
        elif len(selected_ticker_lists) != len(set(selected_ticker_lists)):
            message = 'The stocks must be unique'
        elif threshold == '':
            message = 'Threshold should not be blank'
        elif len(set(selected_ticker_lists)) < int(float(threshold)):
            message = 'The stock list must be greater than threshold'
        elif investing_amount == '':
            message = 'Investment Amount must not be blank'
        elif expected_return_value == '':
            message = 'Expected Return Value must not be blank'
        return message
    
   
            