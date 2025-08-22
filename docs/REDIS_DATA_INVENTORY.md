# Redis Data Inventory

Comprehensive documentation of all data stored in Redis across different APIs and services.

## 📊 Data Types Overview

| Data Type           | Key Pattern                                   | TTL        | Source            | Description               |
| ------------------- | --------------------------------------------- | ---------- | ----------------- | ------------------------- |
| **Stock Data**      | `stock_data:{index}:{sector}`                 | 7 days     | Finviz/Yahoo      | Raw stock market data     |
| **Strength Data**   | `strength_data:{stock_type}:{sector}:{index}` | 24 hours   | Calculated        | Processed strength scores |
| **Annual Returns**  | `annual_returns`                              | 24 hours   | Yahoo Finance     | Expected returns data     |
| **Average Metrics** | `average_metrics`                             | 24 hours   | Calculated        | Sector average metrics    |
| **Portfolio**       | `portfolio:{user_id}`                         | Persistent | User Created      | User portfolios           |
| **User**            | `users`                                       | Persistent | User Registration | User account data         |
| **Subscription**    | `subscriptions`                               | Persistent | Newsletter        | Email subscriptions       |

## 🔍 Detailed Data Breakdown

### 1. Stock Data (`stock_data:{index}:{sector}`)

**Purpose**: Raw stock market data from Finviz/Yahoo Finance
**TTL**: 7 days (604,800 seconds)
**Source**: Finviz API (primary), Yahoo Finance (fallback)

**Key Patterns**:
```
stock_data:S&P 500:Any          # All S&P 500 stocks
stock_data:S&P 500:Technology   # S&P 500 Technology stocks
stock_data:S&P 500:Healthcare   # S&P 500 Healthcare stocks
stock_data:DJIA:Financial       # DJIA Financial stocks
```

**Data Content**:
```json
{
  "Ticker": "AAPL",
  "Company": "Apple Inc.",
  "Sector": "Technology",
  "Index": "S&P 500",
  "price": "150.25",
  "Change": "2.5%",
  "Volume": "45.2M",
  "Market Cap": "2.5T",
  "pe": "25.5",
  "fpe": "24.2",
  "peg": "1.2",
  "pb": "3.2",
  "dividend": "0.5",
  "roe": "15.2",
  "beta": "1.1",
  "Last_Updated": "2025-08-16T17:30:00"
}
```

**APIs That Use This**:
- `/api/screener/data` - Stock screener
- `/api/chart/data` - Chart generation
- `/api/portfolio` - Portfolio building
- Scheduler daily refresh

### 2. Strength Data (`strength_data:{stock_type}:{sector}:{index}`)

**Purpose**: Calculated strength scores for value/growth analysis
**TTL**: 24 hours (86,400 seconds)
**Source**: Calculated from stock data

**Key Patterns**:
```
strength_data:value:Technology:S&P 500    # Value scores for tech stocks
strength_data:growth:Healthcare:S&P 500   # Growth scores for healthcare
strength_data:value:Any:S&P 500           # Value scores for all S&P 500
```

**Data Content**:
```json
{
  "Ticker": "AAPL",
  "Company": "Apple Inc.",
  "Sector": "Technology",
  "Index": "S&P 500",
  "dividend": 0.5,
  "pe": 25.5,
  "fpe": 24.2,
  "pb": 3.2,
  "beta": 1.1,
  "return_risk_ratio": 0.85,
  "strength": 0.75,  // Calculated strength score
  "Last_Updated": "2025-08-16T17:30:00"
}
```

**APIs That Use This**:
- `/api/chart/data` - Chart generation
- `/api/portfolio` - Portfolio optimization

### 3. Annual Returns (`annual_returns`)

**Purpose**: Expected annual returns and risk metrics
**TTL**: 24 hours (86,400 seconds)
**Source**: Yahoo Finance calculations

**Data Content**:
```json
{
  "Ticker": "AAPL",
  "expected_annual_return": "12.5",
  "expected_annual_risk": "8.2",
  "return_risk_ratio": "1.52",
  "Last_Updated": "2025-08-16T17:30:00"
}
```

**APIs That Use This**:
- All services that need return/risk data
- Portfolio optimization

### 4. Average Metrics (`average_metrics`)

**Purpose**: Sector average metrics for comparison
**TTL**: 24 hours (86,400 seconds)
**Source**: Calculated from stock data

**Data Content**:
```json
{
  "Sector": "Technology",
  "avg_pe": "28.5",
  "avg_pb": "4.2",
  "avg_dividend": "1.2",
  "avg_beta": "1.15",
  "Last_Updated": "2025-08-16T17:30:00"
}
```

### 5. Portfolio (`portfolio:{user_id}`)

**Purpose**: User-created portfolios
**TTL**: Persistent (no expiration)
**Source**: User actions

**Data Content**:
```json
{
  "portfolio_id": "user123_portfolio_1",
  "user_id": "user123",
  "name": "My Tech Portfolio",
  "stocks": [
    {"ticker": "AAPL", "shares": 10, "price": 150.25},
    {"ticker": "MSFT", "shares": 5, "price": 300.50}
  ],
  "total_value": 3002.50,
  "created_at": "2025-08-16T17:30:00"
}
```

### 6. User Data (`users`)

**Purpose**: User account information
**TTL**: Persistent
**Source**: User registration

**Data Content**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password_hash": "hashed_password",
  "created_at": "2025-08-16T17:30:00",
  "id": "user123"
}
```

### 7. Subscription (`subscriptions`)

**Purpose**: Newsletter subscriptions
**TTL**: Persistent
**Source**: User signup

**Data Content**:
```json
{
  "email": "user@example.com",
  "subscribed_at": "2025-08-16T17:30:00",
  "active": true
}
```

## 🔄 API Call Tracking

### Finviz API Calls

**Endpoints Called**:
- Valuation screener
- Financial screener
- Technical screener
- Ownership screener
- Performance screener

**Rate Limiting**: 1 call per second with exponential backoff

**Tracking Keys**:
```
redis_tracker:state          # Current state of all cached data
redis_tracker:api_calls      # History of API calls made
```

### Duplicate Prevention

**Pending Request Tracking**:
- Tracks requests in progress
- 5-minute timeout for pending requests
- Prevents multiple simultaneous calls for same data

**Cache Hit Tracking**:
- Records when cached data is used
- Tracks API calls vs cache hits ratio
- Monitors cache effectiveness

## 📈 Data Statistics

### Expected Data Volumes

| Data Type       | Records per Key | Total Keys | Total Records |
| --------------- | --------------- | ---------- | ------------- |
| Stock Data      | 50-500          | 24         | 1,200-12,000  |
| Strength Data   | 50-500          | 72         | 3,600-36,000  |
| Annual Returns  | 500             | 1          | 500           |
| Average Metrics | 11              | 1          | 11            |
| Portfolio       | 1-50            | Variable   | Variable      |
| User            | 1               | Variable   | Variable      |

### Memory Usage Estimates

| Data Type      | Size per Record | Total Size |
| -------------- | --------------- | ---------- |
| Stock Data     | ~2KB            | 2.4-24MB   |
| Strength Data  | ~1.5KB          | 5.4-54MB   |
| Annual Returns | ~500B           | 250KB      |
| Tracking Data  | ~1KB            | 1-2MB      |

**Total Estimated Memory**: 10-80MB

## 🛠️ Management Commands

### Check Cache Status
```bash
# Quick status
curl http://localhost:5001/api/cache/info

# Detailed status (admin only)
curl http://localhost:5001/api/cache/status
```

### Clear Cache
```bash
# Clear all cache
curl -X POST http://localhost:5001/api/cache/clear

# Clear specific data type
curl -X POST http://localhost:5001/api/cache/clear/stock_data
```

### Force Refresh
```bash
# Refresh all data
curl -X POST http://localhost:5001/api/scheduler/force-refresh

# Refresh specific sector
curl -X POST http://localhost:5001/api/scheduler/refresh \
  -H "Content-Type: application/json" \
  -d '{"index": "S&P 500", "sector": "Technology"}'
```

## 🎯 Best Practices

1. **Use Scheduler**: Let the scheduler populate cache automatically
2. **Monitor TTL**: Check cache expiration before making API calls
3. **Track Usage**: Monitor cache hit rates for optimization
4. **Avoid Duplicates**: Use pending request tracking
5. **Regular Cleanup**: Clear expired data periodically

## 🔍 Monitoring

### Key Metrics to Track
- Cache hit rate
- API call frequency
- Memory usage
- Data freshness
- Duplicate request prevention

### Log Messages to Watch
```
📊 Tracked data save: stock_data:S&P 500:Technology (stock_data) from finviz
📊 Tracked data access: stock_data:S&P 500:Technology
📡 Tracked API call: finviz -> screener_view (✅)
🔄 Request pending for stock_data:S&P 500:Technology
✅ Using cached data for S&P 500:Technology (150 records)
```
