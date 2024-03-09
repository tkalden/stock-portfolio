import logging
import uuid

import numpy as np
import pandas as pd
from flask import flash
from flask_login import current_user

import utilities.bigQuery as bigQuery
import utilities.helper as helper
from methods.optimization import optimization
from methods.stock import stock
from utilities.pickle import pickle

stock = stock()
optimization = optimization()
pickle = pickle()

class portfolio():
     # init method or constructor
    def __init__(self):
        self.optimized_df = pd.DataFrame()
        self.optimal_number_stocks = 0
        self.previous_highest_expected_return = 0
        self.threshold = 0
        self.desired_return = 0
        self.portfolio_list = []

    def build_portfolio_from_user_input_tickers(self, df, selected_ticker_list, desired_return, investing_amount,risk_tolerance):
        df = df[df.Ticker.isin(selected_ticker_list)]
        df = df[(df['strength'] > 0) & (df['expected_annual_return'].astype(float) > 0)]
        df = stock.get_risk_tolerance_data(risk_tolerance,df)
        self.threshold = len(selected_ticker_list)
        self.desired_return = desired_return
        self.optimized_df = df #initialize the df
        self.optimized_df = optimization.optimize_expected_return(self.optimized_df,
            number_of_stocks=len(selected_ticker_list),threshold = len(selected_ticker_list), desired_return = desired_return)
        self.optimized_df  = self.calculate_portfolio_value_and_share(investing_amount)
        return self.optimized_df 

    def calculate_portfolio_value_and_share(self, investing_amount):
        self.calculate_portfolio_value_distribution(investing_amount)
        self.total_share()
        portfolio = np.round(self.optimized_df, decimals=3)
        portfolio = portfolio[helper.portfolio_attributes()]
        return portfolio

    def total_share(self):
        self.optimized_df['total_shares'] = np.divide(
            self.optimized_df['invested_amount'], self.optimized_df['price'].astype(float))
        return self.optimized_df

    def build_portfolio_with_top_stocks(self, df, investing_amount,maximum_stock_price,risk_tolerance):  
        self.optimized_df = df[(df['strength'] > 0) & (df['expected_annual_return'].astype(float) > 0) & (df['price'].astype(float) < float(maximum_stock_price))]
        self.optimized_df = stock.get_risk_tolerance_data(risk_tolerance,self.optimized_df)
        self.optimized_df = optimization.calculate_weighted_expected_return(self.optimized_df.head(5)) 
        self.optimized_df  = self.calculate_portfolio_value_and_share(investing_amount)
        return self.optimized_df 
    
    def calculate_portfolio_value_distribution(self, investing_amount):
        self.optimized_df['invested_amount'] = np.multiply(
        self.optimized_df['weight'].astype(float), float(investing_amount))
    

    def calculate_portfolio_return(self,df):
         porfolio_return = df['weighted_expected_return']
         porfolio_return = round(porfolio_return.sum(),3)
         return porfolio_return*100
    
    def calculate_portfolio_risk(self,df):
        portfolio_risk =  df['expected_annual_risk'].astype(float) * df['weight']
        portfolio_risk = portfolio_risk.round(3)
        portfolio_risk = portfolio_risk.sum()
        return portfolio_risk*100

    def save_portfolio_data(self,df,user_id):
        new_df = df.drop(['Ticker'],1)
        new_df = new_df.apply(pd.to_numeric)
        final_df = pd.concat([df['Ticker'],new_df], axis=1)
        uid = uuid.uuid4()
        portfolio_id = uid.hex
        table_id = 'stockdataextractor.stock.portfolio-table'
        final_df['user_id'] = user_id
        final_df['portfolio_id'] = portfolio_id
        pickle.save_data(final_df,table_id)

    def get_portfolios_by_user_id(self,user_id):
        df = bigQuery.get_portfolios_by_user_id(user_id)
        df_tuple = dict(tuple(df.groupby('portfolio_id')))
        res = [df_tuple[key].to_dict('records') for key in df_tuple.keys()]
        self.portfolio_list = res
        return res
    
    def get_porfolio(self):
        return self.portfolio_list

    def get_build_porfolio(self):
        return self.optimized_df
