# Add 'django_crontab' to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps
    'django_crontab',
    'crm',
]

# Define the cron job
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

