import threading
import time
import ConfigParser
import requests
import twitter
import datetime
import traceback
import collections
import sqlalchemy as sqla
import re
import tokenize
import keyword
import bunch
import pytz
from mwo.mapdata import models

class RecurringTimer(threading._Timer):
    def run(self):
        interval = self.interval
        while not self.finished.wait(self.interval):
            t = time.time()
            self.function(*self.args, **self.kwargs)
            t = time.time() - t
            interval = self.interval - t
            if interval < 0:
                interval = 0

def isname(somestr):
    return re.match(tokenize.Name + '$', somestr)

def isidentifier(somestr):
    return isname(somestr) \
           and not keyword.iskeyword(somestr) \
           and not somestr in dir(__builtins__)
           
# class TerritoryTweeter:
#     _fmt_military_dtg = "%d%H%MZ%b%y"
#     _url = 'https://static.mwomercs.com/data/cw/mapdata.json'
#     _update_interval = 900
#     _epoch = datetime.datetime(3049, 12, 16, 2, 30).replace(tzinfo=pytz.utc)        
#     _fmt_archive = "https://static.mwomercs.com/data/cw/mapdata-%Y-%m-%dT%H-%M.json"
#     _fmt_generated = "%a, %d %b %Y %H:%M:%S"
#     
#     def __init__(self, len_history):
#         self._len_history = len_history        
#         
#         ts = self._get_mapdata(self._url).timestamp        
#         history = 0
#         while (self._len_history >= 0 and history < self._len_history) or \
#               (self._len_history < 0 and not ts < self._epoch):
#             try:
#                 arch_url = ts.strftime(self._fmt_archive)
#                 t = time.time()
#                 data = self._get_mapdata(arch_url)
#                 print time.time() - t
#                 t = time.time()                 
#                 self._add_mapdata(data)
#                 print time.time() - t
#                 print
#                 history += 1
#             except sqla.exc.IntegrityError:
#                 history += 1
#             except requests.exceptions.HTTPError:
#                 pass
#             finally:                           
#                 ts -= datetime.timedelta(seconds=self._update_interval)
#         
#         exit(-1)
#         
#     def _territories2bitfield(self, planet):
#         territories = [int(b) for t in planet['territories'] for b in bin(int(t))[2:].zfill(8)[::-1]]
#         return territories
#     
#     def _planet_compare(self, p1, p2):
#             if p1['_']['P'] > p2['_']['P']:
#                 return p1
#             elif p1['_']['P'] == p2['_']['P']:
#                 if p1['_']['D'] > p2['_']['D']:
#                     return p1
#                 elif p1['_']['D'] == p2['_']['D']:
#                     if p1['_']['I'] > p2['_']['I']:
#                         return p1
#             return p2
#         
#     def _add_mapdata(self, data):
#         with session_scope() as session:
#             if self._len_history >= 0:
#                 for _ in range(session.query(MapData).count() - self._len_history):
#                     old_ts = session.query(func.min(MapData.timestamp))
#                     old_data = session.query(MapData).filter(MapData.timestamp == old_ts).one()
#                     session.delete(old_data)           
#             session.add(data)
#     
#     def _get_mapdata(self, url):
#         resp = requests.get(url)
#         resp.raise_for_status()
#         ts = resp.json()['generated']
#         ts = datetime.datetime.strptime(ts, self._fmt_generated)
#         data = resp.text
#         return MapData(timestamp=ts, data=buffer(data))
#         
#     def notify(self):
#         
#         
#         exit(-1)
#         
#         data = None
#         print data['generated']  
#         
#         for id_, planet in data.iteritems():
#             if id_ == 'generated':
#                 continue
#             if len(self._history) > 0:
#                 assert self._history[-1][id_]['name'] == planet['name']
#             
#             planet['_'] = {}  # for computed value storage
#             P = sum(self._territories2bitfield(planet)) / float(planet['total_territories'])
#             planet['_']['P'] = P
#             if len(self._history) > 0:
#                 planet['_']['I'] = P + self._history[-1][id_]['_']['I']
#                 planet['_']['D'] = P - self._history[-1][id_]['_']['P']
#             else:
#                 planet['_']['I'] = P
#                 planet['_']['D'] = 0.                      
#         self._history.append(data)
#         
#         results = {}
#         for id_, planet in data.iteritems():
#             if id_ == 'generated':
#                 continue            
#             
#             if planet['owner']['name'] == self._config.get('MapData', 'faction') and planet['contested'] == '1':
#                 mx = results.get('losing', planet)
#                 mx = self._planet_compare(mx, planet)
#                 results['losing'] = mx
#         
#             if planet['invading']['name'] == self._config.get('MapData', 'faction') and planet['contested'] == '1':
#                 mx = results.get('taking', planet)
#                 mx = self._planet_compare(mx, planet)
#                 results['taking'] = mx
#                     
#         if .5 < results['losing']['_']['P'] or .5 < results['taking']['_']['P'] < 1.:
#             api = twitter.Api(consumer_key=self._config.get('TwitterApi', 'consumer_key'),
#                       consumer_secret=self._config.get('TwitterApi', 'consumer_secret'),
#                       access_token_key=self._config.get('TwitterApi', 'access_token_key'),
#                       access_token_secret=self._config.get('TwitterApi', 'access_token_secret'))
#              
#             dtg = time.strptime(data['generated'], "%a, %d %b %Y %H:%M:%S")
#             dtg = time.strftime('%d%H%MZ%b%y', dtg)
#             
#             tweet = '{} {} #mwo\n'.format(dtg, self._config.get('MapData', 'faction')).upper()
#             if 5 < results['losing']['captured']:
#                 tweet += 'Losing {}[{}] to {}\n'.format(results['losing']['name'], results['losing']['unit']['name'], results['losing']['invading']['name'])
#             if 5 < results['invading']['captured'] < 11:
#                 tweet += 'Taking {} from {}[{}]\n'.format(results['taking']['name'], results['taking']['owner']['name'], results['taking']['unit']['name'])
#             
# #             api.PostUpdate(tweet)
#             print tweet, len(tweet)
#         print

class ArchiveUpdateObserver(object):
#     _fmt_military_dtg = "%d%H%MZ%b%y"
    
    
    def notify(self):
        dt = requests.get(self._url)
        dt.raise_for_status()
        dt = dt.json()
        dt = dt['generated']
        dt = datetime.datetime.strptime(dt, self._fmt_generated).replace(tzinfo=pytz.utc)
        
        
        

def main():    
#     Base.metadata.drop_all()
    models.Base.metadata.create_all()
    
    data = requests.get(TerritoryTweeter._url)
    data.raise_for_status()
    data = data.json()
    
    ts = datetime.datetime.strptime(data['generated'], TerritoryTweeter._fmt_generated).replace(tzinfo=pytz.utc)
    ts = ts.replace(hour=5, minute=0)
    dt = datetime.timedelta(hours=24)
    
    while not ts < TerritoryTweeter._epoch:
        t = time.time()
        
        data = ts.strftime(TerritoryTweeter._fmt_archive)
        print data
        data = requests.get(data)
        try:
            data.raise_for_status()
            data = data.json()
            
            with session_scope() as session:
                
                if not session.query(session.query(StatusUpdate).filter_by(generated=datetime2timestamp(ts)).exists()):                
                    for id_, planet in data.iteritems():
                        if id_ != 'generated':
                            planet = bunch.bunchify(planet)
                            
                            planet_id = {'id':int(id_), 'name':planet.name, 'position_x':int(planet.position.x), 'position_y':int(planet.position.y)}
                            planet_id = sync(session, Planet, **planet_id)
                            
                            invading_id = {'id':int(planet.invading.id), 'name':planet.invading.name, 'icon':planet.invading.icon}
                            invading_id = sync(session, Faction, **invading_id)
                            
                            owner_id = {'id':int(planet.owner.id), 'name':planet.owner.name, 'icon':planet.owner.icon}
                            owner_id = sync(session, Faction, **owner_id)
                            
                            unit_id = {'id':int(planet.unit.id), 'name':planet.unit.name}
                            unit_id = sync(session, Unit, **unit_id)
                            
                            status = {'contested':bool(int(planet.contested)),
                                      'defense_level':int(planet.defense_level),
                                      'generated':datetime2timestamp(ts),
                                      'invading_id':invading_id.id,
                                      'owner_id':owner_id.id,
                                      'planet_id':planet_id.id,
                                      'unit_id':unit_id.id, }
                            try:
                                status.update({'min_tonnage':int(planet.rules.min_tonnage), 'max_tonnage':int(planet.rules.max_tonnage), 'dropship':int(planet.rules.dropship), 'total_territories':int(planet.total_territories), })
                            except AttributeError:
                                status.update({'min_tonnage':140, 'max_tonnage':240, 'dropship':1, 'total_territories':11, })                                      
                            status = sync(session, StatusUpdate, **status)                        
                        
        except requests.exceptions.HTTPError:
            traceback.print_exc()
                
        print time.time() - t
        ts -= dt
        
    exit(-1)
    
#     class Position(object):
#         def setstate(self, state):
#             self.x = float(state['x'])
#             self.y = float(state['y'])
#             return self
#     class Rules(object):
#         def setstate(self, state):
#             self.max_tonnage = int(state['max_tonnage'])
#             self.dropship = int(state['dropship'])
#             self.min_tonnage = int(state['min_tonnage'])
#             return self
#     class Faction(object):
#         def setstate(self, state):
#             self.id = int(state['id'])
#             self.name = state['name']
#             self.icon = state['icon']
#             return self
#     class Unit(object):
#         def setstate(self, state):
#             self.id = int(state['id'])
#             self.name = state['name']
#             return self
#     class Planet(object):
#         def setstate(self, state):
#             self.contested = bool(state['contested'])
#             self.total_territories = int(state['total_territories'])
#             self.name = state['name']
#             self.rules = Rules().setstate(state['rules'])
#             self.invading = Faction().setstate(state['invading'])
#             self.territories = [int(t) for t in state['territories']]
#             self.defense_level = int(state['defense_level'])
#             self.owner = Faction().setstate(state['owner'])
#             self.position = Position().setstate(state['position'])
#             self.unit = Unit().setstate(state['unit'])
#             return self
#     class Mapdata(object):
#         def setstate(self, state):
#             self.generated = datetime.datetime.strptime(state['generated'], "%a, %d %b %Y %H:%M:%S").replace(tzinfo=pytz.utc)
#             self.planets = {int(k):Planet().setstate(v) for k, v in state.iteritems() if k != 'generated'}
#             return self
                    
    def get_keys(obj, res):
        if isinstance(obj, collections.Mapping):
            res.append(tuple(key.encode('ascii') for key in obj.keys() if isname(key)))
            for v in obj.values():
                get_keys(v, res)
        return res
    
    atts = get_keys(data, [])
    for t in atts:
        print type(t)
    for k in set(atts):
#         print "elif k == '{}':\n\tpass".format(k)
        print k
    
    
#     config = ConfigParser.ConfigParser()
#     fp = open('config.ini')
#     config.readfp(fp)
#     
#     tw = TerritoryTweeter(-1)
#     tw.notify()
# #     pt = RecurringTimer(config.getfloat('MapData', 'interval'), TerritoryTweeter.notify, (tw,))
# #     pt.start()
# #     pt.join()
    
if __name__ == '__main__':
    main()
