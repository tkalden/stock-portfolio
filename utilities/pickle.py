import pandas as pd
import numpy as np
import logging
import utilities.helper as helper
from utilities.redis_data import redis_manager

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
        """Save data to Redis instead of BigQuery"""
        logging.info('Saving data to Redis')
        # For now, save to a generic key - you might want to parse table_id
        return redis_manager.save_stock_data(df, "default", "default")