from celery.schedules import crontab


CELERY_IMPORTS = ('tasks.tasks')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'tasks.tasks.keep_td_access_tokens_alive',
        # Every minute
        'schedule': crontab(minute="*"),
    }
}
