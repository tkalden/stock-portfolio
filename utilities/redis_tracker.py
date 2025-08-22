"""
Redis Data Tracker
Comprehensive tracking system for all data saved to Redis
Prevents duplicate Finviz API calls and provides state management
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd

from utilities.redis_data import redis_manager

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Types of data stored in Redis"""
    STOCK_DATA = "stock_data"
    STRENGTH_DATA = "strength_data"
    ANNUAL_RETURNS = "annual_returns"
    AVERAGE_METRICS = "average_metrics"
    PORTFOLIO = "portfolio"
    USER = "user"
    SUBSCRIPTION = "subscription"

class APISource(Enum):
    """Sources of API calls"""
    FINVIZ = "finviz"
    YAHOO_FINANCE = "yahoo_finance"
    CACHE = "cache"
    CALCULATED = "calculated"

@dataclass
class DataEntry:
    """Represents a data entry in Redis"""
    key: str
    data_type: DataType
    source: APISource
    index: Optional[str] = None
    sector: Optional[str] = None
    stock_type: Optional[str] = None
    user_id: Optional[str] = None
    record_count: int = 0
    size_bytes: int = 0
    created_at: str = None
    last_accessed: str = None
    ttl_seconds: int = 0
    api_calls_made: int = 0
    cache_hits: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_accessed is None:
            self.last_accessed = self.created_at

@dataclass
class APICallLog:
    """Log of API calls made"""
    timestamp: str
    source: APISource
    endpoint: str
    parameters: Dict
    success: bool
    response_time_ms: int
    record_count: int
    cache_key: Optional[str] = None

class RedisTracker:
    """Comprehensive Redis data tracking system"""
    
    def __init__(self):
        self.tracking_key = "redis_tracker:state"
        self.api_log_key = "redis_tracker:api_calls"
        self.pending_requests: Dict[str, datetime] = {}
        self.request_lock = {}
        
    def track_data_save(self, 
                       key: str, 
                       data_type: DataType, 
                       source: APISource,
                       index: Optional[str] = None,
                       sector: Optional[str] = None,
                       stock_type: Optional[str] = None,
                       user_id: Optional[str] = None,
                       record_count: int = 0,
                       size_bytes: int = 0,
                       ttl_seconds: int = 0) -> bool:
        """Track when data is saved to Redis"""
        try:
            entry = DataEntry(
                key=key,
                data_type=data_type,
                source=source,
                index=index,
                sector=sector,
                stock_type=stock_type,
                user_id=user_id,
                record_count=record_count,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds
            )
            
            # Get existing state
            state = self._get_tracking_state()
            
            # Update or add entry - convert enums to strings for JSON serialization
            entry_dict = asdict(entry)
            entry_dict['data_type'] = entry_dict['data_type'].value
            entry_dict['source'] = entry_dict['source'].value
            
            state[key] = entry_dict
            
            # Save updated state
            self._save_tracking_state(state)
            
            logger.info(f"📊 Tracked data save: {key} ({data_type.value}) from {source.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking data save: {e}")
            return False
    
    def track_data_access(self, key: str) -> bool:
        """Track when data is accessed from Redis"""
        try:
            state = self._get_tracking_state()
            
            if key in state:
                state[key]['last_accessed'] = datetime.now().isoformat()
                state[key]['cache_hits'] = state[key].get('cache_hits', 0) + 1
                self._save_tracking_state(state)
                
                logger.debug(f"📊 Tracked data access: {key}")
                return True
            else:
                # If key exists in Redis but not in tracking, create a basic entry
                try:
                    from utilities.redis_data import redis_manager
                    if redis_manager.available and redis_manager.r.exists(key):
                        # Create a basic tracking entry for existing data
                        basic_entry = {
                            'key': key,
                            'data_type': 'stock_data',  # Assume stock data
                            'source': 'unknown',
                            'record_count': 0,
                            'size_bytes': 0,
                            'created_at': datetime.now().isoformat(),
                            'last_accessed': datetime.now().isoformat(),
                            'ttl_seconds': 0,
                            'api_calls_made': 0,
                            'cache_hits': 1
                        }
                        
                        # Extract index and sector from key if possible
                        if key.startswith('stock_data:'):
                            parts = key.split(':')
                            if len(parts) >= 3:
                                basic_entry['index'] = parts[1]
                                basic_entry['sector'] = parts[2]
                        
                        state[key] = basic_entry
                        self._save_tracking_state(state)
                        
                        logger.info(f"📊 Created tracking entry for existing key: {key}")
                        return True
                except Exception as e:
                    logger.debug(f"Could not create tracking entry for {key}: {e}")
                
                logger.debug(f"Attempted to track access for untracked key: {key}")
                return False
                
        except Exception as e:
            logger.error(f"Error tracking data access: {e}")
            return False
    
    def track_api_call(self, 
                      source: APISource,
                      endpoint: str,
                      parameters: Dict,
                      success: bool,
                      response_time_ms: int,
                      record_count: int,
                      cache_key: Optional[str] = None) -> bool:
        """Track API calls made"""
        try:
            log_entry = APICallLog(
                timestamp=datetime.now().isoformat(),
                source=source,
                endpoint=endpoint,
                parameters=parameters,
                success=success,
                response_time_ms=response_time_ms,
                record_count=record_count,
                cache_key=cache_key
            )
            
            # Get existing API logs
            logs = self._get_api_logs()
            
            # Add new log (keep last 1000 entries) - convert enum to string for JSON serialization
            log_dict = asdict(log_entry)
            log_dict['source'] = log_dict['source'].value
            
            logs.append(log_dict)
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Save updated logs
            self._save_api_logs(logs)
            
            # Update tracking state for this cache key
            if cache_key:
                state = self._get_tracking_state()
                if cache_key in state:
                    state[cache_key]['api_calls_made'] = state[cache_key].get('api_calls_made', 0) + 1
                    self._save_tracking_state(state)
            
            logger.info(f"📡 Tracked API call: {source.value} -> {endpoint} ({'✅' if success else '❌'})")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")
            return False
    
    def is_request_pending(self, key: str, timeout_minutes: int = 5) -> bool:
        """Check if a request for this key is already pending"""
        try:
            if key in self.pending_requests:
                request_time = self.pending_requests[key]
                time_since_request = datetime.now() - request_time
                
                if time_since_request.total_seconds() < timeout_minutes * 60:
                    logger.info(f"🔄 Request pending for {key} (started {time_since_request.total_seconds():.1f}s ago)")
                    return True
                else:
                    # Request timed out, remove it
                    del self.pending_requests[key]
                    logger.warning(f"⏰ Request timed out for {key}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking pending request: {e}")
            return False
    
    def add_pending_request(self, key: str) -> bool:
        """Mark a request as pending"""
        try:
            self.pending_requests[key] = datetime.now()
            logger.info(f"🔄 Added pending request for {key}")
            return True
        except Exception as e:
            logger.error(f"Error adding pending request: {e}")
            return False
    
    def remove_pending_request(self, key: str) -> bool:
        """Remove a pending request"""
        try:
            if key in self.pending_requests:
                del self.pending_requests[key]
                logger.info(f"✅ Removed pending request for {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing pending request: {e}")
            return False
    
    def get_tracking_summary(self) -> Dict:
        """Get a summary of all tracked data"""
        try:
            state = self._get_tracking_state()
            
            summary = {
                'total_entries': len(state),
                'data_types': {},
                'sources': {},
                'indexes': {},
                'sectors': {},
                'total_records': 0,
                'total_size_bytes': 0,
                'total_api_calls': 0,
                'total_cache_hits': 0,
                'pending_requests': len(self.pending_requests)
            }
            
            for key, entry in state.items():
                # Count by data type
                data_type = entry.get('data_type', 'unknown')
                summary['data_types'][data_type] = summary['data_types'].get(data_type, 0) + 1
                
                # Count by source
                source = entry.get('source', 'unknown')
                summary['sources'][source] = summary['sources'].get(source, 0) + 1
                
                # Count by index
                index = entry.get('index', 'unknown')
                summary['indexes'][index] = summary['indexes'].get(index, 0) + 1
                
                # Count by sector
                sector = entry.get('sector', 'unknown')
                summary['sectors'][sector] = summary['sectors'].get(sector, 0) + 1
                
                # Sum totals
                summary['total_records'] += entry.get('record_count', 0)
                summary['total_size_bytes'] += entry.get('size_bytes', 0)
                summary['total_api_calls'] += entry.get('api_calls_made', 0)
                summary['total_cache_hits'] += entry.get('cache_hits', 0)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting tracking summary: {e}")
            return {}
    
    def get_cache_status(self) -> Dict:
        """Get detailed cache status"""
        try:
            state = self._get_tracking_state()
            
            cache_status = {
                'stock_data': {},
                'strength_data': {},
                'annual_returns': {},
                'other_data': {}
            }
            
            for key, entry in state.items():
                data_type = entry.get('data_type', 'unknown')
                
                if data_type == DataType.STOCK_DATA.value:
                    index = entry.get('index', 'unknown')
                    sector = entry.get('sector', 'unknown')
                    cache_key = f"{index}:{sector}"
                    
                    if cache_key not in cache_status['stock_data']:
                        cache_status['stock_data'][cache_key] = []
                    
                    cache_status['stock_data'][cache_key].append({
                        'key': key,
                        'records': entry.get('record_count', 0),
                        'size': entry.get('size_bytes', 0),
                        'created': entry.get('created_at', 'unknown'),
                        'last_accessed': entry.get('last_accessed', 'unknown'),
                        'api_calls': entry.get('api_calls_made', 0),
                        'cache_hits': entry.get('cache_hits', 0)
                    })
                
                elif data_type == DataType.STRENGTH_DATA.value:
                    cache_status['strength_data'][key] = entry
                
                elif data_type == DataType.ANNUAL_RETURNS.value:
                    cache_status['annual_returns'][key] = entry
                
                else:
                    cache_status['other_data'][key] = entry
            
            return cache_status
            
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return {}
    
    def get_api_call_history(self, limit: int = 50) -> List[Dict]:
        """Get recent API call history"""
        try:
            logs = self._get_api_logs()
            return logs[-limit:] if logs else []
        except Exception as e:
            logger.error(f"Error getting API call history: {e}")
            return []
    
    def clear_tracking_data(self) -> bool:
        """Clear all tracking data"""
        try:
            if redis_manager.available:
                redis_manager.r.delete(self.tracking_key)
                redis_manager.r.delete(self.api_log_key)
                self.pending_requests.clear()
                logger.info("🧹 Cleared all tracking data")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing tracking data: {e}")
            return False
    
    def _get_tracking_state(self) -> Dict:
        """Get the current tracking state from Redis"""
        try:
            if redis_manager.available:
                data = redis_manager.r.get(self.tracking_key)
                if data:
                    return json.loads(data)
            return {}
        except Exception as e:
            logger.error(f"Error getting tracking state: {e}")
            return {}
    
    def _save_tracking_state(self, state: Dict) -> bool:
        """Save the tracking state to Redis"""
        try:
            if redis_manager.available:
                redis_manager.r.set(self.tracking_key, json.dumps(state))
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving tracking state: {e}")
            return False
    
    def _get_api_logs(self) -> List[Dict]:
        """Get API call logs from Redis"""
        try:
            if redis_manager.available:
                data = redis_manager.r.get(self.api_log_key)
                if data:
                    return json.loads(data)
            return []
        except Exception as e:
            logger.error(f"Error getting API logs: {e}")
            return []
    
    def _save_api_logs(self, logs: List[Dict]) -> bool:
        """Save API call logs to Redis"""
        try:
            if redis_manager.available:
                redis_manager.r.set(self.api_log_key, json.dumps(logs))
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving API logs: {e}")
            return False

# Global tracker instance
redis_tracker = RedisTracker()
