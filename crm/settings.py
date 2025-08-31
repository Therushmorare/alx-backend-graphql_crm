# Add 'django_crontab' to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'django_crontab',
    'crm',
    'django_celery_beat',
]

# Define the cron job
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}

