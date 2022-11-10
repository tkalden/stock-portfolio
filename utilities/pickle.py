import pandas as pd
import numpy as np
import logging
import utilities.helper as helper
import utilities.bigQuery as bigQuery

logging.basicConfig(level = logging.INFO)

class pickle():

    def pickle_file(self, df, key):
        logging.info('Pickle DF')
        return df.to_pickle(helper.get_pickle_file()[key])

    def unpickle_file(self,key):
        return pd.read_pickle(helper.get_pickle_file()[key])
    
    def checkFile(self,key):
        result = True
        try:
            pd.read_pickle(helper.get_pickle_file()[key])
        except:
            result = False
        return result
    
    def save_data(self, df, table_id):
         return bigQuery.write_to_bigquery(df,table_id)