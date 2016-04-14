from __future__ import absolute_import

from apscheduler.triggers.cron import CronTrigger
import pytz
import datetime
from celery.signals import beat_init
from celery import signature
from .celeryapp import app
from .celeryconfig import CELERYBEAT_SCHEDULE
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

@app.task
def call(obj, name, *args, **kwargs):
    return getattr(obj, name).__call__(*args, **kwargs)

@beat_init.connect
def beat_init_handler(sender=None, **kwargs):
    
#     def get_run_times(trigger, first_run_time, end_time):
#         if end_time == None:
#             end_time = datetime.datetime.now(pytz.utc)
#         run_times = []
#         while first_run_time and first_run_time <= end_time:
#             run_times.append(first_run_time)
#             first_run_time = trigger.get_next_fire_time(first_run_time, first_run_time)
#         return run_times
    
    for v in CELERYBEAT_SCHEDULE.itervalues():
        trigger = CronTrigger(hour=','.join(str(h) for h in v['schedule'].hour),
                          start_date=v['options']['eta'],
                          end_date=v['options'].get('expires', None),
                          timezone=pytz.utc)
        next_fire_time = trigger.start_date
        while next_fire_time and next_fire_time <= (trigger.end_date if trigger.end_date else datetime.datetime.now(pytz.utc)):
            task = signature(v['task'], v.get('args', ()) + (next_fire_time,), v.get('kwargs', {}), v.get('options', {}), app)
            try:
                task()
            except Exception as e:
                logger.exception(e)
            next_fire_time = trigger.get_next_fire_time(next_fire_time, next_fire_time)
                
        
