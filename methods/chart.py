import utilities.helper as helper
import pandas as pd
from methods.stock import stock
from utilities.pickle import pickle

pickle = pickle()
stock = stock()
class chart():
     # init method or constructor
    def __init__(self):
        self.top_dict = []

    def get_chart_data(self,key,stock_type,base_metric,overwrite):
        df = pd.DataFrame()
        if pickle.checkFile(key) and not overwrite:
            df = pickle.unpickle_file(key)
        else:
            df = stock.get_stock_data_by_sector_and_index('S&P 500','Any')
            if base_metric == helper.Metric.STRENGTH.value:
                stock.update_avg_metric_dic('Any')
                df = stock.calculate_strength_value(df,stock_type)
            elif base_metric == helper.Metric.DIVIDEND.value:
                df = df.sort_values(by="dividend", ascending=False)
            pickle.pickle_file(df,key)  
        return self.top_stocks(df,base_metric)
       
    def top_stocks(self,df,base_metric):
        sectors = helper.get_sector()
        sectors.remove('Any')
        for sector in sectors:
            new_df = df[df['Sector'] == sector].head(5)
            labels = new_df["Ticker"].values.tolist()
            chart_values = pd.DataFrame()
            if base_metric == 'Strength':
                chart_values = new_df["strength"]
                #strength_values = np.divide(1,np.sum(strength_values)) * strength_values   
            elif base_metric == 'Dividend':
                chart_values = new_df["dividend"] 
            values = chart_values.values.tolist()
            self.top_dict.append({"id": sector, "values":values, "labels":labels, "title": sector})
        return self.top_dict
    

    
