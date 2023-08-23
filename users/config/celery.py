from __future__ import absolute_import,unicode_literals
import os

from celery import Celery
from django.apps import apps

# set django default settings model
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# creating an instance for celery   
app = Celery('users')

# loading tasks from all registered apps
app.config_from_object('django.conf:settings', namespace='CELERY')

# auto discover task from apps
app.autodiscover_tasks()

# for debugging purposes: know the requests
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))