"""
Redis-based Message Queue System
Handles background data processing tasks with retry logic and error handling
"""

import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import redis
from dataclasses import dataclass, asdict
from utilities.redis_data import redis_manager

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class Task:
    id: str
    task_type: str
    data: Dict[str, Any]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for Redis storage"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['priority'] = TaskPriority(data['priority'])
        data['status'] = TaskStatus(data['status'])
        return cls(**data)

class RedisMessageQueue:
    """Redis-based message queue for background tasks"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client or redis_manager.r
        self.queue_name = "stocknity:task_queue"
        self.processing_queue = "stocknity:processing_queue"
        self.completed_queue = "stocknity:completed_queue"
        self.failed_queue = "stocknity:failed_queue"
        self.task_prefix = "stocknity:task:"
        self.workers = {}
        self.running = False
    
    def enqueue_task(self, task_type: str, data: Dict[str, Any], 
                    priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Enqueue a new task"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            task_type=task_type,
            data=data,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store task details
        self.redis.setex(
            f"{self.task_prefix}{task_id}",
            3600,  # 1 hour TTL
            json.dumps(task.to_dict())
        )
        
        # Add to priority queue
        self.redis.zadd(
            self.queue_name,
            {task_id: priority.value}
        )
        
        logger.info(f"Enqueued task {task_id} of type {task_type}")
        return task_id
    
    def dequeue_task(self) -> Optional[Task]:
        """Dequeue the highest priority task"""
        try:
            # Get highest priority task
            result = self.redis.zpopmax(self.queue_name)
            if not result:
                return None
            
            task_id = result[0][0]
            
            # Get task details
            task_data = self.redis.get(f"{self.task_prefix}{task_id}")
            if not task_data:
                return None
            
            task = Task.from_dict(json.loads(task_data))
            task.status = TaskStatus.PROCESSING
            task.updated_at = datetime.now()
            
            # Update task status
            self.redis.setex(
                f"{self.task_prefix}{task_id}",
                3600,
                json.dumps(task.to_dict())
            )
            
            # Add to processing queue
            self.redis.sadd(self.processing_queue, task_id)
            
            return task
            
        except Exception as e:
            logger.error(f"Error dequeuing task: {e}")
            return None
    
    def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed"""
        try:
            task_data = self.redis.get(f"{self.task_prefix}{task_id}")
            if task_data:
                task = Task.from_dict(json.loads(task_data))
                task.status = TaskStatus.COMPLETED
                task.updated_at = datetime.now()
                task.result = result
                
                # Update task
                self.redis.setex(
                    f"{self.task_prefix}{task_id}",
                    3600,
                    json.dumps(task.to_dict())
                )
                
                # Move to completed queue
                self.redis.srem(self.processing_queue, task_id)
                self.redis.sadd(self.completed_queue, task_id)
                
                logger.info(f"Completed task {task_id}")
            
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
    
    def fail_task(self, task_id: str, error_message: str):
        """Mark task as failed"""
        try:
            task_data = self.redis.get(f"{self.task_prefix}{task_id}")
            if task_data:
                task = Task.from_dict(json.loads(task_data))
                task.retry_count += 1
                task.error_message = error_message
                task.updated_at = datetime.now()
                
                if task.retry_count < task.max_retries:
                    # Retry task
                    task.status = TaskStatus.RETRY
                    self.redis.zadd(
                        self.queue_name,
                        {task_id: task.priority.value}
                    )
                    logger.info(f"Retrying task {task_id} (attempt {task.retry_count})")
                else:
                    # Mark as permanently failed
                    task.status = TaskStatus.FAILED
                    self.redis.sadd(self.failed_queue, task_id)
                    logger.error(f"Task {task_id} failed permanently after {task.max_retries} retries")
                
                # Update task
                self.redis.setex(
                    f"{self.task_prefix}{task_id}",
                    3600,
                    json.dumps(task.to_dict())
                )
                
                # Remove from processing queue
                self.redis.srem(self.processing_queue, task_id)
            
        except Exception as e:
            logger.error(f"Error failing task {task_id}: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get task status"""
        try:
            task_data = self.redis.get(f"{self.task_prefix}{task_id}")
            if task_data:
                return Task.from_dict(json.loads(task_data))
            return None
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return None
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        try:
            return {
                'pending': self.redis.zcard(self.queue_name),
                'processing': self.redis.scard(self.processing_queue),
                'completed': self.redis.scard(self.completed_queue),
                'failed': self.redis.scard(self.failed_queue)
            }
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            return {}

class TaskProcessor:
    """Task processor that handles different task types"""
    
    def __init__(self, queue: RedisMessageQueue):
        self.queue = queue
        self.task_handlers = {}
        self.running = False
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type"""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    async def start_processing(self, num_workers: int = 3):
        """Start processing tasks with multiple workers"""
        self.running = True
        logger.info(f"Starting task processor with {num_workers} workers")
        
        # Start worker tasks
        workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(num_workers)
        ]
        
        try:
            await asyncio.gather(*workers)
        except Exception as e:
            logger.error(f"Task processor error: {e}")
        finally:
            self.running = False
            logger.info("Task processor stopped")
    
    async def _worker(self, worker_name: str):
        """Worker task for processing tasks"""
        logger.info(f"Started worker: {worker_name}")
        
        while self.running:
            try:
                # Dequeue task
                task = self.queue.dequeue_task()
                if not task:
                    await asyncio.sleep(1)  # Wait for tasks
                    continue
                
                logger.info(f"{worker_name} processing task {task.id} of type {task.task_type}")
                
                # Get handler for task type
                handler = self.task_handlers.get(task.task_type)
                if not handler:
                    self.queue.fail_task(task.id, f"No handler for task type: {task.task_type}")
                    continue
                
                # Process task
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(task.data)
                    else:
                        result = handler(task.data)
                    
                    self.queue.complete_task(task.id, result)
                    
                except Exception as e:
                    logger.error(f"Error processing task {task.id}: {e}")
                    self.queue.fail_task(task.id, str(e))
                
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop the task processor"""
        self.running = False

# Task handlers
async def fetch_stock_data_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for stock data fetching tasks"""
    from services.data_fetcher import fetch_stock_data_async
    
    index = data.get('index', 'S&P 500')
    sector = data.get('sector', 'Any')
    
    try:
        result = await fetch_stock_data_async(index, sector)
        return {
            'success': result.success,
            'data_count': len(result.data) if not result.data.empty else 0,
            'source': result.source.value,
            'error': result.error
        }
    except Exception as e:
        logger.error(f"Error in fetch_stock_data_handler: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def calculate_annual_returns_handler(data: Dict[str, Any]) -> Dict[str, Any]:
    """Handler for annual returns calculation tasks"""
    from services.annualReturn import AnnualReturn
    
    tickers = data.get('tickers', [])
    
    try:
        annual_return = AnnualReturn()
        result = await annual_return.get_result(tickers)
        return {
            'success': True,
            'data_count': len(result) if not result.empty else 0
        }
    except Exception as e:
        logger.error(f"Error in calculate_annual_returns_handler: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Global instances
message_queue = RedisMessageQueue()
task_processor = TaskProcessor(message_queue)

# Register handlers
task_processor.register_handler('fetch_stock_data', fetch_stock_data_handler)
task_processor.register_handler('calculate_annual_returns', calculate_annual_returns_handler)

def enqueue_stock_data_fetch(index: str, sector: str = 'Any', 
                           priority: TaskPriority = TaskPriority.NORMAL) -> str:
    """Enqueue a stock data fetch task"""
    return message_queue.enqueue_task(
        'fetch_stock_data',
        {'index': index, 'sector': sector},
        priority
    )

def enqueue_annual_returns_calculation(tickers: List[str], 
                                     priority: TaskPriority = TaskPriority.NORMAL) -> str:
    """Enqueue an annual returns calculation task"""
    return message_queue.enqueue_task(
        'calculate_annual_returns',
        {'tickers': tickers},
        priority
    )

async def start_background_processing():
    """Start the background task processing"""
    await task_processor.start_processing(num_workers=3)
