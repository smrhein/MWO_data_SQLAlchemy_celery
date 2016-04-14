from __future__ import absolute_import

from celery import Celery

app = Celery('mwo.mapdata',
             include=['mwo.mapdata.celerytasks'])
app.config_from_object('mwo.mapdata.celeryconfig')

if __name__ == '__main__':
    app.start()
