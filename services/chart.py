import logging

import pandas as pd

import enums.enum as enum
from services.sourceDataMapper import SourceDataMapperService
from services.strengthCalculator import StrengthCalculator
from utilities.constant import SECTORS

strengthCalculator = StrengthCalculator()
sourceDataMapperService = SourceDataMapperService()


class chart():
     # init method or constructor
    def __init__(self):
        self.index = 'S&P 500' #default
        self.sectors = SECTORS
 
    def get_chart_data(self,stock_type):
        top_dict = []
        for sector in self.sectors:
            chart_values = pd.DataFrame()
            labels = []
            if stock_type == enum.StockType.GROWTH.value or stock_type == enum.StockType.VALUE.value:
                strength_data = strengthCalculator.calculate_strength_value(stock_type,sector,self.index).head(5)
                labels = strength_data["Ticker"]
                chart_values = strength_data["strength"]
            elif stock_type == enum.StockType.DIVIDEND.value:
                dividend_data = sourceDataMapperService.get_data_by_index_sector(index=self.index,sector=sector).sort_values(by="dividend", ascending=False).head(5)
                labels = dividend_data["Ticker"]
                chart_values = dividend_data["dividend"]
            values = chart_values.tolist()
            labels= labels.tolist()
            top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        logging.info(f'Top dict: {top_dict}')
        return top_dict
    
    

    
