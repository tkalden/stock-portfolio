
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
        self.selected_df = pd.DataFrame()
        self.metric_df = pd.DataFrame()
        self.avg_metric_df = pd.DataFrame()
        self.avg_metric_dictionary = {}
        self.stock_type = stock_type
        self.index = index
    
    def update_metric_df(self,df):
        self.metric_df = df
        return self.metric_df

    def get_ticker_list(self):
        return self.metric_df["Ticker"].to_numpy()
    
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
        return self.avg_metric_df 
    
    def update_avg_metric_dic(self):
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
        return self.avg_metric_dictionary

    
    def calculate_strength_value(self):
        self.update_avg_metric_dic
        pe =  self.metric_dic['pe'] - self.metric_df['P/E']
        fpe =  self.metric_dic['fpe'] - self.metric_df['Forward P/E']
        pc = self.metric_dic['pc'] - self.metric_df['P/C']
        pb = self.metric_dic['pb'] - self.metric_df['P/B']
        peg = self.metric_dic['peg'] - self.metric_df['PEG']
        div =  self.metric_df['Dividend'] - self.metric_dic['div']
        combination = pe + fpe + pc + pb + peg + div
        if self.stock_type == 'Value':
            self.metric_df["Strength"] = combination 
        elif self.stock_type == 'Growth':
            self.metric_df["Strength"] = -1 * combination  # -1 because Growth has opposite metric values
        else :
            raise ValueError("Stock Type must be Value or Growth")
        return self.metric_df


    def calculate_weight_expected_return(self):
        strengthArray  = self.metric_df["Strength"].replace(np.nan, 0).to_numpy()
        strengthList = list(map(float, strengthArray))
        weight_array = np.divide(strengthList, sum(strengthList))
        self.metric_df["Weight"] = weight_array
        self.metric_df["Expected Return"] = self.metric_df["ROI"].replace(np.nan, 0) * self.metric_df["Weight"]
        return self.metric_df['Weight']
    
    def calculate_portfolio_value_distribution(self,investing_amount):
        self.metric_df['Invested Amount'] = np.multiply(self.metric_df['Weight'], investing_amount)
        return self.metric_df['Invested Amount'] 


    def total_share(self):
        self.metric_df['Total Shares'] = np.divide(self.metric_df['Invested Amount'], self.metric_df['Price'])
        return self.metric_df



    def optimize_expected_return(self,threshold,desired_return,number_of_stocks):
        self.calculate_weight_expected_return(self)
        actual_return = self.metric_df["Expected Return"].replace(np.nan, 0).to_numpy()
        actual_expected_return = sum(actual_return)
        number_of_stocks = number_of_stocks
        optimal_number_of_stocks =  number_of_stocks
        desired_return = desired_return

        if (actual_expected_return > desired_return):
             desired_return = actual_expected_return

        if  number_of_stocks > threshold:
            number_of_stocks = number_of_stocks - 1
            return self.optimize_expected_return(self, threshold, desired_return, number_of_stocks)
        else:
            self.metric_df = self.avg_metric_df.head(optimal_number_of_stocks)
            return self.calculate_weight_expected_return(self)


    def top_stocks(self):
        stocks_df = self.update_metric_data_frame
        self.update_avg_metric_df
        stocks_df = self.calculate_strength_value
        stocks_df = stocks_df.sort_values(by=['Strength Value'], ascending=False)
        return stocks_df

    def build_portfolio(self,selected_ticker_list,threshold,desired_return,investing_amount):
        stocks_df = self.update_metric_data_frame
        self.update_avg_metric_df
        stocks_df = stocks_df[stocks_df["Ticker" == selected_ticker_list ]]
        stocks_df = self.calculate_strength_value
        stocks_df = stocks_df.sort_values(by=['Strength Value'], ascending=False)
        stocks_df = self.optimize_expected_return(self, threshold,desired_return,number_of_stocks=len(
            selected_ticker_list)) 
        stocks_df = self.calculate_portfolio_value_distribution(investing_amount)
        stocks_df = self.total_share
        return stocks_df

    def remove_empty_element(stock_list):
            while '' in stock_list:
                stock_list.remove('')


