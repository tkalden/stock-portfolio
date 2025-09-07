.PHONY: help install test run clean docker-build docker-run k8s-deploy k8s-clean cache-pre-warm

help: ## Show this help message
	@echo "Stocknity - Advanced Stock Portfolio Management System"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	source venv/bin/activate && pip install -r requirements.txt

install-dev: ## Install development dependencies
	source venv/bin/activate && pip install -r requirements.txt
	source venv/bin/activate && pip install pytest pytest-cov black flake8 mypy

test: ## Run tests
	source venv/bin/activate && python -m pytest tests/ -v

test-async: ## Test async data fetching system
	source venv/bin/activate && python tests/test_async_system.py

test-ai: ## Test AI investment system
	source venv/bin/activate && python tests/test_ai_system.py

test-scheduler-config: ## Test scheduler configuration
	source venv/bin/activate && python tests/test_scheduler_config.py

demo-scheduler: ## Demo scheduler with different configurations
	source venv/bin/activate && python tests/demo_scheduler.py

test-coverage: ## Run tests with coverage
	source venv/bin/activate && python -m pytest tests/ --cov=src --cov-report=html

format: ## Format code with black
	source venv/bin/activate && black src/ tests/

lint: ## Lint code with flake8
	source venv/bin/activate && flake8 src/ tests/

type-check: ## Type check with mypy
	source venv/bin/activate && mypy src/

run: ## Run the Flask application
	source venv/bin/activate && python main.py

run-dev: ## Run in development mode
	source venv/bin/activate && FLASK_DEBUG=true python main.py

docker-build: ## Build Docker image
	docker build -t stocknity:latest .

docker-run: ## Run with Docker Compose
	docker-compose up --build -d

docker-stop: ## Stop Docker containers
	docker-compose down

k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f k8s/stock-portfolio-deployment.yaml
	kubectl apply -f k8s/redis-deployment.yaml

k8s-clean: ## Clean up Kubernetes resources
	kubectl delete -f k8s/stock-portfolio-deployment.yaml
	kubectl delete -f k8s/redis-deployment.yaml

k8s-port-forward: ## Start port-forward for development
	kubectl port-forward service/stock-portfolio-service 8080:80

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage

setup: install ## Setup the project
	@echo "Setting up Stocknity..."
	@echo "1. Installing dependencies..."
	@echo "2. Setting up environment..."
	@echo "3. Ready to run!"

dev-setup: install-dev ## Setup development environment
	@echo "Setting up Stocknity development environment..."
	@echo "1. Installing dependencies..."
	@echo "2. Installing development tools..."
	@echo "3. Ready for development!"

check: format lint type-check test ## Run all checks
	@echo "All checks passed!"

deploy: docker-build k8s-deploy ## Deploy to production
	@echo "Deployed to production!"

cache-pre-warm: ## Pre-warm the annual returns cache
	source venv/bin/activate && python scripts/pre_warm_cache.py

cache-status: ## Check cache status
	curl -s https://stock-portfolio-theta.vercel.app/api/cache/annual-returns/status | python -m json.tool