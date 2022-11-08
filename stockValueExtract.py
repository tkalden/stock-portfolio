import pandas as pd
import numpy as np
import helper
import bigQuery
import logging
pd.options.mode.chained_assignment = None  # default='warn'
import uuid

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
        self.metric_df = self.combine_with_return_data(self.metric_df)
        self.metric_df = self.metric_df.drop_duplicates()
        self.metric_df  = self.metric_df.replace(np.nan,0)
        self.metric_df=self.metric_df.applymap(str)
         #the dataTable throws invalid json if the dtype is not string. Workaround solution for now
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
            df[a] = np.round(df[a].astype(float), decimals = 3)
        return df
 
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
        if stock_type == helper.StockType.VALUE.value:
            df["strength"] = df["strength"]
        elif stock_type == helper.StockType.GROWTH.value:
            df["strength"] = -1*df["strength"]
        else:
            raise ValueError("Stock Type must be Value or Growth")
        df = df.replace(np.nan,0)
        df = np.round(df, decimals=3) 
        df = df.sort_values(by=["strength","expected_annual_return"], ascending=[False,False])
        return df

    def calculate_weighted_expected_return(self, df):
        strengthArray = df["strength"]
        strengthList = list(map(float, strengthArray))
        weight_array = np.divide(strengthList, sum(strengthList))
        df['weight'] = weight_array
        df['weighted_expected_return'] =  df['expected_annual_return'].astype(float) * df['weight']
        return df

    def calculate_portfolio_value_distribution(self, investing_amount):
        self.optimized_df['invested_amount'] = np.multiply(
        self.optimized_df['weight'].astype(float), float(investing_amount))
        return

    def calculate_portfolio_return(self,df):
         porfolio_return = df['weighted_expected_return']
         porfolio_return = round(porfolio_return.sum(),3)
         return porfolio_return*100
    
    def calculate_portfolio_risk(self,df):
        portfolio_risk =  df['expected_annual_risk'].astype(float) * df['weight']
        portfolio_risk = portfolio_risk.round(3)
        portfolio_risk = portfolio_risk.sum()
        return portfolio_risk*100
 

    def total_share(self):
        self.optimized_df['total_shares'] = np.divide(
            self.optimized_df['invested_amount'], self.optimized_df['price'].astype(float))
        return self.optimized_df
    
    """Returns the optimal number of stocks from the top strength stocks that give the expected
    return equal or higher than the desired expected return
        :param number_of_stocks: iterative number of stocks 
        :param threshold: minimum number of stocks
        :param desired_return: desired expected return 
        :returns: optimal portfolio 
    """
    def optimize_expected_return(self, number_of_stocks, threshold,desired_return):
        #we want to remove the lowest strength iteratively till we get the optimal expected return
        if number_of_stocks < float(threshold):
            return  
        df = self.optimized_df.head(number_of_stocks)
        self.calculate_weighted_expected_return(df)
        actual_return = df['weighted_expected_return']
        actual_expected_return = float(actual_return.sum())
        actual_greater_than_desired = actual_expected_return > float(desired_return)
        actual_greater_than_previous_actual = actual_expected_return > self.previous_highest_expected_return 
        if actual_greater_than_desired:
            self.optimal_number_stocks = number_of_stocks
        elif (actual_greater_than_previous_actual) & (not actual_greater_than_desired):
             self.optimal_number_stocks = number_of_stocks
             self.previous_highest_expected_return = actual_expected_return
        self.optimize_expected_return(number_of_stocks - 1,threshold,actual_expected_return)
        df = self.optimized_df.head(self.optimal_number_stocks)
        self.optimized_df = self.calculate_weighted_expected_return(df)
        return self.optimized_df

    def top_stocks(self,df,base_metric):
        sectors = helper.get_sector()
        sectors.remove('Any')
        for sector in sectors:
            new_df = df[df['Sector'] == sector].head(5)
            labels = new_df["Ticker"].values.tolist()
            if base_metric == 'Strength':
                strength_values = new_df["strength"]
                #strength_values = np.divide(1,np.sum(strength_values)) * strength_values
                values = strength_values.values.tolist()
                self.top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
            elif base_metric == 'Dividend':
                dividend_values = new_df["dividend"] 
                values = dividend_values.values.tolist()
                self.top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        return self.top_dict

    def build_portfolio_from_user_input_tickers(self, df, selected_ticker_list, threshold, desired_return, investing_amount,maximum_stock_price):
        df = df[df.Ticker.isin(selected_ticker_list)]
        df = df[(df['strength'] > 0) & (df['expected_annual_return'].astype(float) > 0) & (df['price'].astype(float) < float(maximum_stock_price)) ]
        self.threshold = threshold
        self.desired_return = desired_return
        self.optimized_df = df #initialize the df
        self.optimized_df = self.optimize_expected_return(
            number_of_stocks=len(selected_ticker_list),threshold = threshold, desired_return = desired_return)
        return self.calculate_portfolio_value_and_share(investing_amount)

    def calculate_portfolio_value_and_share(self, investing_amount):
        self.calculate_portfolio_value_distribution(investing_amount)
        self.total_share()
        portfolio = np.round(self.optimized_df, decimals=3)
        portfolio = portfolio[helper.portfolio_attributes()]
        return portfolio

    def build_portfolio_with_top_stocks(self, df, investing_amount,maximum_stock_price):   
        self.optimized_df = df[(df['strength'] > 0) & (df['expected_annual_return'].astype(float) > 0) & (df['price'].astype(float) < float(maximum_stock_price))]
        self.optimized_df = self.calculate_weighted_expected_return(self.optimized_df.head(5)) 
        return self.calculate_portfolio_value_and_share(investing_amount)

    def checkFile(self,key):
     result = True
     try:
         pd.read_pickle(helper.get_pickle_file()[key])
     except:
        result = False
     return result
    
    def get_chart_data(self,key,stock_type,base_metric,overwrite):
        df = pd.DataFrame()
        if self.checkFile(key) and not overwrite:
            df = self.unpickle_file(key)
        else:
            df = self.get_stock_data_by_sector_and_index('S&P 500','Any')
            if base_metric == helper.Metric.STRENGTH.value:
                self.update_avg_metric_dic('Any')
                df = self.calculate_strength_value(df,stock_type)
            elif base_metric == helper.Metric.DIVIDEND.value:
                df = df.sort_values(by="dividend", ascending=False)
            self.pickle_file(df,key)  
        return self.top_stocks(df,base_metric)

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

    def pickle_file(self, df, key):
        logging.info('Pickle DF')
        return df.to_pickle(helper.get_pickle_file()[key])

    def unpickle_file(self,key):
        return pd.read_pickle(helper.get_pickle_file()[key])

    def save_data(self, df, table_id):
         return bigQuery.write_to_bigquery(df,table_id)

    def save_portfolio_data(self,df,user_id):
         new_df = df.drop(['Ticker'],1)
         new_df = new_df.apply(pd.to_numeric)
         final_df = pd.concat([df['Ticker'],new_df], axis=1)
         uid = uuid.uuid4()
         portfolio_id = uid.hex
         table_id = 'stockdataextractor.stock.portfolio-table'
         final_df['user_id'] = user_id
         final_df['portfolio_id'] = portfolio_id
         self.save_data(final_df,table_id)

    def get_portfolios_by_user_id(self,user_id):
        return bigQuery.get_portfolios_by_user_id(user_id)
   
    def cache_stock_data(self):
        if not self.checkFile('stock'):
            data = self.get_stock_data_by_sector_and_index(sector = 'Any', index='S&P 500')
            self.pickle_file(data,'stock')

    
   
            
