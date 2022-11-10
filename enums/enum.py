from enum import Enum

class IndexType(Enum):
    SP500 = 'S&P 500'
    DJIA = 'DJIA'

class StockType(Enum):
    VALUE = 'Value'
    GROWTH = 'Growth'
    NONE = ''

class RiskEnum(Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'

class Metric(Enum):
    STRENGTH = 'Strength'
    DIVIDEND = 'Dividend'


class PEFilter(Enum):
    HIGH = 'Over 25'
    LOW = 'Under 25'

class ErrorCode(Enum):
    INVALID_PAGE = "01"
    TOO_MANY_REQUEST = "02"
    OTHERS = "03"


class FunctionEnum(Enum):
    VALUATION = 'fvaluation'
    OWNERSHIP = 'fownership'
    TECHNICAL = 'ftechnical'
    PERFORMANCE = 'fperformance'
    FINANCIAL = 'financial'
    G_OVERVIEW = 'gOverview'
    G_VALUATION = 'gValuation'