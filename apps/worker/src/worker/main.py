from celery import Celery

celery_app = Celery(
    "onboard-ai-worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.config_from_object("worker.celeryconfig", silent=True)
