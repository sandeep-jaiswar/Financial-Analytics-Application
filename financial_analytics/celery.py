import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_analytics.settings')

app = Celery('financial_analytics')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'daily-historical-ingestion': {
        'task': 'data_ingestion.tasks.ingest_daily_historical',
        'schedule': crontab(hour=18, minute=0),  # 6 PM daily
    },
    'intraday-quote-ingestion': {
        'task': 'data_ingestion.tasks.ingest_intraday_quotes',
        'schedule': crontab(minute='*/15', hour='9-16', day_of_week='mon-fri'),  # Every 15 min, 9 AM - 4 PM, Mon-Fri
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
