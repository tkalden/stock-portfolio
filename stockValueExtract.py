# For data manipulation
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.valuation import Valuation
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.technical import Technical
import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

foverview = Overview()
fvaluation  = Valuation()
fownership = Ownership()
ftechnical = Technical()
fperformance = Performance()
financial = Financial()
ticker = Ticker()


def get_overview(filters_dict):
    foverview.set_filter(filters_dict=filters_dict)
    df = foverview.screener_view()
    return df


def get_valuation(filters_dict):
    fvaluation.set_filter(filters_dict=filters_dict)
    df = fvaluation.screener_view()
    return df


def get_financial(filters_dict):
    financial.set_filter(filters_dict=filters_dict)
    df = financial.screener_view()
    return df


def get_ownership(filters_dict):
    fownership.set_filter(filters_dict=filters_dict)
    df = fownership.screener_view()
    return df

def get_technical(filters_dict):
    ftechnical.set_filter(filters_dict=filters_dict)
    df = ftechnical.screener_view()
    return df


def get_filters():
    return foverview.get_filters()


def fundamental_metric(soup, metric):
    return soup.find(text=metric).find_next(class_='snapshot-td2').text


def update_mean_value_dic(df):
    df.replace(np.nan,0)
    avg_pe = df["P/E"].mean()
    avg_pc = df["P/C"].mean()
    avg_fpe = df["Fwd P/E"].mean()
    avg_peg = df["PEG"].mean()
    avg_pb = df["P/B"].mean()
    avg_div = pd.to_numeric(df["Dividend"]).mean()
   # avg_roe = df["ROE"].mean()
    #avg_roi = df["ROI"].mean()
    #avg_io = df["Insider Own"].mean()
    return {"pe": avg_pe, "pc": avg_pc, "fpe": avg_fpe, "peg": avg_peg, "pb": avg_pb,
            "div": avg_div
            #, "roe": avg_roe, "roi": avg_roi, "io": avg_io
            }


def get_stocks_by_sector_and_index(sector, index):
    valuation = get_valuation({'Index': index, 'Sector': sector})
    financial = get_financial({'Index': index, 'Sector': sector})
   # ownership = get_ownership({'Index': 'S&P 500', 'Sector': 'Basic Materials'})
    #technical = get_technical({'Index': 'S&P 500', 'Sector': 'Basic Materials'})
    df1 = valuation[['Ticker', 'P/C', 'P/E','Fwd P/E', 'PEG', 'P/B']]
    df2= financial[['Dividend', 'ROE', 'ROI']]
    #df3 = ownership["Insider Own"]
    #df4=technical["Beta"]

    df = pd.concat([df1,df2.reindex(df1.index)],axis=1)        
    df['Dividend'] = df['Dividend'].astype(str).str.replace('%', '')
    df['ROE'] = df['ROE'].astype(str).str.replace('%', '')
    df['ROI'] = df['ROI'].astype(str).str.replace('%', '')
   # df['Insider Own'] = df['Insider Own'].str.replace('%', '')
    return df


def get_fundamental_data(df):
    for symbol in df.index:
        try:
            url = ("http://finviz.com/quote.ashx?t=" + symbol.lower())
            req = Request(url=url, headers={
                          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
            response = urlopen(req)
            soup = BeautifulSoup(response, features="html.parser")
            for m in df.columns:
                df.loc[symbol, m] = fundamental_metric(soup, m)
        except Exception as e:
            print(e)
            print(symbol, 'not found')
    return df


def calculate_strength_value(df, metric_dic, stock_type,):
    strength_value = []
    for symbol in df.index:
        value = 0
        try:
            for m in df.loc[:, df.columns != 'Stock']:
                metricValue = df[m].iloc[symbol]
                if (np.isnan(metricValue) == False):
                    metricValue = float(metricValue)
                    value = update_strength_value(
                        value, m, metricValue, metric_dic, stock_type)
        except Exception as e:
            print(e)
        strength_value.append(value)
    df['Strength Value'] = strength_value
    return df


def calculate_weight_and_expected_return(df):
    strengthArray = get_array('Strength Value', df)
    weight_array = calculate_weight(strengthArray)
    roi_array = get_array('ROI', df)
    expected_return = calculate_expected_return(weight_array, roi_array)
    df['Weight'] = weight_array
    df['Expected Return'] = expected_return
    return df


def calculate_weight(strengthArray):
    return np.divide(strengthArray, sum(strengthArray))


def calculate_expected_return(weightArray, rateOfReturnArray):
    return np.multiply(weightArray, rateOfReturnArray)


def get_array(column, df):
    array = df[column].replace(np.nan, 0).to_numpy()
    return list(map(float, array))


def calculate_portfolio_value_distribution(total_amount, df):
    df['Invested Amount'] = np.multiply(df['Weight'], total_amount)
    return df


def total_share(df):
    df['Total Shares'] = np.divide(df['Invested Amount'], df['Price'])
    return df


def update_strength_value(value, m, metricValue, metric_dic, stock_type):
    if stock_type == 'Value':
        if m == 'P/E':
            value += np.subtract(metric_dic['pe'], metricValue)
        elif m == 'Forward P/E':
            value += np.subtract(metric_dic['fpe'], metricValue)
        elif m == 'P/C':
            value += np.subtract(metric_dic['pc'], metricValue)
        elif m == 'P/B':
            value += np.subtract(metric_dic['pb'], metricValue)
        elif m == 'PEG':
            value += np.subtract(metric_dic['peg'], metricValue)
        elif m == 'Dividend':
            value += np.subtract(metricValue, metric_dic['div'])
        elif m == 'Beta':
            value -= metricValue
    elif stock_type == 'Growth':
        if m == 'P/E':
            value += np.subtract(metricValue, metric_dic['pe'])
        elif m == 'Forward P/E':
            value += np.subtract(metricValue, metric_dic['fpe'])
        elif m == 'P/C':
            value += np.subtract(metricValue, metric_dic['pc'])
        elif m == 'P/B':
            value += np.subtract(metricValue, metric_dic['pb'])
        elif m == 'PEG':
            value += np.subtract(metricValue, metric_dic['peg'])
        elif m == 'Dividend':
            value += np.subtract(metric_dic['div'], metricValue)
        elif m == 'Beta':
            value += metricValue
    """ elif m == 'ROE':
        value += np.subtract(metricValue, metric_dic['roe'])
    elif m == 'ROI':
        value += np.subtract(metricValue, metric_dic['roi'])
    elif m == 'Insider Own':
        value += np.subtract(metricValue, metric_dic['io']) """
    # elif m == 'EPS (ttm)':
        #value += np.subtract(metricValue,metric_dic['epsttm)'])
    # elif m == 'EPS Q/Q':
        #value += np.subtract(metricValue,metric_dic['epsqq'])
    return value



def clean_data(df):
    df['Dividend %'] = df['Dividend %'].str.replace('%', '')
    df['ROE'] = df['ROE'].str.replace('%', '')
    df['ROI'] = df['ROI'].str.replace('%', '')
    df['EPS Q/Q'] = df['EPS Q/Q'].str.replace('%', '')
    df['Insider Own'] = df['Insider Own'].str.replace('%', '')
    df = df.apply(pd.to_numeric, errors='coerce')
    return df


def get_metric():
    return [
        'P/B',
        'P/E',  # below 15 consider cheap above 18 consider expensive
        'P/C',  # between 15 - 20 % consider good. lower the better
        'Forward P/E',  # between 10 - 25 is good
        'PEG',  # < 1 good , above > 1 unfavaroble
        'EPS (ttm)',  # 80 or higher good
        'Dividend %',  # between 2 and 4 good. we choose > 2.
        'ROE',  # between 15-20 % is considered good. we choose > 15.
        'ROI',  # 7% or above consider good
        'EPS Q/Q',  # 80 or above consider good
        'Insider Own',  # higher better
        'Beta',  # > 1 more volatle,
        'Price'
    ]


def change_index_to_col(df):
    df.reset_index(inplace=True)
    df = df.rename(columns={'index': 'Stock'})
    return df


def optimize_expected_return(df, number_of_stocks, desired_expected_return, threshold, optimal_number_of_stocks):

    desired_expected_return = desired_expected_return
    threshold = threshold
    number_of_stocks = number_of_stocks
    optimal_number_of_stocks = optimal_number_of_stocks
    original_df = df

    df_with_number_of_stocks = calculate_weight_and_expected_return(
        df.head(number_of_stocks))
    actual_return = get_array('Expected Return', df_with_number_of_stocks)
    actual_expected_return = sum(actual_return)

    if (actual_expected_return > desired_expected_return):
        optimal_number_of_stocks = number_of_stocks
        desired_expected_return = actual_expected_return

    if number_of_stocks > threshold:
        return optimize_expected_return(original_df, np.subtract(number_of_stocks, 1), desired_expected_return, threshold, optimal_number_of_stocks)
    else:
        return calculate_weight_and_expected_return(original_df.head(optimal_number_of_stocks))


def top_stocks(sector, index, stock_type):
    print(sector, index)
    stocks_df = get_stocks_by_sector_and_index(sector, index)
    avg_metric = update_mean_value_dic(stocks_df)
    stocks_df = calculate_strength_value(stocks_df, avg_metric, stock_type)
    stocks_df = stocks_df.sort_values(by=['Strength Value'], ascending=False)
    return stocks_df

def build_portfolio(sector, index, selected_ticker_list, stock_type, desired_expected_return, threshold, optimal_number_of_stocks, investing_amount):
    stocks_df = get_stocks_by_sector_and_index(sector, index)
    avg_metric = update_mean_value_dic(stocks_df)
    stocks_df = stocks_df[stocks_df["Ticker" == selected_ticker_list ]]
    stocks_df = calculate_strength_value(stocks_df, avg_metric, stock_type)
    stocks_df = stocks_df.sort_values(by=['Strength Value'], ascending=False)
    stocks_df = optimize_expected_return(stocks_df, number_of_stocks=len(
        selected_ticker_list), desired_expected_return=desired_expected_return, threshold=threshold, optimal_number_of_stocks=optimal_number_of_stocks)
    stocks_df = calculate_portfolio_value_distribution(investing_amount, stocks_df)
    stocks_df = total_share(stocks_df)
    #meta_dictionary = get_gs_meta()
    #write_to_gsheet(service_file_path=meta_dictionary.get('auth_json_path'), spreadsheet_id=meta_dictionary.get(
        #'spreadsheet_key'), sheet_name=meta_dictionary.get('wks_name'), data_df=stocks_df)
    return stocks_df


def get_optimized_result(df):
    optimized_expected_return = get_array('Expected Return', df)
    optimized_stock_list = list(df['Stock'].to_numpy())
    investing_amount = get_array('Invested Amount', df)
    total_shares = get_array('Total Shares', df)
    remove_empty_element(optimized_stock_list)
    optimized_weight = get_array('Weight', df)
    return {'Stock': optimized_stock_list, 'Optimized Expected Return': optimized_expected_return, 'Optimized Weight': optimized_weight, 'Amount to Invest': investing_amount, 'Number of Shares': total_shares}




def remove_empty_element(stock_list):
    while '' in stock_list:
        stock_list.remove('')


def append_optimized_results(optimization_results, optimized_portfolio):
    optimization_results.append(
        {'Optimized Expected Return (%)': optimized_portfolio['optimized_expected_return']})
    optimization_results.append(
        {'Optimized Stock List': optimized_portfolio['optimized_stock_list']})
    optimization_results.append(
        {'Optimized Weight List': optimized_portfolio['optimized_weight']})
    return optimization_results
