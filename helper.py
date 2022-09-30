def get_stock_dict():
    return [{"label": "stock", "title": "Stock1", "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock2",
                "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock3",
                "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock4",
                "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock5",
                "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock6",
                "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock7",
                "placeholder": "Enter Stock Ticker"},
            {"label": "stock", "title": "Stock8",
                "placeholder": "Enter Stock Ticker"}]

def get_sector_and_index():
    return [{"label": "index", "content": get_index(), "title":"Select Index"},
        {"label": "sector", "content": get_sector(), "title": "Selected Sector"}]

def get_optimization_parameters():
    return [{"label": "index", "title": "Index", "placeholder": "Market Index"},
        {"label": "sector", "title": "Sector", "placeholder": "Enter Sector"},
        {"label": "stock_type", "title": "stock_type", "placeholder": "Select Stock Type"},
        {"label": "investing_amount", "title": "Investing Amount ($)", "placeholder": "Amount to Invest"},
            {"label": "threshold", "title": "Threshold",
                "placeholder": "Min. number of Stocks"},
            {"label": "expected_return_value",
                "title": "Expected Return (%)", "placeholder": "Enter Expected Return"},
            {"label": "high_risk_flag",
             "title": "High Risk Flag (True or False)", "placeholder": "True or False"}]

def get_sector():
    return ['Basic Materials', 'Energy', 'Communication Services', 'Consumer Cyclical', 'Healthcare', 'Industrials', 'Real Estate', 'Financial', 'Consumer Defensive', 'Technology', 'Utilities']

def get_index():
    return ['DJIA','S&P 500']

def get_exchange():
     return ['NASDAQ','NYSE','AMEX']

def get_stock_type():
    return ['Value','Growth']
