def load_constant():
       return {
        "table_names": {
            'metric':'stockdataextractor.stock.average-metric',
            'porfolio':'stockdataextractor.stock.portfolio-table',
            'user':'stockdataextractor.stock.user-table',
            'subscription':'stockdataextractor.stock.subscription-table'
        }
       }
SECTORS = ['Basic Materials', 'Energy', 'Communication Services', 'Consumer Cyclical', 'Healthcare', 'Industrials', 'Real Estate', 'Financial', 'Consumer Defensive', 'Technology', 'Utilities']
INDEX = ['DJIA', 'S&P 500']
COLUMNS = ['Ticker', 'P/E', 'Fwd P/E', 'PEG', 'P/B', 'P/C', 'Price','Dividend', 'ROE', 'ROI','Insider Own','Beta']
AVG_METRIC_COLUMNS = ['Name','P/E', 'Fwd P/E', 'PEG', 'P/B', 'P/C','Dividend']