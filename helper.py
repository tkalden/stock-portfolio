from enum import Enum


def get_stock_dict(ticker_list,size):
    total_list =  [{"label": "stock", "title": "Stock1", "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock2",
                "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock3",
                "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock4",
                "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock5",
                "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock6",
                "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock7",
                "ticker_list": ticker_list},
            {"label": "stock", "title": "Stock8",
                "ticker_list": ticker_list}]
    if size < 10 :
        return total_list[0:size]
    else :
         return total_list


def index_select_attributes():
    return [{"label": "index", "content": get_index(), "title": "Select Index"},
            {"label": "sector", "content": get_sector(), "title": "Selected Sector"},
            {"label": "stock type", "content": get_stock_type(),
             "title": "Select Stock Type"}
            ]


def get_optimization_parameters():
    return [{"label": "investing_amount",
             "title": "Investing Amount ($)", "placeholder": "Amount to Invest"},
            {"label": "threshold", "title": "Threshold",
             "placeholder": "Min. number of Stocks"},
            {"label": "expected_return_value",
             "title": "Expected Return (%)", "placeholder": "Enter Expected Return"},
            {"label": "high_risk_flag",
             "title": "High Risk Flag (True or False)", "placeholder": "True or False"}]


def get_sector():
    return ['Basic Materials', 'Energy', 'Communication Services', 'Consumer Cyclical', 'Healthcare', 'Industrials', 'Real Estate', 'Financial', 'Consumer Defensive', 'Technology', 'Utilities']


def get_index():
    return ['DJIA', 'S&P 500']


def get_exchange():
    return ['NASDAQ', 'NYSE', 'AMEX']


def get_stock_type():
    return [StockType.VALUE.value, StockType.GROWTH.value]

# convert to dictionary


def get_valuation_metric():
    return ['Ticker', 'P/E', 'Fwd P/E', 'PEG', 'P/B', 'P/C', 'Price']


def get_financial_metric():
    return ["Dividend", "ROE", "ROI"]


def get_ownership_metric():
    return ['Insider Own']


def get_techical_metric():
    return ['Beta']


def get_techical_metric():
    return ['Beta']


def get_goverview_metric():
    return ['Dividend']


def get_gvaluation_metric():
    return ['Name','P/E', 'Fwd P/E', 'PEG', 'P/B', 'P/C']


class StockType(Enum):
    VALUE = 'Value'
    GROWTH = 'Growth'


class PEFilter(Enum):
    HIGH = 'Over 25'
    LOW = 'Under 25'


class FunctionEnum(Enum):
    VALUATION = 'fvaluation'
    OWNERSHIP = 'fownership'
    TECHNICAL = 'ftechnical'
    PERFORMANCE = 'fperformance'
    FINANCIAL = 'financial'
    G_OVERVIEW = 'gOverview'
    G_VALUATION = 'gValuation'
