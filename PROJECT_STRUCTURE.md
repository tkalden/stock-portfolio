# Stocknity Project Structure

This document describes the organized structure of the Stocknity project.

## 📁 Directory Structure

```
stock-portfolio/
├── README.md                    # Comprehensive project documentation
├── PROJECT_STRUCTURE.md         # This file - project structure overview
├── setup.py                     # Python package setup
├── requirements.txt             # Python dependencies
├── Makefile                     # Development tasks and shortcuts
├── main.py                      # Main application entry point
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker image definition
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code directory
│   ├── api/                     # API layer
│   │   ├── main.py             # Main API routes
│   │   └── auth.py             # Authentication routes
│   ├── core/                    # Core application
│   │   ├── __init__.py         # Flask app factory
│   │   ├── app.py              # Application entry point
│   │   └── scheduler.py        # Data scheduling
│   └── config/                  # Configuration (future use)
│
├── services/                    # Business logic services
│   ├── portfolio.py            # Portfolio management
│   ├── advanced_optimization.py # Professional optimization algorithms
│   ├── screener.py             # Stock screening
│   ├── chart.py                # Chart data
│   ├── backtesting.py          # Backtesting framework
│   ├── news.py                 # News data
│   ├── annualReturn.py         # Annual return calculations
│   ├── strengthCalculator.py   # Stock strength calculations
│   ├── sourceDataMapper.py     # Data mapping utilities
│   └── optimization.py         # Basic optimization
│
├── utilities/                   # Utility functions
│   ├── redis_data.py           # Redis data manager
│   ├── userFunction.py         # User CRUD operations
│   ├── helper.py               # Helper functions
│   ├── model.py                # Data models
│   ├── redis.py                # Redis connection
│   ├── pickle.py               # Pickle utilities
│   ├── constant.py             # Constants
│   └── bigQuery.py             # BigQuery integration
│
├── finvizfinance/              # FinvizFinance library
│   ├── __init__.py
│   ├── quote.py
│   ├── screener/
│   ├── group/
│   └── ...
│
├── enums/                      # Enumeration definitions
│   └── enum.py
│
├── tests/                      # Test files
│   ├── test_advanced_api.py
│   ├── test_advanced_fix.py
│   ├── test_advanced_optimization.py
│   ├── test_cache_keys.py
│   ├── test_chart_functionality.py
│   ├── test_data_fetch.py
│   ├── test_finviz_detailed.py
│   ├── test_password.py
│   ├── test_yahoo_direct.py
│   └── test_yahoo_finance.py
│
├── scripts/                    # Utility scripts
│   ├── build-and-push.sh       # Docker build and push
│   ├── deploy.sh               # Deployment script
│   ├── dev.sh                  # Development setup
│   ├── registry.sh             # Registry management
│   ├── create_admin_user.py    # Admin user creation
│   ├── fetch_data_now.py       # Manual data fetching
│   ├── manage_yahoo_cache.py   # Yahoo cache management
│   └── debug/                  # Debug scripts
│       ├── debug_login.py
│       ├── debug_yahoo_errors.py
│       └── ...
│
├── k8s/                        # Kubernetes manifests
│   ├── stock-portfolio-deployment.yaml
│   ├── redis-deployment.yaml
│   └── stock-portfolio-secret.yaml
│
├── docs/                       # Documentation
│   ├── ADVANCED_OPTIMIZATION.md
│   └── sequence-diagrams/      # Sequence diagrams
│       ├── fetchChartData.drawio
│       └── newsData.drawio
│
└── stocknity-ui/               # React frontend
    ├── src/
    │   ├── components/         # React components
    │   ├── context/            # React context
    │   ├── config/             # Configuration
    │   └── App.tsx             # Main app component
    ├── package.json            # Node dependencies
    └── tsconfig.json           # TypeScript config
```

## 🏗️ Architecture Overview

### Backend Architecture
- **API Layer** (`src/api/`): REST API endpoints and authentication
- **Core Layer** (`src/core/`): Flask application factory and core functionality
- **Services Layer** (`services/`): Business logic and domain services
- **Utilities Layer** (`utilities/`): Helper functions and data access

### Frontend Architecture
- **Components** (`stocknity-ui/src/components/`): React components
- **Context** (`stocknity-ui/src/context/`): React context for state management
- **Configuration** (`stocknity-ui/src/config/`): API configuration and constants

## 🚀 Development Workflow

### Quick Start
```bash
# Show all available commands
make help

# Install dependencies and setup
make setup

# Run the application
make run

# Run tests
make test

# Format code
make format

# Run all checks
make check
```

### Development Commands
```bash
# Show all available commands
make help

# Setup development environment
make dev-setup

# Run all checks (format, lint, type-check, test)
make check

# Deploy to Kubernetes
make k8s-deploy

# Start port-forward for development
make k8s-port-forward
```

## 📦 Package Organization

### Python Package Structure
- **src/**: Main source code with proper Python package structure
- **setup.py**: Package installation and distribution
- **requirements.txt**: Dependencies management

### Testing Structure
- **tests/**: All test files organized in one location
- **scripts/debug/**: Debug and troubleshooting scripts

### Documentation Structure
- **README.md**: Comprehensive project documentation
- **docs/**: Additional documentation and diagrams
- **PROJECT_STRUCTURE.md**: This file - structure overview

## 🔧 Configuration Files

### Development
- **Makefile**: Common development tasks
- **.gitignore**: Git ignore rules
- **docker-compose.yml**: Local development with Docker

### Production
- **Dockerfile**: Production Docker image
- **k8s/**: Kubernetes deployment manifests
- **scripts/**: Deployment and utility scripts

## 📊 Data Flow

1. **Data Collection**: `scheduler.py` → `services/` → `finvizfinance/`
2. **Data Storage**: `utilities/redis_data.py` → Redis
3. **API Layer**: `src/api/` → `services/` → `utilities/`
4. **Frontend**: `stocknity-ui/` → API endpoints

## 🎯 Benefits of This Structure

- **Clean Separation**: Clear separation of concerns
- **Maintainable**: Easy to find and modify code
- **Scalable**: Structure supports growth
- **Testable**: Organized test structure
- **Deployable**: Clear deployment configuration
- **Documented**: Comprehensive documentation

This structure follows Python best practices and makes the project easy to understand, maintain, and extend.
