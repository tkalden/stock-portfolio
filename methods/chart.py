import utilities.helper as helper
import enums.enum as enum
import pandas as pd
from methods.stock import stock
from utilities.pickle import pickle

pickle = pickle()
stock = stock()
class chart():
     # init method or constructor
    def __init__(self):
        self.top_dict = []
        self.sp_500_data = pd.DataFrame()

    def get_chart_data(self,stock_type,base_metric):
        df = pd.DataFrame()
        if self.sp_500_data.empty:
            df = stock.get_stock_data_by_sector_and_index('S&P 500','Any')
            if base_metric == enum.Metric.STRENGTH.value:
                stock.update_avg_metric_dic('Any')
                df = stock.calculate_strength_value(df,stock_type)
            elif base_metric == enum.Metric.DIVIDEND.value:
                df = df.sort_values(by="dividend", ascending=False)
            self.sp_500_data = df 
        return self.top_stocks(self.sp_500_data,base_metric)
       
    def top_stocks(self,df,base_metric):
        self.top_dict = []
        sectors = helper.get_sector()
        sectors.remove('Any')
        for sector in sectors:
            new_df = df[df['Sector'] == sector].head(5)
            labels = new_df["Ticker"].values.tolist()
            chart_values = pd.DataFrame()
            if base_metric == 'Strength':
                chart_values = new_df["strength"]
            elif base_metric == 'Dividend':
                chart_values = new_df["dividend"] 
            values = chart_values.values.tolist()
            self.top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        return self.top_dict
    

    
