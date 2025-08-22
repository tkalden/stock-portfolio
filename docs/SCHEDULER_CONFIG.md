# Scheduler Configuration

The async scheduler can be configured using environment variables to control when and how often data is fetched from Finviz.

## Environment Variables

### Core Settings

| Variable                                  | Default | Description                                          |
| ----------------------------------------- | ------- | ---------------------------------------------------- |
| `SCHEDULER_START_DELAY_MINUTES`           | `5`     | Minutes to wait before starting the first data fetch |
| `SCHEDULER_DATA_FETCH_INTERVAL_MINUTES`   | `1440`  | How often to fetch fresh data (in minutes)           |
| `SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES` | `60`    | How often to run health checks (in minutes)          |
| `SCHEDULER_CLEANUP_INTERVAL_DAYS`         | `7`     | How often to clean old data (in days)                |

### Time Settings (for daily/weekly schedules)

| Variable                   | Default | Description                   |
| -------------------------- | ------- | ----------------------------- |
| `SCHEDULER_DAILY_REFRESH`  | `08:00` | Time for daily data refresh   |
| `SCHEDULER_HOURLY_CHECK`   | `00:00` | Time for hourly health checks |
| `SCHEDULER_WEEKLY_CLEANUP` | `02:00` | Time for weekly cleanup       |

## Example Configurations

### Development/Testing (Frequent Updates)
```bash
export SCHEDULER_START_DELAY_MINUTES=1
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=30
export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=15
```

### Production (Standard Daily Updates)
```bash
export SCHEDULER_START_DELAY_MINUTES=5
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=1440
export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=60
```

### High-Frequency Trading (Every 5 Minutes)
```bash
export SCHEDULER_START_DELAY_MINUTES=1
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=5
export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=5
```

### Real-Time Monitoring (Every Minute)
```bash
export SCHEDULER_START_DELAY_MINUTES=1
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=1
export SCHEDULER_HEALTH_CHECK_INTERVAL_MINUTES=1
```

## How It Works

1. **Start Delay**: The scheduler waits this many minutes before running the first data fetch
2. **Data Fetch Interval**: 
   - If < 1440 minutes: Runs every N minutes
   - If >= 1440 minutes: Runs daily at the specified time
3. **Health Check Interval**:
   - If < 60 minutes: Runs every N minutes
   - If >= 60 minutes: Runs every hour
4. **Cleanup Interval**:
   - If 1 day: Runs daily
   - If > 1 day: Runs weekly

## Usage

Set the environment variables before starting the application:

```bash
# For development
export SCHEDULER_START_DELAY_MINUTES=1
export SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=30
python main.py

# Or create a .env file
echo "SCHEDULER_START_DELAY_MINUTES=1" > .env
echo "SCHEDULER_DATA_FETCH_INTERVAL_MINUTES=30" >> .env
python main.py
```

## Monitoring

The scheduler logs its configuration and activities:

```
INFO: Scheduler configuration: {'daily_refresh': '08:00', 'hourly_check': '00:00', ...}
INFO: Scheduled tasks configured with start delay: 5 minutes
INFO: Data fetch interval: 1440 minutes
INFO: Health check interval: 60 minutes
INFO: Cleanup interval: 7 days
```
