import datetime
import pytz
import requests
from mwo.mapdata import controllers, models
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron import CronTrigger

class StatusUpdateView(object):
    _url = 'https://static.mwomercs.com/data/cw/mapdata.json'
#     _epoch = datetime.datetime(3049, 12, 16, 2, 30, tzinfo=pytz.utc)        
    _fmt_archive = "https://static.mwomercs.com/data/cw/mapdata-%Y-%m-%dT%H-%M.json"
    def onMapUpdated(self, timestamp=None):
        if timestamp == None:
            data = self._url
        else:
            timestamp = timestamp.replace(year=timestamp.year + (3049 - 2014))  # TODO: remove this hack
            data = timestamp.strftime(self._fmt_archive)
        data = requests.get(data)
        data.raise_for_status()
        data = data.json()
        controllers.StatusUpdateController().sync(data)

# def test_apscheduler():
#     import logging
#     from apscheduler.schedulers.background import BackgroundScheduler
#     
#     logging.basicConfig()
#     
#     scheduler = BackgroundScheduler()
#     url = 'sqlite:///{}'.format(models.db_file)
#     scheduler.add_jobstore('sqlalchemy', url=url)
#     
#     triggers_kwargs = []
#     
#     
#     job = scheduler.add_job(call, 'cron', (StatusUpdateView(), 'onMapUpdated',),
#                             replace_existing=True,
#                             id='daily_ceasefire',
#                             hour=5,
#                             timezone=pytz.utc,
#                             start_date=datetime.datetime(year=2014, month=12, day=16, hour=2, minute=30, tzinfo=pytz.utc),
#                             end_date=None)
# #     scheduler.start()
#     
#     print get_run_times(job.trigger, datetime.datetime(year=2014, month=12, day=16, hour=5, tzinfo=pytz.utc), datetime.datetime.now(pytz.utc))
#     raise KeyboardInterrupt(raw_input('Enter anything to exit:'))
