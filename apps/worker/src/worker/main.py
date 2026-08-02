from celery import Celery

from worker.config import settings

celery_app = Celery(
    "onboard-ai-worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.config_from_object("worker.celeryconfig", silent=True)
celery_app.autodiscover_tasks(["worker"])
