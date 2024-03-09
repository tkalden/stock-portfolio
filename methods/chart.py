import logging

import pandas as pd

import enums.enum as enum
from methods.sourceDataMapper import SourceDataMapperService
from methods.stock import stock
from utilities.constant import SECTORS
from utilities.pickle import pickle

pickle = pickle()
stock = stock()
SourceDataMapperService = SourceDataMapperService()

class chart():
     # init method or constructor
    def __init__(self):
        self.index = 'S&P 500' #default
        self.sectors = SECTORS
 
    def get_chart_data(self,stock_type):
        logging.info(f"Getting chart data for {stock_type} Stock")
        stock.update_avg_metric_dic('Any') #first find the average values across all the sectors for SP500
        top_dict = []
        for sector in self.sectors:
            chart_values = pd.DataFrame()
            labels = []
            data = SourceDataMapperService.get_data_by_index_sector(self.index,sector)
            if stock_type == enum.StockType.GROWTH.value or stock_type == enum.StockType.VALUE.value:
                strength_data = stock.calculate_strength_value(data,stock_type).head(5)
                labels = strength_data["Ticker"]
                chart_values = strength_data["strength"]
            elif stock_type == enum.StockType.DIVIDEND.value:
                dividend_data = data.sort_values(by="dividend", ascending=False).head(5)
                labels = dividend_data["Ticker"]
                chart_values = dividend_data["dividend"]
            values = chart_values.tolist()
            labels= labels.tolist()
            top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        return top_dict
    
    

    
