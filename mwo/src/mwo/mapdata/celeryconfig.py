from __future__ import absolute_import

from celery.schedules import crontab
import datetime
import pytz
from .views import StatusUpdateView

db_file = '/home/rhein/git/vims/mwo/src/mwo/mapdata/{}.sqlite'.format(__name__)
BROKER_URL = 'sqla+sqlite:///{}'.format(db_file)
CELERY_RESULT_BACKEND = 'db+sqlite:///{}'.format(db_file)
# CELERY_TASK_RESULT_EXPIRES = 3600
# CELERY_REDIRECT_STDOUTS = True

CELERYBEAT_SCHEDULE = {
    'once_daily_ceasefire': {
        'task': 'mwo.mapdata.celerytasks.call',
        'schedule': crontab(hour=6),
        'args': (StatusUpdateView(), 'onMapUpdated'),
        'options':{'eta':datetime.datetime(2014, 12, 16, 6, 00, tzinfo=pytz.utc),
                   'expires':datetime.datetime(2015, 1, 20, 22, 00, tzinfo=pytz.utc)},
    },
   'thrice_daily_ceasefire': {
        'task': 'mwo.mapdata.celerytasks.call',
        'schedule': crontab(hour=[6, 14, 22]),
        'args': (StatusUpdateView(), 'onMapUpdated'),
        'options':{'eta':datetime.datetime(2015, 1, 20, 22, 00, tzinfo=pytz.utc)},
    },
}

CELERY_TIMEZONE = 'UTC'
