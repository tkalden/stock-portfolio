import asyncio
import logging
import math

import pandas as pd
from pandas_datareader import data

from methods.sourceDataMapper import SourceDataMapperService
from utilities.redis import (check_data_from_redis, fetch_data_from_redis,
                             save_data_to_redis)

logger_format = '%(asctime)s:%(threadName)s:%(message)s'
logging.basicConfig(format=logger_format, level=logging.INFO, datefmt="%H:%M:%S")

SourceDataMapperService = SourceDataMapperService()

async def get_result(n):
    logging.info(f"Start Task {n}")
    df = await get_annual_return(n)
    logging.info(f"End Task {n}")
    return df

async def gather_result(ticker_lists):
   logging.info("Main started")
   return await asyncio.gather(*[get_result(n) for n in zip(*(iter(ticker_lists),) * 10)])


async def get_annual_return(ticker_lists):
    # We would like all available data from 01/01/2000 until 12/31/2016.
    start_date = '2018-01-01'
    end_date = '2022-10-31'
    # User pandas_reader.data.DataReader to load the desired data. As simple as that.
    panel_data = data.DataReader(ticker_lists, 'yahoo', start_date, end_date)
    close = panel_data['Adj Close']
    # Getting all weekdays between 01/01/2000 and 12/31/2016
    all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
    # How do we align the existing prices in adj_close with our new set of dates?
    # All we need to do is reindex close using all_weekdays as the new index
    close = close.reindex(all_weekdays)
    # Reindexing will insert missing values (NaN) for the dates that were not present
    # in the original set. To cope with this, we can fill the missing by replacing them
    # with the latest available price for each instrument.
    close = close.fillna(method='ffill')
    daily_simple_returns = close.pct_change(1)
    df =  pd.DataFrame()
    annual_return = daily_simple_returns.mean()*252
    df['expected_annual_return'] = annual_return
    df['expected_annual_risk'] = daily_simple_returns.std()*math.sqrt(252)
    df['return_risk_ratio'] =  df['expected_annual_return']/  df['expected_annual_risk']
    df.reset_index(inplace=True)
    df = df.rename(columns = {'Symbols':'Ticker'})
    return df

def get_annual_return_data():
    key = 'annual-return'
    if check_data_from_redis(key):
        return fetch_data_from_redis(key)
    df1 = SourceDataMapperService.get_data_by_index('S&P 500')
    ticker_lists = df1['Ticker'].tolist()
    logging.info(f"Ticker List {ticker_lists}")
    df = pd.concat(asyncio.run(gather_result(ticker_lists)),axis = 0)
    save_data_to_redis(df,'annual_return')
    return data

