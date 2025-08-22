# Async Data Fetching System

## Overview

The Stocknity application now features a robust, asynchronous data fetching system that replaces the previous synchronous approach with multiple data sources, intelligent caching, and background processing.

## Architecture

### Core Components

1. **DataFetcher** (`services/data_fetcher.py`)
   - Handles multiple data sources with fallbacks
   - Implements rate limiting and error handling
   - Provides both async and sync interfaces

2. **MessageQueue** (`services/message_queue.py`)
   - Redis-based task queue system
   - Supports priority-based task processing
   - Includes retry logic and error handling

3. **AsyncScheduler** (`services/async_scheduler.py`)
   - Manages scheduled data refresh tasks
   - Coordinates background processing
   - Provides manual refresh capabilities

## Key Features

### 🔄 **Multiple Data Sources**
- **Primary**: Finviz Finance API
- **Fallback**: Yahoo Finance API
- **Future**: Alpha Vantage, Polygon.io

### ⚡ **Asynchronous Processing**
- Non-blocking data fetching
- Concurrent worker processes
- Rate limiting to respect API limits

### 🗄️ **Intelligent Caching**
- Redis-based caching with TTL
- Automatic cache invalidation
- Data validation before caching

### 🔄 **Background Processing**
- Message queue for task management
- Priority-based task scheduling
- Automatic retry with exponential backoff

### 📊 **Monitoring & Health Checks**
- Queue statistics monitoring
- Task status tracking
- Health check endpoints

## Usage

### Basic Data Fetching

```python
from services.data_fetcher import fetch_stock_data_sync

# Fetch S&P 500 data
result = fetch_stock_data_sync('S&P 500', 'Technology')
if result.success:
    data = result.data
    print(f"Fetched {len(data)} records from {result.source.value}")
else:
    print(f"Error: {result.error}")
```

### Async Data Fetching

```python
import asyncio
from services.data_fetcher import fetch_stock_data_async

async def fetch_data():
    result = await fetch_stock_data_async('S&P 500', 'Technology')
    return result

# Run async function
result = asyncio.run(fetch_data())
```

### Background Task Processing

```python
from services.message_queue import enqueue_stock_data_fetch, TaskPriority

# Queue a high-priority data fetch task
task_id = enqueue_stock_data_fetch(
    index='S&P 500',
    sector='Technology',
    priority=TaskPriority.HIGH
)
print(f"Task queued with ID: {task_id}")
```

### Scheduler Management

```python
from services.async_scheduler import start_scheduler, stop_scheduler

# Start the scheduler
await start_scheduler()

# Stop the scheduler
await stop_scheduler()
```

## API Endpoints

### Scheduler Management

- `POST /api/scheduler/start` - Start the async scheduler
- `POST /api/scheduler/stop` - Stop the async scheduler
- `GET /api/scheduler/status` - Get scheduler status and queue stats
- `POST /api/scheduler/refresh` - Manually refresh specific data
- `POST /api/scheduler/force-refresh` - Force refresh all data

### Example API Usage

```bash
# Start scheduler
curl -X POST http://localhost:5001/api/scheduler/start

# Get status
curl http://localhost:5001/api/scheduler/status

# Manual refresh
curl -X POST http://localhost:5001/api/scheduler/refresh \
  -H "Content-Type: application/json" \
  -d '{"index": "S&P 500", "sector": "Technology"}'

# Force refresh all data
curl -X POST http://localhost:5001/api/scheduler/force-refresh
```

## Configuration

### Rate Limiting

```python
# Configure rate limiter in DataFetcher
rate_limiter = RateLimiter(calls_per_second=2)  # 2 calls per second
```

### Cache TTL

```python
# Redis cache TTL (in seconds)
CACHE_TTL = 3600  # 1 hour for stock data
ANNUAL_RETURNS_TTL = 86400  # 24 hours for annual returns
```

### Scheduler Configuration

```python
schedule_config = {
    'daily_refresh': '08:00',  # 8 AM daily
    'hourly_check': '00:00',   # Every hour
    'weekly_cleanup': '02:00'  # 2 AM Sunday
}
```

## Error Handling

### Data Source Failures

The system automatically falls back to alternative data sources:

1. Try Finviz Finance API
2. If failed, try Yahoo Finance API
3. If all sources fail, return empty DataFrame with error

### Task Retry Logic

- **Max Retries**: 3 attempts per task
- **Retry Delay**: Exponential backoff
- **Failure Handling**: Move to failed queue after max retries

### Network Timeouts

- **Request Timeout**: 30 seconds per request
- **Connection Pool**: Reusable HTTP sessions
- **Circuit Breaker**: Automatic failure detection

## Monitoring

### Queue Statistics

```python
from services.message_queue import message_queue

stats = message_queue.get_queue_stats()
print(f"Pending: {stats['pending']}")
print(f"Processing: {stats['processing']}")
print(f"Completed: {stats['completed']}")
print(f"Failed: {stats['failed']}")
```

### Task Status Tracking

```python
from services.message_queue import message_queue

task = message_queue.get_task_status(task_id)
print(f"Task {task.id}: {task.status.value}")
print(f"Error: {task.error_message}")
```

## Performance Optimizations

### 1. **Concurrent Processing**
- Multiple worker processes handle tasks concurrently
- Configurable worker count (default: 3)

### 2. **Chunked Processing**
- Large datasets processed in chunks
- Prevents memory overflow
- Respects API rate limits

### 3. **Intelligent Caching**
- Cache hit rate optimization
- Automatic cache warming
- Stale data detection

### 4. **Connection Pooling**
- Reusable HTTP connections
- Reduced connection overhead
- Better resource utilization

## Migration from Old System

### Before (Synchronous)
```python
# Old approach with sleep hacks
from services.sourceDataMapper import SourceDataMapperService

service = SourceDataMapperService()
data = service.get_data_by_index_sector('S&P 500', 'Technology')
# Blocking call with sleep(1) hacks
```

### After (Asynchronous)
```python
# New async approach
from services.data_fetcher import fetch_stock_data_sync

result = fetch_stock_data_sync('S&P 500', 'Technology')
if result.success:
    data = result.data
# Non-blocking with proper rate limiting
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis in minikube
   kubectl get pods | grep redis
   kubectl exec -it <redis-pod> -- redis-cli ping
   ```

2. **Task Queue Full**
   ```bash
   # Check queue stats
   curl http://localhost:5001/api/scheduler/status
   ```

3. **Data Source Errors**
   ```bash
   # Check logs for specific errors
   kubectl logs -f <app-pod>
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features

1. **Additional Data Sources**
   - Alpha Vantage API integration
   - Polygon.io real-time data
   - IEX Cloud API

2. **Advanced Caching**
   - Multi-level caching (Redis + Memory)
   - Cache warming strategies
   - Predictive caching

3. **Enhanced Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alerting system

4. **Scalability Improvements**
   - Horizontal scaling support
   - Load balancing
   - Auto-scaling based on queue depth

## Best Practices

### 1. **Error Handling**
Always check the success flag:
```python
result = fetch_stock_data_sync(index, sector)
if result.success:
    # Process data
else:
    # Handle error
    logger.error(f"Failed to fetch data: {result.error}")
```

### 2. **Resource Management**
Use context managers for async operations:
```python
async with DataFetcher() as fetcher:
    result = await fetcher.fetch_stock_data(index, sector)
```

### 3. **Monitoring**
Regularly check queue health:
```python
stats = message_queue.get_queue_stats()
if stats['failed'] > 10:
    # Alert or take action
```

### 4. **Rate Limiting**
Respect API limits and use appropriate priorities:
```python
# Use URGENT only for critical operations
enqueue_stock_data_fetch(index, sector, TaskPriority.URGENT)
```

This new system provides a robust, scalable foundation for data fetching that eliminates the need for sleep hacks and provides much better reliability and performance.
