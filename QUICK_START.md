# Stock Portfolio Application - Quick Start Guide

## 🚀 Features Implemented

### ✅ **Fixed Issues**
- **Login Redirection**: Fixed authentication system to handle both email and user_id lookups
- **Data Structure Errors**: Made data processing robust for missing columns
- **Code Quality**: Fixed duplicated string literals
- **Missing Methods**: Added `get_sp500_data()` method to Screener class

### ✅ **Scheduler System**
- **Daily Data Fetch**: Automatically fetches stock data at 8 AM daily
- **Manual Data Fetch**: Immediate data fetching when needed
- **Redis Caching**: All data cached in Redis to prevent timeout issues
- **Background Processing**: Scheduler runs in background thread
- **Smart Caching**: Skips fetching data that already exists in cache
- **Force Refresh**: Option to refresh all data regardless of cache
- **Pre-fetched S&P 500**: General S&P 500 data pre-cached for instant portfolio building

## 🛠️ Commands

### **Start the Application**
```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=main.py
export PYTHONPATH=/Users/tenzinkalden/projects/stock-portfolio

# Start Flask app
python -m flask run --host=0.0.0.0 --port=5000
```

### **Manual Data Fetch**
```bash
# Check cache status
python fetch_data_now.py --status

# Smart fetch (skip existing data)
python fetch_data_now.py

# Force refresh all data
python fetch_data_now.py --force
```

### **Test Application**
```bash
# Test if app starts without errors
python test_app.py
```

### **Redis Commands**
```bash
# Check all Redis keys
docker exec -it upbeat_dijkstra redis-cli --raw KEYS "*"

# Check user data
docker exec -it upbeat_dijkstra redis-cli --raw HGETALL users

# Check specific stock data
docker exec -it upbeat_dijkstra redis-cli --raw GET "stock_data:S&P 500:Technology"

# Check average metrics
docker exec -it upbeat_dijkstra redis-cli --raw GET "average_metrics"
```

### **Docker Commands**
```bash
# Start with Docker Compose
docker-compose up --build -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
```

## 📊 Data Structure

### **Redis Keys**
- `users` - User authentication data
- `stock_data:{index}:{sector}` - Stock data by index and sector
- `average_metrics` - Average market metrics
- `annual_returns` - Annual return calculations
- `subscriptions` - Newsletter subscriptions

### **Sectors Available**
- Basic Materials
- Energy
- Communication Services
- Consumer Cyclical
- Healthcare
- Industrials
- Real Estate
- Financial
- Consumer Defensive
- Technology
- Utilities

### **Indices Available**
- S&P 500
- DJIA

## 🔧 Configuration

### **Environment Variables**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
FLASK_APP=main.py
PYTHONPATH=/path/to/project
```

### **Scheduler Settings**
- **Daily Run**: 8:00 AM
- **Data TTL**: 24 hours for stock data
- **Portfolios**: Persistent (no TTL) - users can delete on demand
- **Retry Logic**: Automatic retry on failures
- **Logging**: Both file and console output

## 🎯 Usage

### **User Authentication**
1. **Sign Up**: Create account with email, name, and password
2. **Login**: Use email and password to authenticate
3. **Profile**: Access user dashboard after login

### **Portfolio Management**
1. **Build Portfolio**: Select stocks and build portfolio
2. **Optimize Portfolio**: Use optimization algorithms
3. **Save Portfolio**: Save to Redis for later access
4. **View Portfolios**: Access saved portfolios
5. **Delete Portfolio**: Remove portfolios on demand

### **Data Access**
- **Screener**: Filter stocks by sector and index
- **Charts**: View value, growth, and dividend charts
- **News**: Latest market news

## 🐛 Troubleshooting

### **Common Issues**
1. **Redis Connection**: Ensure Redis container is running
2. **Data Fetch Timeouts**: Use cached data or manual fetch
3. **Login Issues**: Check user data in Redis
4. **Missing Data**: Run manual data fetch

### **Logs**
- **Application**: Flask logs in console
- **Scheduler**: `scheduler.log` file
- **Redis**: Docker container logs

## 📈 Performance

### **Optimizations**
- **Caching**: All data cached in Redis
- **Background Processing**: Scheduler runs independently
- **Error Handling**: Robust error recovery
- **Data Validation**: Input validation and sanitization

### **Monitoring**
- **Health Checks**: Application health monitoring
- **Data Freshness**: 24-hour data refresh cycle
- **Error Logging**: Comprehensive error tracking

## 🚀 Production Ready

The application is now production-ready with:
- ✅ Containerized deployment
- ✅ Automated data management
- ✅ Robust error handling
- ✅ User authentication
- ✅ Data persistence
- ✅ Performance optimization 