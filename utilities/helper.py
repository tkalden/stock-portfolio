import numpy as np
import enums.enum as enum

def get_stock_dict(ticker_list):
    return {"label": "stock", "title": "Stock1", "ticker_list": ticker_list}

def index_select_attributes():
    return [{"label": "index", "content": get_index(), "title": "Select Index"},
            {"label": "sector", "content": get_sector(), "title": "Select Sector"},
            {"label": "stock_type", "content": get_stock_type(),
             "title": "Select Stock Type"}
            ]

def index_sector():
    return [{"label": "index", "content": get_index(), "title": "Select Index"},
            {"label": "sector", "content": get_sector(), "title": "Select Sector"},
            ]
def build_porfolio_column():
    return ['Ticker',
            'Price ($)',
            'Expected Return (%)',
            'Expected Risk (%)',
            'Expected Ratio (%)',
            'Weight (%)',
            'Weighted Expected Return (%)',
            'Total Shares',
            'Invested Amount ($)']

def get_optimization_parameters():
    return [{"label": "investing_amount",
             "title": "Investing Amount ($)", "placeholder": "Amount to Invest"},
            {"label": "expected_return_value",
             "title": "Expected Return (%)", "placeholder": "Enter Expected Return"}]

def get_pickle_file():
    return {"dividend":"./pickleFiles/dividendchart.pkl",
            "value":"./pickleFiles/valuechart.pkl",
            "growth":"./pickleFiles/growthchart.pkl",
            "stock":"./pickleFiles/stock.pkl",
            "screener":"./pickleFiles/screener.pkl",
            "portfolio":"./pickleFiles/portfolio.pkl"
        }

def get_sector():
    return ['Basic Materials', 'Energy', 'Communication Services', 'Consumer Cyclical', 'Healthcare', 'Industrials', 'Real Estate', 'Financial', 'Consumer Defensive', 'Technology', 'Utilities', 'Any']


def get_index():
    return ['DJIA', 'S&P 500']


def get_exchange():
    return ['NASDAQ', 'NYSE', 'AMEX']


def get_stock_type():
    return [enum.StockType.VALUE.value, enum.StockType.GROWTH.value]

# convert to dictionary
def get_valuation_metric():
    return ['Ticker', 'P/E', 'Fwd P/E', 'PEG', 'P/B', 'P/C', 'Price','Dividend', 'ROE', 'ROI','Insider Own','Beta']

def get_goverview_metric():
    return ['Dividend']

def get_gvaluation_metric():
    return ['Name','P/E', 'Fwd P/E', 'PEG', 'P/B', 'P/C']

def portfolio_attributes():
    return ['Ticker','price', 'expected_annual_return', 'weight','expected_annual_risk', 'return_risk_ratio', 'total_shares', 'invested_amount','weighted_expected_return']

def risk():
    return ['High', 'Medium', 'Low']


def round_decimal_place(df,roundArray):
        for a in roundArray:
            df[a] = np.round(df[a].astype(float), decimals = 3)
        return df




