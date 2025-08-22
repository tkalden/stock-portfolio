# Stocknity - Advanced Stock Portfolio Management System

A comprehensive stock portfolio management application featuring professional-grade optimization algorithms, real-time data analysis, and an intuitive React frontend.

## 🚀 Features

### Core Features
- **Stock Data Management**: Real-time data from Finviz with Redis caching
- **Professional Portfolio Optimization**: 4 advanced algorithms (Markowitz, Risk Parity, Max Sharpe, HRP)
- **AI-Powered Analysis**: Machine learning sentiment analysis and stock recommendations
- **User Management**: Secure authentication and portfolio persistence
- **Advanced Analytics**: Backtesting, risk metrics, and performance comparison
- **Responsive UI**: Modern React frontend with Bootstrap
- **Scheduled Updates**: Daily data refresh at 8 AM
- **Kubernetes Ready**: Full containerization with minikube support
- **Async Data Processing**: Background task queue with multiple data sources and fallbacks

### Advanced Portfolio Optimization
- **Modern Portfolio Theory (Markowitz)**: Nobel Prize-winning approach
- **Risk Parity**: Equal risk contribution strategy
- **Maximum Sharpe Ratio**: Optimal risk-adjusted returns
- **Hierarchical Risk Parity (HRP)**: Machine learning-based clustering
- **Comprehensive Backtesting**: Historical performance analysis
- **Risk Metrics**: VaR, CVaR, maximum drawdown, volatility

### Async Data Processing System
- **Multiple Data Sources**: Finviz (primary) + Yahoo Finance (fallback)
- **Background Task Queue**: Redis-based message queue with priority processing
- **Rate Limiting**: Intelligent API rate limiting to respect service limits
- **Automatic Retries**: Exponential backoff with configurable retry attempts
- **Real-time Monitoring**: Queue statistics and task status tracking
- **Scheduled Operations**: Daily data refresh, hourly health checks, weekly cleanup
- **Manual Control**: API endpoints for manual data refresh and force updates

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with Python 3.8+
- **Database**: Redis for caching and data storage
- **Authentication**: Flask-Login with session management
- **Data Processing**: Pandas, NumPy, SciPy
- **Optimization**: CVXPY, scikit-learn
- **Containerization**: Docker & Kubernetes
- **Async Processing**: aiohttp, asyncio, Redis-based message queue

### Frontend (React)
- **Framework**: React 18 with TypeScript
- **UI Library**: React Bootstrap
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Routing**: React Router

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Redis server
- Docker (optional)
- minikube (for Kubernetes deployment)

### Backend Setup

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd stock-portfolio
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies and setup**
   ```bash
   # Using Makefile (recommended)
   make setup
   
   # Or manually
   pip install -r requirements.txt
   ```

3. **Start Redis**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine
   ```

4. **Set environment variables**
   ```bash
   export FLASK_APP=main.py
   export PYTHONPATH=/path/to/project
   export SECRET_KEY="your-secret-key"
   ```

5. **Start Flask app**
   ```bash
   # Using Makefile (recommended)
   make run
   
   # Or manually
   python -m flask run --host=0.0.0.0 --port=5001
   ```
   
   **Note**: The app runs on port 5001 by default to avoid conflicts with macOS AirPlay (which uses port 5000).

6. **Start Async Data Scheduler (Optional)**
   ```bash
   # Start scheduler via API
   curl -X POST http://localhost:5001/api/scheduler/start
   
   # Check scheduler status
   curl http://localhost:5001/api/scheduler/status
   
   # Manual data refresh
   curl -X POST http://localhost:5001/api/scheduler/refresh \
     -H "Content-Type: application/json" \
     -d '{"index": "S&P 500", "sector": "Technology"}'
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd stocknity-ui
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

## 🛠️ Makefile Commands

The project includes a comprehensive Makefile with useful commands for development and deployment:

### Quick Commands
```bash
make help          # Show all available commands
make setup         # Install dependencies and setup project
make run           # Start the Flask application
make test          # Run tests
make format        # Format code with black
```

### Development Commands
```bash
make install       # Install Python dependencies
make install-dev   # Install development dependencies
make dev-setup     # Setup development environment
make run-dev       # Run in development mode
```

### Code Quality Commands
```bash
make lint          # Lint code with flake8
make type-check    # Type check with mypy
make check         # Run all checks (format, lint, type-check, test)
make test-coverage # Run tests with coverage
```

### Docker Commands
```bash
make docker-build  # Build Docker image
make docker-run    # Run with Docker Compose
make docker-stop   # Stop Docker containers
```

### Kubernetes Commands
```bash
make k8s-deploy    # Deploy to Kubernetes
make k8s-clean     # Clean up Kubernetes resources
make k8s-port-forward  # Start port-forward for development
```

### Utility Commands
```bash
make clean         # Clean up generated files
make deploy        # Deploy to production
```

### Kubernetes Deployment (Recommended)

1. **Start minikube**
   ```bash
   minikube start
   minikube addons enable ingress
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/stock-portfolio-deployment.yaml
   kubectl apply -f k8s/redis-deployment.yaml
   ```

3. **Port-forward for development**
   ```bash
   kubectl port-forward service/stock-portfolio-service 8080:80
   ```

4. **Update UI configuration**
   ```javascript
   // stocknity-ui/src/config/api.ts
   export const API_BASE_URL = 'http://localhost:8080/api';
   ```

## 📊 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/signup` - User registration
- `POST /api/logout` - User logout
- `GET /api/profile` - Get user profile

### Stock Data
- `GET /api/home` - Get news and home page data
- `GET /api/screener` - Get stock screener data
- `POST /api/screener` - Update screener filters

### Portfolio Management
- `GET /api/portfolio/data` - Get current portfolio data
- `POST /api/portfolio` - Build/Optimize/Save portfolios
- `GET /api/my-portfolio/data` - Get user's saved portfolios
- `POST /api/delete-portfolio/<id>` - Delete a portfolio

### Advanced Optimization
- `GET /api/portfolio/optimization-methods` - Get available methods
- `POST /api/portfolio/advanced` - Run advanced optimization
- `POST /api/portfolio/compare-methods` - Compare all methods
- `POST /api/portfolio/backtest` - Run backtesting analysis

### Charts & Analytics
- `GET /api/chart/<type>` - Get chart data (value/growth/dividend)
- `GET /api/health` - Health check endpoint

### AI-Powered Analysis
- `GET /api/ai/sentiment/<ticker>` - Get comprehensive sentiment analysis
- `GET /api/ai/sentiment/<ticker>/trend` - Get sentiment trend over time
- `GET /api/ai/recommendations` - Get AI-powered stock recommendations
- `GET /api/ai/performance` - Get AI model performance metrics

> **📊 Financial Analysis**: For detailed information about financial calculations, metrics, and methodologies, see [Financial Metrics Documentation](docs/FINANCIAL_METRICS.md).
> **🤖 AI Investment System**: For comprehensive AI system design and implementation details, see [AI Investment System Documentation](docs/AI_INVESTMENT_SYSTEM.md).

## 🎯 Usage Guide

### User Authentication
1. **Sign Up**: Create account with email, name, and password
2. **Login**: Use email and password to authenticate
3. **Profile**: Access user dashboard after login

### Basic Portfolio Management
1. **Stock Screening**: Filter stocks by sector, index, and metrics
2. **Build Portfolio**: Select stocks and build portfolio
3. **Save Portfolio**: Save to Redis for later access
4. **View Portfolios**: Access saved portfolios
5. **Delete Portfolio**: Remove portfolios on demand

### Advanced Portfolio Optimization
1. **Navigate to Advanced Portfolio**: Access professional optimization tools
2. **Configure Parameters**:
   - Optimization Method (Markowitz, Risk Parity, Max Sharpe, HRP)
   - Investment Amount (minimum $1,000)
   - Max Stock Price limit
   - Risk Tolerance (Low, Medium, High)
   - Sector and Index selection
3. **Build Portfolio**: Run optimization algorithm
4. **Compare Methods**: See how all 4 algorithms perform
5. **Run Backtesting**: Test strategies on historical data

## 📈 Performance Metrics

### Return Metrics
- **Expected Return**: Annualized expected portfolio return
- **Total Return**: Cumulative return over backtest period
- **Annualized Return**: Yearly return rate

### Risk Metrics
- **Volatility**: Standard deviation of returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **VaR (95%)**: Value at Risk at 95% confidence
- **CVaR (95%)**: Conditional Value at Risk

### Risk-Adjusted Metrics
- **Sharpe Ratio**: Return per unit of risk
- **Calmar Ratio**: Return relative to maximum drawdown
- **Information Ratio**: Excess return vs. tracking error

> **📊 Financial Methodology**: For detailed information about financial calculations, metrics, and methodologies, see [Financial Metrics Documentation](docs/FINANCIAL_METRICS.md).

## 🔧 Configuration

### Environment Variables
```bash
# Backend
FLASK_APP=main.py
PYTHONPATH=/path/to/project
SECRET_KEY=your-secret-key
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Frontend
REACT_APP_API_BASE_URL=http://localhost:8080/api
```

### Scheduler Settings
The scheduler is now fully configurable via environment variables. See [Scheduler Configuration](docs/SCHEDULER_CONFIG.md) for details.

**Default Settings:**
- **Start Delay**: 5 minutes from application start
- **Data Fetch**: Every 24 hours (1440 minutes)
- **Health Checks**: Every hour (60 minutes)
- **Cleanup**: Weekly (7 days)

**Quick Examples:**
```bash
# Development (frequent updates)
export SCHEDULER_START_DELAY_MINUTES=1
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=30

# High-frequency (every 5 minutes)
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=5
export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=5
```

### Async Data Streaming
The screener now supports real-time data streaming from Finviz:
- **Real-time Progress**: See data being fetched stock by stock
- **Partial Updates**: View data as it's processed
- **Fallback Support**: Automatic fallback to Yahoo Finance if Finviz fails
- **Cache Integration**: Uses Redis for fast cached data access

## 🚀 Production Deployment

### Quick Deployment Options

#### 🚀 **Fast Production Deployment (Recommended)**
```bash
# Build and push to registry (one-time or when code changes)
./scripts/build-and-push.sh

# Deploy from registry (fast - no building)
./scripts/deploy.sh --registry
```
**Time: ~30 seconds** (vs 5+ minutes for local build)

#### 🔨 **Local Development Deployment**
```bash
# For development and testing
./scripts/deploy.sh
```
**Time: ~5 minutes** (includes Docker build)

### Development (minikube)
```bash
# Start port-forward
kubectl port-forward service/stock-portfolio-service 8080:80

# UI connects to: http://localhost:8080/api
```

### Production (Cloud Kubernetes)
1. **Deploy to GKE, EKS, or AKS**
2. **Configure ingress with your domain**
3. **Set up SSL certificates**
4. **Update REACT_APP_API_BASE_URL to your domain**

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build -d

# Or build individual images
docker build -t stock-portfolio:latest .
docker run -p 5000:5000 stock-portfolio:latest
```

### Registry Configuration

Edit `scripts/build-and-push.sh` to configure your registry:
```bash
REGISTRY_URL="localhost:5001"  # Local Docker registry
```

**Registry Options:**
- **Local Docker Registry**: `localhost:5001` (port 5001 to avoid conflict with Flask app on 5000)
- **Docker Hub**: `docker.io/yourusername`
- **Google Container Registry**: `gcr.io/your-project`
- **AWS ECR**: `your-account.dkr.ecr.region.amazonaws.com`
- **Azure Container Registry**: `your-registry.azurecr.io`

### Production Workflow

#### **Initial Setup:**
1. Configure your registry in `scripts/build-and-push.sh`
2. Build and push image: `./scripts/build-and-push.sh`

#### **Daily Deployments:**
1. Deploy from registry: `./scripts/deploy.sh --registry`
2. **That's it!** - Takes ~30 seconds

#### **When Code Changes:**
1. Build and push new image: `./scripts/build-and-push.sh`
2. Deploy: `./scripts/deploy.sh --registry`

### Performance Comparison

| Method                | Build Time     | Deploy Time | Total Time |
| --------------------- | -------------- | ----------- | ---------- |
| Local Build           | 5+ minutes     | 30 seconds  | 5+ minutes |
| Registry Pull         | 0 minutes      | 30 seconds  | 30 seconds |
| **Speed Improvement** | **10x faster** |

### Production Optimizations

#### Dockerfile Features
- **Security**: Non-root user, removed build tools after use
- **Size**: Optimized image size
- **Caching**: Optimized layer caching
- **Production-ready**: Proper environment variables

#### Kubernetes Configuration
- **Environment variables**: Production-ready config
- **Secrets**: Secure secret key management
- **Health checks**: Liveness and readiness probes
- **Resource limits**: Memory and CPU constraints

### Accessing the Application

After deployment, the application is available at:
```
http://<minikube-ip>:<nodeport>
```

The script will show you the exact URL.

## 🐛 Troubleshooting

### Common Issues
1. **Redis Connection**: Ensure Redis container is running
2. **Data Fetch Timeouts**: Use cached data or manual fetch
3. **Login Issues**: Check user data in Redis
4. **Missing Data**: Run manual data fetch with `python fetch_data_now.py`

### Deployment Issues

#### Registry Issues
- Ensure you're logged into your registry: `docker login your-registry.com`
- Check image exists: `docker pull your-registry.com/stock-portfolio:latest`

#### Certificate Issues
The script automatically detects and fixes minikube certificate issues by recreating the cluster.

#### Pod Issues
```bash
# Check pod status
kubectl get pods

# Check logs
kubectl logs deployment/stock-portfolio

# Restart deployment
kubectl rollout restart deployment/stock-portfolio
```

### Manual Data Fetch
```bash
# Check cache status
python fetch_data_now.py --status

# Smart fetch (skip existing data)
python fetch_data_now.py

# Force refresh all data
python fetch_data_now.py --force
```

### Redis Commands
```bash
# Check all Redis keys
docker exec -it redis-container redis-cli KEYS "*"

# Check user data
docker exec -it redis-container redis-cli HGETALL users

# Check stock data
docker exec -it redis-container redis-cli GET "stock_data:S&P 500:Technology"
```

## 📁 Project Structure

```
stock-portfolio/
├── main.py                 # Main API routes
├── auth.py                 # Authentication routes
├── app.py                  # Flask app factory
├── scheduler.py            # Data scheduling
├── services/               # Business logic
│   ├── portfolio.py        # Portfolio management
│   ├── advanced_optimization.py  # Professional optimization
│   ├── screener.py         # Stock screening
│   ├── chart.py            # Chart data
│   └── backtesting.py      # Backtesting framework
├── utilities/              # Utility functions
│   ├── redis_data.py       # Redis data manager
│   ├── userFunction.py     # User CRUD operations
│   └── helper.py           # Helper functions
├── k8s/                    # Kubernetes manifests
│   └── stock-portfolio-deployment.yaml
└── requirements.txt        # Python dependencies

stocknity-ui/
├── src/
│   ├── components/         # React components
│   │   ├── Navigation.tsx
│   │   ├── Home.tsx
│   │   ├── Portfolio.tsx
│   │   ├── AdvancedPortfolio.tsx
│   │   └── ...
│   ├── context/            # React context
│   │   └── AuthContext.tsx
│   ├── config/             # Configuration
│   │   └── api.ts
│   └── App.tsx             # Main app component
├── package.json            # Node dependencies
└── tsconfig.json           # TypeScript config
```

## 🧪 Testing

### Backend Testing
```bash
# Test API health
curl http://localhost:5000/api/health

# Test stock data
curl http://localhost:5000/api/screener

# Test authentication
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Frontend Testing
```bash
cd stocknity-ui
npm test
```

## 📚 Documentation

### Technical Documentation
- **[Financial Metrics Documentation](docs/FINANCIAL_METRICS.md)**: Comprehensive guide to financial calculations, methodologies, and industry standards
- **[AI Investment System Documentation](docs/AI_INVESTMENT_SYSTEM.md)**: Advanced AI-powered investment system design and implementation
- **[Async Data System Documentation](docs/ASYNC_DATA_SYSTEM.md)**: Detailed information about the background data processing system
- **[Project Structure Documentation](PROJECT_STRUCTURE.md)**: Overview of the codebase organization

### Educational Resources

#### Portfolio Optimization
- **Modern Portfolio Theory**: Nobel Prize-winning approach by Harry Markowitz
- **Risk Parity**: Bridgewater Associates' flagship strategy
- **Sharpe Ratio**: Industry standard performance measure
- **Hierarchical Clustering**: Machine learning approach for portfolio construction

#### Best Practices
- **Diversification**: Don't put all eggs in one basket
- **Rebalancing**: Regular portfolio maintenance
- **Risk Management**: Set appropriate limits
- **Performance Monitoring**: Track results over time

> **📊 Financial Analysis**: For detailed financial calculations, risk metrics, and investment methodologies, see [Financial Metrics Documentation](docs/FINANCIAL_METRICS.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions and support:
- **Technical Issues**: Check the troubleshooting section and API documentation
- **Financial Calculations**: Review [Financial Metrics Documentation](docs/FINANCIAL_METRICS.md)
- **Data Processing**: See [Async Data System Documentation](docs/ASYNC_DATA_SYSTEM.md)
- **Testing**: Test different parameters to understand their impact
- **Comparison Tools**: Use the comparison tools to make informed decisions

### Important Disclaimers
- **Not Financial Advice**: This application provides analysis tools only
- **Past Performance**: Historical data doesn't guarantee future results
- **Market Risk**: All investments carry inherent market risk
- **Due Diligence**: Users should conduct their own research

---

**Transform your investment strategy with professional-grade portfolio optimization!** 🚀

