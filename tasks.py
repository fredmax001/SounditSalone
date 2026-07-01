"""Celery task definitions for Sound It Salone.

When Redis is available, long-running or out-of-band work (emails, notifications)
is sent to a Celery worker. If Redis is unreachable, the same functions are
scheduled via FastAPI BackgroundTasks so the request still returns immediately.
"""
import logging
import os
import sys
from typing import Any, Optional

# Ensure the project root is on sys.path for both the web process and Celery workers.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _ensure_project_root() -> None:
    """Add the project root to sys.path if needed.

    Celery workers may reset sys.path between module import and task execution,
    so task functions call this before importing project modules.
    """
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

from celery import Celery
from fastapi import BackgroundTasks

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL

# Always create the Celery app when a broker is configured; Celery connects
# lazily, so the worker can start before Redis is ready.
celery_app: Optional[Celery] = None
if _broker_url:
    celery_app = Celery(
        "soundit",
        broker=_broker_url,
        backend=settings.CELERY_RESULT_BACKEND or _broker_url,
        include=["tasks"],
    )
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        worker_prefetch_multiplier=1,
    )


def _redis_available() -> bool:
    """Check whether the configured Redis broker is reachable right now."""
    if not _broker_url:
        return False
    try:
        import redis

        client = redis.from_url(_broker_url, socket_connect_timeout=1, socket_timeout=1)
        return client.ping()
    except Exception:
        return False


def dispatch_task(
    task,
    background_tasks: Optional[BackgroundTasks] = None,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Send a task to Celery if available, otherwise schedule it locally."""
    if celery_app is not None and _redis_available():
        try:
            task.delay(*args, **kwargs)
            return
        except Exception as exc:
            logger.warning(f"Celery dispatch failed, falling back to background task: {exc}")

    if background_tasks is not None:
        background_tasks.add_task(task.run, *args, **kwargs)
    else:
        # Last-resort synchronous execution so the operation still happens.
        try:
            task.run(*args, **kwargs)
        except Exception as exc:
            logger.exception(f"Synchronous task fallback failed: {exc}")


# ---------------------------------------------------------------------------
# Email / notification tasks
# ---------------------------------------------------------------------------

if celery_app is not None:
    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def send_welcome_email_task(self, email: str, first_name: str) -> None:
        _ensure_project_root()
        try:
            from email_service import send_welcome_email

            send_welcome_email(email, first_name)
        except Exception as exc:
            logger.warning(f"send_welcome_email failed: {exc}")
            raise self.retry(exc=exc)


    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def send_password_reset_email_task(self, email: str, token: str, first_name: str) -> None:
        _ensure_project_root()
        try:
            from email_service import send_password_reset_email

            send_password_reset_email(email, token, first_name)
        except Exception as exc:
            logger.warning(f"send_password_reset_email failed: {exc}")
            raise self.retry(exc=exc)


    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def send_otp_email_task(self, email: str, code: str, purpose: str = "login") -> None:
        _ensure_project_root()
        try:
            from email_service import send_otp_email

            send_otp_email(email, code, purpose=purpose)
        except Exception as exc:
            logger.warning(f"send_otp_email failed: {exc}")
            raise self.retry(exc=exc)


    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def send_contact_form_email_task(self, to_email: str, subject: str, html_body: str, text_content: Optional[str] = None) -> None:
        _ensure_project_root()
        try:
            from email_service import send_email

            send_email(to_email, subject, html_body, text_content=text_content)
        except Exception as exc:
            logger.warning(f"send_contact_form_email failed: {exc}")
            raise self.retry(exc=exc)


    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def notify_organizer_and_buyer_task(self, order_id: int, ticket_ids: list, buyer_id: int, event_id: int) -> None:
        _ensure_project_root()
        try:
            from api.payments import _notify_organizer_and_buyer_task

            _notify_organizer_and_buyer_task(order_id, ticket_ids, buyer_id, event_id)
        except Exception as exc:
            logger.warning(f"notify_organizer_and_buyer failed: {exc}")
            raise self.retry(exc=exc)


    @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
    def send_broadcast_email_task(self, email: str, subject: str, html_body: str, text_content: str) -> None:
        _ensure_project_root()
        try:
            from email_service import send_email

            send_email(email, subject, html_body, text_content=text_content)
        except Exception as exc:
            logger.warning(f"send_broadcast_email failed: {exc}")
            raise self.retry(exc=exc)

else:
    # No broker configured: define no-op task objects that expose the same
    # .run() interface so dispatch_task can fall back cleanly.
    class _FallbackTask:
        def __init__(self, func):
            self.run = func

    def send_welcome_email_task(email: str, first_name: str) -> None:
        from email_service import send_welcome_email
        send_welcome_email(email, first_name)

    def send_password_reset_email_task(email: str, token: str, first_name: str) -> None:
        from email_service import send_password_reset_email
        send_password_reset_email(email, token, first_name)

    def send_otp_email_task(email: str, code: str, purpose: str = "login") -> None:
        from email_service import send_otp_email
        send_otp_email(email, code, purpose=purpose)

    def send_contact_form_email_task(to_email: str, subject: str, html_body: str, text_content: Optional[str] = None) -> None:
        from email_service import send_email
        send_email(to_email, subject, html_body, text_content=text_content)

    def notify_organizer_and_buyer_task(order_id: int, ticket_ids: list, buyer_id: int, event_id: int) -> None:
        from api.payments import _notify_organizer_and_buyer_task
        _notify_organizer_and_buyer_task(order_id, ticket_ids, buyer_id, event_id)

    def send_broadcast_email_task(email: str, subject: str, html_body: str, text_content: str) -> None:
        from email_service import send_email
        send_email(email, subject, html_body, text_content=text_content)

    send_welcome_email_task = _FallbackTask(send_welcome_email_task)
    send_password_reset_email_task = _FallbackTask(send_password_reset_email_task)
    send_otp_email_task = _FallbackTask(send_otp_email_task)
    send_contact_form_email_task = _FallbackTask(send_contact_form_email_task)
    notify_organizer_and_buyer_task = _FallbackTask(notify_organizer_and_buyer_task)
    send_broadcast_email_task = _FallbackTask(send_broadcast_email_task)
