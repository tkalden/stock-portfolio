# Stocknity API Server

A Flask-based REST API server for stock portfolio management and analysis. This is the backend API that powers the Stocknity frontend application.

## Features

- **Stock Data Management**: Fetch and cache stock data from Finviz
- **Portfolio Optimization**: Build and optimize stock portfolios using various algorithms
- **User Management**: User registration, authentication, and portfolio persistence
- **Redis Caching**: Fast data access with Redis caching layer
- **Scheduled Data Updates**: Daily data refresh at 8 AM
- **RESTful API**: Clean API endpoints for frontend integration

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Redis (for caching and data storage)
- **Authentication**: Flask-Login
- **Data Processing**: Pandas, NumPy
- **Stock Data**: FinvizFinance
- **Scheduling**: Python schedule library
- **Containerization**: Docker & Kubernetes ready

## API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration
- `POST /api/logout` - User logout
- `POST /api/subscribe` - Newsletter subscription

### User Management
- `GET /api/profile` - Get user profile (requires authentication)

### Stock Data
- `GET /api/home` - Get news and home page data
- `GET /api/screener/data` - Get stock screener data
- `POST /api/screener` - Update screener filters

### Portfolio Management
- `GET /api/portfolio/data` - Get current portfolio data
- `POST /api/portfolio` - Build/Optimize/Save portfolios
- `GET /api/my-portfolio/data` - Get user's saved portfolios
- `POST /api/delete-portfolio/<portfolio_id>` - Delete a portfolio
- `POST /api/clear-built-portfolio` - Clear current built portfolio

### Charts
- `GET /api/chart/<chart_type>` - Get chart data (value/growth/dividend)

## Getting Started

### Prerequisites

- Python 3.8+
- Redis server
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-portfolio
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Redis**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # Or install Redis locally
   # Follow Redis installation guide for your OS
   ```

5. **Configure environment variables**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export REDIS_HOST="localhost"
   export REDIS_PORT="6379"
   export REDIS_DB="0"
   ```

### Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the API**
   - API will be available at `http://localhost:5001`
   - Health check: `GET http://localhost:5001/`

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t stocknity-api .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## API Usage Examples

### User Registration
```bash
curl -X POST http://localhost:5001/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "SecurePass123!",
    "confirm": "SecurePass123!"
  }'
```

### User Login
```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Get Stock Data
```bash
curl http://localhost:5001/api/screener/data
```

### Build Portfolio
```bash
curl -X POST http://localhost:5001/api/portfolio \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "btn=Build&sector=Technology&index=S&P 500&stock_type=value&investing_amount=10000&max_stock_price=100&risk_tolerance=medium"
```

## Data Flow

1. **Scheduled Data Fetching**: Daily at 8 AM, the scheduler fetches:
   - Stock data from Finviz
   - Annual returns and risk data
   - Strength calculations for all stocks

2. **Redis Caching**: All data is cached in Redis for fast access

3. **Portfolio Operations**: 
   - Build portfolios using top stocks or custom selections
   - Optimize portfolios based on risk tolerance and return expectations
   - Save portfolios to Redis (persistent, no TTL)
   - Delete portfolios on demand

## Development

### Project Structure
```
stock-portfolio/
├── app.py                 # Main application entry point
├── __init__.py           # Flask app factory
├── main.py               # Main API routes
├── auth.py               # Authentication routes
├── services/             # Business logic services
│   ├── portfolio.py      # Portfolio management
│   ├── screener.py       # Stock screening
│   ├── chart.py          # Chart data
│   └── ...
├── utilities/            # Utility functions
│   ├── redis_data.py     # Redis data manager
│   ├── userFunction.py   # User CRUD operations
│   └── ...
├── scheduler.py          # Data scheduling
└── requirements.txt      # Python dependencies
```

### Adding New Endpoints

1. Add route in `main.py` or `auth.py`
2. Return JSON responses using `jsonify()`
3. Include proper error handling and status codes
4. Add authentication decorators where needed

### Testing

```bash
# Test API health
curl http://localhost:5001/

# Test stock data
curl http://localhost:5001/api/screener/data

# Test with authentication
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## Frontend Integration

This API is designed to work with the separate `stocknity-ui` React frontend. The frontend should:

- Make HTTP requests to the API endpoints
- Handle authentication with cookies/sessions
- Display data returned in JSON format
- Handle error responses appropriately

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

