"""
Sound It Platform - Monitoring & Error Tracking
===============================================
Production monitoring with:
- Error tracking and alerting
- Performance metrics
- System health checks
- Admin dashboard data
"""

import logging
import json
import time
import traceback
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict

from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database_production import get_db_context, check_database_health
from config_production import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# In-memory metrics store (use Redis in production with multiple workers)
_metrics_store = {
    "requests": defaultdict(list),
    "errors": defaultdict(list),
    "response_times": defaultdict(list),
    "endpoint_calls": defaultdict(int),
}


@dataclass
class ErrorReport:
    """Error report structure"""
    id: str
    timestamp: datetime
    level: str  # error, warning, critical
    message: str
    stack_trace: Optional[str]
    endpoint: Optional[str]
    user_id: Optional[int]
    ip_address: Optional[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "stack_trace": self.stack_trace,
            "endpoint": self.endpoint,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "metadata": self.metadata,
        }


class ErrorTracker:
    """Track and manage application errors"""
    
    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self._errors: List[ErrorReport] = []
    
    def log_error(
        self,
        message: str,
        level: str = "error",
        exception: Optional[Exception] = None,
        request: Optional[Request] = None,
        user_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> ErrorReport:
        """Log an error and return the error report"""
        
        error_id = f"ERR-{int(time.time() * 1000)}-{len(self._errors)}"
        
        stack_trace = None
        if exception:
            stack_trace = traceback.format_exc()
        
        endpoint = None
        ip_address = None
        if request:
            endpoint = str(request.url.path)
            ip_address = request.client.host if request.client else None
        
        error_report = ErrorReport(
            id=error_id,
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            stack_trace=stack_trace,
            endpoint=endpoint,
            user_id=user_id,
            ip_address=ip_address,
            metadata=metadata or {}
        )
        
        # Add to store
        self._errors.append(error_report)
        
        # Trim old errors
        if len(self._errors) > self.max_errors:
            self._errors = self._errors[-self.max_errors:]
        
        # Log to file
        logger.error(f"[{level.upper()}] {message}", extra={
            "error_id": error_id,
            "endpoint": endpoint,
            "user_id": user_id,
        })
        
        # Send webhook alert for critical errors
        if level == "critical":
            self._send_alert(error_report)
        
        return error_report
    
    def _send_alert(self, error: ErrorReport):
        """Send alert for critical errors"""
        if settings.ERROR_WEBHOOK_URL:
            try:
                import requests
                requests.post(
                    settings.ERROR_WEBHOOK_URL,
                    json=error.to_dict(),
                    timeout=5
                )
            except Exception as e:
                logger.error(f"Failed to send error alert: {e}")
    
    def get_recent_errors(
        self,
        hours: int = 24,
        level: Optional[str] = None
    ) -> List[ErrorReport]:
        """Get recent errors"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        errors = [e for e in self._errors if e.timestamp > cutoff]
        
        if level:
            errors = [e for e in errors if e.level == level]
        
        return sorted(errors, key=lambda e: e.timestamp, reverse=True)
    
    def get_error_stats(self, hours: int = 24) -> Dict:
        """Get error statistics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self._errors if e.timestamp > cutoff]
        
        stats = {
            "total": len(recent_errors),
            "by_level": defaultdict(int),
            "by_endpoint": defaultdict(int),
            "trend": []
        }
        
        for error in recent_errors:
            stats["by_level"][error.level] += 1
            if error.endpoint:
                stats["by_endpoint"][error.endpoint] += 1
        
        # Calculate trend (errors per hour)
        for i in range(hours):
            hour_start = cutoff + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            hour_errors = sum(1 for e in recent_errors if hour_start <= e.timestamp < hour_end)
            stats["trend"].append({
                "hour": hour_start.isoformat(),
                "count": hour_errors
            })
        
        return dict(stats)


# Global error tracker instance
error_tracker = ErrorTracker()


def track_errors(func: Callable) -> Callable:
    """Decorator to track errors in a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_tracker.log_error(
                message=str(e),
                exception=e,
                metadata={"function": func.__name__}
            )
            raise
    return wrapper


class PerformanceMonitor:
    """Monitor application performance"""
    
    @staticmethod
    def record_request(endpoint: str, response_time: float, status_code: int):
        """Record request metrics"""
        _metrics_store["endpoint_calls"][endpoint] += 1
        _metrics_store["response_times"][endpoint].append({
            "time": response_time,
            "status": status_code,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 1000 entries per endpoint
        if len(_metrics_store["response_times"][endpoint]) > 1000:
            _metrics_store["response_times"][endpoint] = _metrics_store["response_times"][endpoint][-1000:]
    
    @staticmethod
    def get_performance_stats() -> Dict:
        """Get performance statistics"""
        stats = {
            "endpoints": {},
            "overall": {
                "total_requests": 0,
                "avg_response_time": 0,
                "error_rate": 0
            }
        }
        
        all_times = []
        total_requests = 0
        error_requests = 0
        
        for endpoint, times in _metrics_store["response_times"].items():
            if not times:
                continue
            
            response_times = [t["time"] for t in times]
            status_codes = [t["status"] for t in times]
            
            endpoint_stats = {
                "call_count": _metrics_store["endpoint_calls"].get(endpoint, 0),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)],
                "error_rate": sum(1 for s in status_codes if s >= 400) / len(status_codes)
            }
            
            stats["endpoints"][endpoint] = endpoint_stats
            all_times.extend(response_times)
            total_requests += len(times)
            error_requests += sum(1 for s in status_codes if s >= 400)
        
        if all_times:
            stats["overall"] = {
                "total_requests": total_requests,
                "avg_response_time": sum(all_times) / len(all_times),
                "error_rate": error_requests / total_requests if total_requests > 0 else 0
            }
        
        return stats


class SystemMonitor:
    """Monitor system health and resources"""
    
    @staticmethod
    def get_system_health() -> Dict:
        """Get overall system health"""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Database health
        db_health = check_database_health()
        health["services"]["database"] = db_health
        
        if db_health["status"] != "healthy":
            health["status"] = "degraded"
        
        # Disk space
        try:
            import shutil
            disk = shutil.disk_usage("/")
            health["services"]["disk"] = {
                "status": "healthy",
                "total_gb": disk.total // (2**30),
                "used_gb": disk.used // (2**30),
                "free_gb": disk.free // (2**30),
                "usage_percent": (disk.used / disk.total) * 100
            }
            
            if health["services"]["disk"]["usage_percent"] > 90:
                health["services"]["disk"]["status"] = "critical"
                health["status"] = "degraded"
            elif health["services"]["disk"]["usage_percent"] > 80:
                health["services"]["disk"]["status"] = "warning"
        
        except Exception as e:
            health["services"]["disk"] = {"status": "unknown", "error": str(e)}
        
        # Memory usage
        try:
            import psutil
            memory = psutil.virtual_memory()
            health["services"]["memory"] = {
                "status": "healthy",
                "total_gb": memory.total // (2**30),
                "available_gb": memory.available // (2**30),
                "usage_percent": memory.percent
            }
            
            if memory.percent > 90:
                health["services"]["memory"]["status"] = "critical"
                health["status"] = "degraded"
            elif memory.percent > 80:
                health["services"]["memory"]["status"] = "warning"
        
        except ImportError:
            health["services"]["memory"] = {"status": "unknown", "note": "psutil not installed"}
        
        return health


class AdminDashboard:
    """Generate data for admin dashboard"""
    
    @staticmethod
    def get_realtime_stats(db: Session) -> Dict:
        """Get real-time platform statistics"""
        from models import (
            User, UserRole, UserStatus, Event, Order, 
            PaymentStatus, Ticket, BookingRequest, BookingStatus
        )
        
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # User stats
        user_stats = {
            "total": db.query(User).count(),
            "active": db.query(User).filter(User.status == UserStatus.ACTIVE).count(),
            "new_24h": db.query(User).filter(User.created_at >= last_24h).count(),
            "new_7d": db.query(User).filter(User.created_at >= last_7d).count(),
            "by_role": {
                role.value: db.query(User).filter(User.role == role).count()
                for role in UserRole
            }
        }
        
        # Revenue stats
        revenue_stats = {
            "total_revenue": db.query(func.sum(Order.total_amount)).filter(
                Order.payment_status == PaymentStatus.COMPLETED
            ).scalar() or 0,
            "revenue_24h": db.query(func.sum(Order.total_amount)).filter(
                Order.payment_status == PaymentStatus.COMPLETED,
                Order.paid_at >= last_24h
            ).scalar() or 0,
            "revenue_7d": db.query(func.sum(Order.total_amount)).filter(
                Order.payment_status == PaymentStatus.COMPLETED,
                Order.paid_at >= last_7d
            ).scalar() or 0,
            "pending_orders": db.query(Order).filter(
                Order.payment_status == PaymentStatus.PENDING
            ).count(),
        }
        
        # Event stats
        event_stats = {
            "total": db.query(Event).count(),
            "upcoming": db.query(Event).filter(Event.start_date >= now).count(),
            "ongoing": db.query(Event).filter(
                Event.start_date <= now,
                Event.end_date >= now
            ).count(),
            "tickets_sold": db.query(func.sum(Event.tickets_sold)).scalar() or 0,
        }
        
        # Ticket stats
        ticket_stats = {
            "total": db.query(Ticket).count(),
            "used": db.query(Ticket).filter(Ticket.is_used == True).count(),
            "scanned_24h": db.query(Ticket).filter(
                Ticket.is_used == True,
                Ticket.used_at >= last_24h
            ).count(),
        }
        
        # Booking stats
        booking_stats = {
            "total": db.query(BookingRequest).count(),
            "pending": db.query(BookingRequest).filter(
                BookingRequest.status == BookingStatus.PENDING
            ).count(),
            "accepted": db.query(BookingRequest).filter(
                BookingRequest.status == BookingStatus.ACCEPTED
            ).count(),
        }
        
        return {
            "users": user_stats,
            "revenue": revenue_stats,
            "events": event_stats,
            "tickets": ticket_stats,
            "bookings": booking_stats,
            "timestamp": now.isoformat()
        }
    
    @staticmethod
    def get_recent_activities(db: Session, limit: int = 20) -> List[Dict]:
        """Get recent platform activities"""
        from models import User, Order, Event, BookingRequest
        
        activities = []
        
        # Recent user registrations
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
        for user in recent_users:
            activities.append({
                "type": "user_registration",
                "timestamp": user.created_at.isoformat() if user.created_at else None,
                "description": f"New user registered: {user.email or user.phone}",
                "user_id": user.id,
                "metadata": {"role": user.role.value if user.role else None}
            })
        
        # Recent orders
        recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(limit).all()
        for order in recent_orders:
            activities.append({
                "type": "order",
                "timestamp": order.created_at.isoformat() if order.created_at else None,
                "description": f"Order {order.order_number} - {order.payment_status.value}",
                "user_id": order.user_id,
                "amount": order.total_amount,
                "metadata": {"status": order.payment_status.value}
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
        return activities[:limit]
    
    @staticmethod
    def get_pending_actions(db: Session) -> List[Dict]:
        """Get pending admin actions"""
        from models import Event, EventStatus, BookingRequest, BookingStatus, VerificationRequest, VerificationStatus
        
        actions = []
        
        # Pending event approvals
        pending_events = db.query(Event).filter(Event.status == EventStatus.PENDING).all()
        for event in pending_events:
            actions.append({
                "id": f"event_{event.id}",
                "type": "event_approval",
                "title": f"Event Approval: {event.title}",
                "description": f"Event '{event.title}' is pending approval",
                "created_at": event.created_at.isoformat() if event.created_at else None,
                "entity_id": event.id,
                "entity_type": "event",
                "priority": "medium"
            })
        
        # Pending booking requests
        pending_bookings = db.query(BookingRequest).filter(
            BookingRequest.status == BookingStatus.PENDING
        ).all()
        for booking in pending_bookings:
            actions.append({
                "id": f"booking_{booking.id}",
                "type": "booking_review",
                "title": f"Booking Request #{booking.id}",
                "description": f"New booking request from user #{booking.requester_id}",
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
                "entity_id": booking.id,
                "entity_type": "booking",
                "priority": "high" if booking.budget and booking.budget > 10000 else "medium"
            })
        
        # Pending verifications
        pending_verifications = db.query(VerificationRequest).filter(
            VerificationRequest.status == VerificationStatus.PENDING
        ).all()
        for verification in pending_verifications:
            actions.append({
                "id": f"verification_{verification.id}",
                "type": "verification_review",
                "title": f"Verification Request: {verification.request_type.value}",
                "description": f"User #{verification.user_id} requested {verification.request_type.value} verification",
                "created_at": verification.submitted_at.isoformat() if verification.submitted_at else None,
                "entity_id": verification.id,
                "entity_type": "verification",
                "priority": "low"
            })
        
        # Sort by priority and date
        priority_order = {"high": 0, "medium": 1, "low": 2}
        actions.sort(key=lambda x: (priority_order.get(x["priority"], 3), x["created_at"]), reverse=False)
        
        return actions


def get_monitoring_summary() -> Dict:
    """Get complete monitoring summary for admin dashboard"""
    with get_db_context() as db:
        return {
            "system": SystemMonitor.get_system_health(),
            "performance": PerformanceMonitor.get_performance_stats(),
            "errors": error_tracker.get_error_stats(hours=24),
            "platform": AdminDashboard.get_realtime_stats(db),
            "recent_activities": AdminDashboard.get_recent_activities(db, limit=20),
            "pending_actions": AdminDashboard.get_pending_actions(db),
        }
