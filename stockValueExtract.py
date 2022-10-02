
import pandas as pd
import numpy as np
import helper
from finvizfinance.group.overview import Overview as Goverview
from finvizfinance.group.valuation import Valuation as Gvaluation
pd.options.mode.chained_assignment = None  # default='warn'

class stock():
     # init method or constructor
    def __init__(self, sector, stock_type, index):
        self.sector = sector
        self.optimized_df = pd.DataFrame()
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.avg_metric_dictionary = {}
        self.stock_type = stock_type
        self.index = index
    
    def update_metric_df(self,df):
        self.metric_df = df
        return self.metric_df

    def get_ticker_list(self):
        return self.metric_df["Ticker"].to_list()
    
    def get_metric_df(self):
        return self.metric_df

    def get_metric_data(self,function,page):
        try:
            filter_dic = {"Sector": self.sector, "Index":self.index}
            if self.stock_type == helper.StockType.GROWTH.value:
                filter_dic.update({"P/E":helper.PEFilter.HIGH.value})
            elif self.stock_type == helper.StockType.VALUE.value:
                filter_dic.update({"P/E":helper.PEFilter.LOW.value})
            function.set_filter(filters_dict=filter_dic)
            self.metric_df = function.screener_view(select_page=page)
            #
        except Exception as e:
             print("An exception occurred", e)
             pass
        return self.metric_df

    def update_avg_metric_df(self):
        gOverview = Goverview()
        gValuation = Gvaluation()
        overview = gOverview.screener_view(group='Sector', order='Name')[helper.get_goverview_metric()]
        valuation = gValuation.screener_view(group='Sector', order='Name')[helper.get_gvaluation_metric()]
        self.avg_metric_df =  pd.concat([overview, valuation], axis =1 , join = 'inner') 
        print("AVGE DF", self.avg_metric_df)
        self.avg_metric_df = self.avg_metric_df.loc[self.avg_metric_df['Name'] == self.sector]
        return self.avg_metric_df 
    
    """  def update_avg_metric_dic(self):
        avg_metric_df_by_sector = self.avg_metric_df["Name" : self.sector ]
        avg_pe = avg_metric_df_by_sector["P/E"].values()
        avg_pc = avg_metric_df_by_sector["P/C"].values()
        avg_fpe = avg_metric_df_by_sector["Fwd P/E"].values()
        avg_peg = avg_metric_df_by_sector["PEG"].values()
        avg_pb = avg_metric_df_by_sector["P/B"].values()
        avg_div = avg_metric_df_by_sector["Dividend"].astype(str).str.replace('%', '').values()
        self.avg_metric_dictionary = {"pe": avg_pe, "pc": avg_pc, "fpe": avg_fpe, "peg": avg_peg, "pb": avg_pb,
            "div": avg_div
            }
        return self.avg_metric_dictionary """

    
    def calculate_strength_value(self):
        pe =  self.avg_metric_df['P/E'] - self.metric_df['P/E']
        fpe =  self.avg_metric_df['Fwd P/E'] - self.metric_df['Fwd P/E']
        pc = self.avg_metric_df['P/C'] - self.metric_df['P/C']
        pb = self.avg_metric_df['P/B'] - self.metric_df['P/B']
        peg = self.avg_metric_df['PEG'] - self.metric_df['PEG']
        div =  self.metric_df['Dividend'] - self.avg_metric_df['Dividend']
        combination = pe + fpe + pc + pb + peg + div
        if self.stock_type == 'Value':
            self.optimized_df["Strength"] = combination 
        elif self.stock_type == 'Growth':
            self.optimized_df["Strength"] = -1 * combination  # -1 because Growth has opposite metric values
        else :
            raise ValueError("Stock Type must be Value or Growth")
        return self.optimized_df


    def calculate_weight_expected_return(self):
        strengthArray  = self.optimized_df["Strength"].replace(np.nan, 0).to_numpy()
        strengthList = list(map(float, strengthArray))
        weight_array = np.divide(strengthList, sum(strengthList))
        self.optimized_df["Weight"] = weight_array
        self.optimized_df["Expected Return"] = self.optimized_df["ROI"].replace(np.nan, 0) * self.optimized_df["Weight"]
        return self.optimized_df['Weight']
    
    def calculate_portfolio_value_distribution(self,investing_amount):
        self.optimized_df['Invested Amount'] = np.multiply(self.optimized_df['Weight'], investing_amount)
        return self.optimized_df['Invested Amount'] 


    def total_share(self):
        self.optimized_df['Total Shares'] = np.divide(self.optimized_df['Invested Amount'], self.optimized_df['Price'])
        return self.optimized_df



    def optimize_expected_return(self,threshold,desired_return,number_of_stocks):
        self.calculate_weight_expected_return()
        optimal_number_of_stocks =  threshold
        desired_return = desired_return
        self.optimized_df = self.optimized_df.head(number_of_stocks)
        actual_return = self.optimized_df['Expected Return'].replace(np.nan, 0).to_numpy()
        actual_expected_return = sum(actual_return)


        if (actual_expected_return > desired_return):
            optimal_number_of_stocks = number_of_stocks
            desired_return = actual_expected_return

        if  number_of_stocks > threshold:
            return self.optimize_expected_return(self, threshold, desired_return, number_of_stocks - 1)
        else:
            self.optimized_df = self.optimized_df.head(optimal_number_of_stocks)
            return self.calculate_weight_expected_return()


    def top_stocks(self):
        stocks_df = self.update_metric_data_frame
        self.update_avg_metric_df
        stocks_df = self.calculate_strength_value
        stocks_df = stocks_df.sort_values(by=['Strength Value'], ascending=False)
        return stocks_df

    def build_portfolio(self,df,selected_ticker_list,threshold,desired_return,investing_amount):
        self.metric_df = df
        print("DFFF",df)
        self.update_avg_metric_df()
        self.optimized_df = df[df.Ticker.isin(selected_ticker_list)]
        optimized_df = self.calculate_strength_value()
        optimized_df = self.optimized_df.sort_values(by=['Strength'], ascending=False)
        optimized_df = self.optimize_expected_return(threshold,desired_return,number_of_stocks=len(selected_ticker_list)) 
        optimized_df = self.calculate_portfolio_value_distribution(investing_amount)
        optimized_df = self.total_share()
        return optimized_df

    def remove_empty_element(stock_list):
            while '' in stock_list:
                stock_list.remove('')


