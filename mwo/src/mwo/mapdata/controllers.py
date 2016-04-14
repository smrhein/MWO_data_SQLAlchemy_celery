import datetime
import bunch
import models
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
import contextlib
import pytz
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
                    
session_factory = sessionmaker(models.engine)
Session = scoped_session(session_factory)

@contextlib.contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close() 

class StatusUpdateController(object):
#     _url = 'https://static.mwomercs.com/data/cw/mapdata.json'
#     _epoch = datetime.datetime(3049, 12, 16, 2, 30).replace(tzinfo=pytz.utc)        
#     _fmt_archive = "https://static.mwomercs.com/data/cw/mapdata-%Y-%m-%dT%H-%M.json"
    _fmt_generated = "%a, %d %b %Y %H:%M:%S"
    
    def sync(self, data):
        dt = datetime.datetime.strptime(data['generated'], self._fmt_generated).replace(tzinfo=pytz.utc)
        logger.debug('{}: {}'.format(StatusUpdateController.sync.__name__, dt))
        
        with session_scope() as session:
            if session.query(models.StatusUpdate).filter_by(datetime_generated=models.datetime2timestamp(dt)).first():
                return
            for id_, planet in data.iteritems():
                if id_ != 'generated':
                    planet = bunch.bunchify(planet)
                    
                    planet_id = {'id':int(id_), 'name':planet.name, 'position_x':int(planet.position.x), 'position_y':int(planet.position.y)}
                    planet_id = models.sync(session, models.Planet, **planet_id)
                    
                    invading_id = {'id':int(planet.invading.id), 'name':planet.invading.name, 'icon':planet.invading.icon}
                    invading_id = models.sync(session, models.Faction, **invading_id)
                    
                    owner_id = {'id':int(planet.owner.id), 'name':planet.owner.name, 'icon':planet.owner.icon}
                    owner_id = models.sync(session, models.Faction, **owner_id)
                    
                    unit_id = {'id':int(planet.unit.id), 'name':planet.unit.name}
                    unit_id = models.sync(session, models.Unit, **unit_id)
                    
                    status = {'contested':bool(int(planet.contested)),
                              'defense_level':int(planet.defense_level),
                              'datetime_generated':models.datetime2timestamp(dt),
                              'invading_id':invading_id.id,
                              'owner_id':owner_id.id,
                              'planet_id':planet_id.id,
                              'unit_id':unit_id.id, }
                    try:
                        status.update({'min_tonnage':int(planet.rules.min_tonnage), 'max_tonnage':int(planet.rules.max_tonnage), 'dropship':int(planet.rules.dropship), 'total_territories':int(planet.total_territories), })
                    except AttributeError:  # legacy format
                        status.update({'min_tonnage':140, 'max_tonnage':240, 'dropship':1, 'total_territories':11, })                                      
                    status = models.sync(session, models.StatusUpdate, **status)
        

def main():
    pass

if __name__ == '__main__':
    main()
