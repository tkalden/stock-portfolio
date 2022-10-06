# Portfolio Investment

The goal of this project is to build a portfolio for a list of stocks with the weight of each stock calculated from the analysis of financial indicators or metrics.

## 
We pull metric data for a given stock from finviz website (https://finviz.com/quote.ashx?t={stock}&ty=c&ta=1&p=d). 
For each stock in the list we compare its metric value against the avg value of sector it belongs to. 

| P/B | P/E     | P/C  | Forward P/E | PEG | Dividend % | ROE  | ROI | Beta |

Assumption is that for growth stock : higher value of these metrics except (dividend) is preffered whereas the opposite is true for the value stock. A weight of individual stock is the ratio of

```
weight_A = strength_value_A / sum (strength_value) across all stocks

```

### Metric Descriptions

The stock metric description is directly pulled from (http://finviz.com/quote.ashx).

### Market Cap
The total dollar value of all of a company's outstanding shares. Market capitalization is a measure of corporate size.
```
Market Capital = Current Market Price * Number Of Shares Outstanding
Shares Outstanding = Total Number Of Shares - Shares Held In Treasury
Float = Shares Outstanding - Insider Shares - Above 5% Owners - Rule 144 Shares
```
### P/E
A popular valuation ratio of a company's current share price compared to its per-share earnings (trailing twelve months). Low P/E value indicates a stock is relatively cheap compared to its earnings. For instance, a P/E value of 15 means that the current price equals the sum of 15-year earnings per share. The average level varies across the market. Therefore, P/E value should be compared per sector or industry.
```
P/E = Current Market Price / Earnings Per Share (EPS)
P/E = Average Common Stock Price / Net Income Per Share
EPS = (Net Income - Dividends On Preferred Stock) / Average Outstanding Shares
```
### PEG
A ratio used to determine a stock's value while taking into account the earnings' growth. PEG is used to measure a stock's valuation (P/E) against its projected 3-5 year growth rate. It is favored by many over the price/earnings ratio because it also takes growth into account. A lower PEG ratio indicates that a stock is undervalued.
```
PEG = (P/E) / Annual EPS Growth
```
 ```
 = 1 - fairly valued
 < 1 - undervalued (a good indicator that a stock will outperform over the next few years)
> 1 - overvalued
```
### Price / Cash
A ratio used to compare a stock's market value to its cash assets. It is calculated by dividing the current closing price of the stock by the latest quarter's cash per share.## Usage
```
P/C = Current Market Price / Cash per Share
```

### Relative Price Strength
Relative price strength (RPS), also known as relative strength, is the ratio between the price trend of a stock price compared to the price trend of the market

### Accumulation / Distribution 
The accumulation/distribution indicator (A/D) is a cumulative indicator that uses volume and price to assess whether a stock is being accumulated or distributed

### Beta 
A measure of a stock's price volatility relative to the market. An asset with a beta of 0 means that its price is not at all correlated with the market. A positive beta means that the asset generally follows the market. A negative beta shows that the asset inversely follows the market, decreases in value if the market goes up.

### Volatility
A statistical measure of the dispersion of returns for a given stock. Represents average daily high/low % range.

### Return On Investment

Performance measure used to evaluate the efficiency of an investment or to compare the efficiency of a number of different investments. To calculate ROI, the benefit (return) of an investment is divided by the cost of the investment.

```
ROI = (Gain from Investment - Cost of Investment) / Cost of Investment.

```


## Further Analysis
For greater certainty about a stock's prospects, it's important to use a company's EPS Rating in conjunction with its Composite Rating, Relative Strength Rating and Accumulation/Distribution score.

