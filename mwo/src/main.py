import requests
import bs4
import gdata.spreadsheets.data
import traceback
import gdata.docs.client
import ConfigParser
import collections
import re
import threading
import time
import twitter
import warnings
import os


def f(o):
    if isinstance(o, collections.Mapping):
        for k, v in o.iteritems():
            o[str(k)] = f(v)
        for k in o.iterkeys():
            if not re.match('^[^\d\W]\w*\Z', k):  # invalid identifier
                return o
        return type('', (object,), o)()
    else:
        return o

def read_config():
    config = ConfigParser.SafeConfigParser()
    config.write(open('mwo_stats.ini', 'w'))
    return config
    
    
def write_config():
    config = ConfigParser.SafeConfigParser()
    
    config.add_section('mwomercs')
    config.set('mwomercs', 'email', 'stephenrhein@gmail.com')
    config.set('mwomercs', 'password', 'mecha')
    
    config.add_section('google')
    config.set('google', 'email', 'stephenrhein@gmail.com')
    config.set('google', 'password', 'Iw5L1!vv4m$7v60n1N+w')
    config.set('google', 'source', 'mwo_stat')
    config.set('google', 'sheet_title', 'mwo_stat')
    
    config.write(open('mwo_stats.ini', 'w'))
    
    
def get_mwo_headers(config):
    with requests.Session() as s:
        data = {'email': config.get('mwomercs', 'email'), 'password': config.get('mwomercs', 'password')}
        r = s.post('https://mwomercs.com/do/login', data=data)
        r.raise_for_status()
        headers = ()    
        types = ['', 'mech', 'weapon', 'map', 'mode']
        for type_ in types:            
            params = {'type':type_}
            r = s.get('https://mwomercs.com/profile/stats', params=params)
            r.raise_for_status()            
            soup = bs4.BeautifulSoup(r.text)
            table = soup.table            
            headers += tuple('{}_{}'.format(type_, th.text.replace(' ', '_')) for th in table('th'))        
        return headers
    
    
def transfer_stats(config):    
    client = gdata.docs.client.DocsClient()
    client.ClientLogin(config.get('google', 'email'), config.get('google', 'password'), config.get('google', 'sheet_title'))
    
    qry = gdata.docs.client.DocsQuery(title=config.get('google', 'sheet_title'), title_exact='true')
    
    feed = client.GetResources(q=qry)
    
    if feed is None:
        document = gdata.docs.data.Resource(type='spreadsheet', title=config.get('google', 'sheet_title'))
        document = client.CreateResource(document)
    elif len(feed.entry) == 1:
        document = feed.entry[0]
    else:
        raise Exception
    
    with requests.Session() as s:
        data = {'email': config.get('mwomercs', 'email'), 'password': config.get('mwomercs', 'password')}
        r = s.post('https://mwomercs.com/do/login', data=data)
        r.raise_for_status()
    
        types = ['', 'mech', 'weapon', 'map', 'mode']
        for type_ in types:            
            params = {'type':type_}
            r = s.get('https://mwomercs.com/profile/stats', params=params)
            r.raise_for_status()
            
            soup = bs4.BeautifulSoup(r.text)
            table = soup.table
            
            headers = tuple('{}_{}'.format(type_, th.text.replace(' ', '_')) for th in table('th'))
            rows = tuple(tuple(str(td.text) for td in tr('td')) for tr in table.tbody('tr'))
                        
            
def main():
    cw()
#     config = read_config()
    
    
if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
    finally:
        pass
