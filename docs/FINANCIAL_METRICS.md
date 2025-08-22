# Financial Metrics & Analysis Methodology

## Overview

This document outlines the financial metrics, calculations, and methodologies used in the Stocknity application. All calculations are based on industry-standard financial analysis practices to ensure accuracy and reliability.

## Chart Analysis Metrics

### Value Stocks Analysis

**Purpose**: Identify stocks that are potentially undervalued relative to their fundamentals.

**Metrics Used**:
1. **P/E Ratio (Price-to-Earnings)** - 40% weight
2. **P/B Ratio (Price-to-Book)** - 30% weight  
3. **Dividend Yield** - 30% weight

**Calculation Method**:
```
Value Score = (1/P/E × 40) + (1/P/B × 30) + (Dividend Yield × 100 × 30)
```

**Interpretation**:
- **Lower P/E ratios** indicate potentially undervalued stocks
- **Lower P/B ratios** suggest stocks trading below book value
- **Higher dividend yields** provide income and indicate value characteristics
- **Higher scores** indicate better value characteristics

**Industry Standards**:
- P/E < 15: Generally considered value territory
- P/B < 1: Trading below book value
- Dividend Yield > 2%: Income-generating value stock

### Growth Stocks Analysis

**Purpose**: Identify stocks with strong growth potential and momentum.

**Metrics Used**:
1. **Sales Growth (5-Year)** - 40% weight
2. **PEG Ratio (Price/Earnings-to-Growth)** - 30% weight
3. **Forward P/E Ratio** - 30% weight

**Calculation Method**:
```
Growth Score = (Sales Growth × 40) + (1/PEG × 30) + (1/Forward P/E × 30)
```

**Interpretation**:
- **Higher sales growth** indicates expanding business
- **Lower PEG ratios** suggest growth is reasonably priced
- **Lower forward P/E ratios** indicate future earnings potential
- **Higher scores** indicate better growth characteristics

**Industry Standards**:
- Sales Growth > 10%: Strong growth company
- PEG < 1: Growth reasonably priced
- Forward P/E < 20: Future earnings potential

### Dividend Stocks Analysis

**Purpose**: Identify stocks with attractive dividend income potential.

**Metrics Used**:
- **Dividend Yield Percentage**

**Display Method**:
- Values shown as percentages (e.g., 5.2% = 5.2% annual dividend yield)
- Sorted by highest dividend yield first

**Interpretation**:
- **Higher percentages** indicate better dividend income
- **Sustainable yields** typically range from 2-6%
- **Very high yields** (>8%) may indicate risk

**Industry Standards**:
- 2-4%: Moderate dividend yield
- 4-6%: High dividend yield
- >6%: Very high yield (assess sustainability)

## Data Sources & Reliability

### Primary Data Sources
1. **Finviz Finance** - Primary source for fundamental data
2. **Yahoo Finance** - Fallback source for additional metrics
3. **Redis Cache** - Local caching for performance optimization

### Data Quality Assurance
- **Real-time validation** of numeric fields
- **Fallback mechanisms** when primary sources fail
- **Data cleaning** to handle missing or invalid values
- **Consistent formatting** across all metrics

### Update Frequency
- **Daily refresh** at 8:00 AM EST
- **Cache expiration** after 24 hours
- **Manual refresh** available via API endpoints

## Risk Disclaimers

### Important Notices
1. **Not Financial Advice**: This application provides analysis tools only
2. **Past Performance**: Historical data doesn't guarantee future results
3. **Market Risk**: All investments carry inherent market risk
4. **Due Diligence**: Users should conduct their own research

### Limitations
- **Data Lag**: Market data may have slight delays
- **Calculation Simplifications**: Complex financial scenarios may not be fully captured
- **Market Conditions**: Metrics may not reflect current market sentiment
- **Company-Specific Factors**: Qualitative factors not included in calculations

## Methodology Validation

### Industry Alignment
- **P/E Ratios**: Standard valuation metric used by professional analysts
- **P/B Ratios**: Common measure of book value relative to market price
- **PEG Ratios**: Growth-adjusted valuation metric
- **Dividend Yields**: Standard income measurement

### Calculation Verification
- **Mathematical accuracy** verified through unit tests
- **Edge case handling** for missing or extreme values
- **Consistent application** across all sectors and indices
- **Regular validation** against external financial data sources

## API Endpoints

### Chart Data Endpoints
- `GET /api/chart/value` - Value stock analysis
- `GET /api/chart/growth` - Growth stock analysis  
- `GET /api/chart/dividend` - Dividend stock analysis

### Data Format
```json
{
  "data": [
    {
      "id": "Sector Name",
      "values": [score1, score2, score3, score4, score5],
      "labels": ["TICKER1", "TICKER2", "TICKER3", "TICKER4", "TICKER5"],
      "title": "Sector Name"
    }
  ]
}
```

## Future Enhancements

### Planned Improvements
1. **Risk Metrics**: Beta, volatility, and downside risk calculations
2. **Quality Metrics**: ROE, ROA, and debt-to-equity ratios
3. **Momentum Indicators**: Price momentum and relative strength
4. **Sector Comparisons**: Cross-sector analysis and benchmarking
5. **Custom Weightings**: User-configurable metric importance

### Research Areas
- **Machine Learning**: Predictive modeling for stock selection
- **Alternative Data**: ESG scores, sentiment analysis
- **Portfolio Optimization**: Modern portfolio theory applications
- **Backtesting**: Historical performance validation

## Contact & Support

For questions about financial calculations or methodology:
- **Documentation**: This file and inline code comments
- **Code Review**: All calculations are open source and reviewable
- **Validation**: Independent verification encouraged

---

**Last Updated**: August 16, 2025
**Version**: 1.0.0
**Next Review**: Quarterly basis
