import utilities.helper as helper
import enums.enum as enum
import pandas as pd
from methods.stock import stock
from utilities.pickle import pickle
from cachetools import cached, TTLCache


pickle = pickle()
stock = stock()
cache = TTLCache(maxsize=1000, ttl=86400)

class chart():
     # init method or constructor
    def __init__(self):
        self.top_dict = []
 
    @cached(cache)
    def get_chart_data(self,stock_type,base_metric):
        sp_500_data = stock.cache_sp500_data()
        df = sp_500_data
        if base_metric == enum.Metric.STRENGTH.value:
            stock.update_avg_metric_dic('Any')
            df = stock.calculate_strength_value(df,stock_type)
        elif base_metric == enum.Metric.DIVIDEND.value:
            df = df.sort_values(by="dividend", ascending=False)
        return self.top_stocks(df,base_metric)
       
    def top_stocks(self,df,base_metric):
        self.top_dict = []
        sectors = helper.get_sector()
        sectors.remove('Any')
        for sector in sectors:
            new_df = df[df['Sector'] == sector].head(5)
            labels = new_df["Ticker"].values.tolist()
            chart_values = pd.DataFrame()
            if base_metric == enum.Metric.STRENGTH.value:
                chart_values = new_df["strength"]
            elif base_metric == enum.Metric.DIVIDEND.value:
                chart_values = new_df["dividend"] 
            values = chart_values.values.tolist()
            self.top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        return self.top_dict
    

    
