from requests.exceptions import *
from requests.models import Response

import requests
import urlparse
import json

class _Request(object):
    """
    Issues requests to the collections API
    """
    def __init__(self,zkconnection):
        self.connection = zkconnection
        self.client = requests.Session()
        
    def request(self,path,params,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        params['wt'] = 'json'

        servers = list(self.connection.servers)
        host = servers.pop(0)
        def make_request(host,path):
            fullpath = urlparse.urljoin(host,path)
            try:
                r = self.client.request(method,fullpath,
                                        params=params,
                                        headers=headers)
                
                return r.json
            except ConnectionError:
                host = servers.pop(0)
                return make_request(host,path)
       
        result = make_request(host,path)
        return result

    def update(self,path,params,body):
        return self.request(path,params,body,method='POST')

    def get(self,path,params):
        return self.request(path,params,method='GET')

class Collection(object):
    """
    Class to manage collections
    """
    def __init__(self,connection):
        self.connection = connection
        self.client = _Request(connection)
        
    def create(self,name,num_shards,params={}):
        params.update({'action':'CREATE','name':name,'numShards':num_shards})
        self.client.get('admin/collections',params)
                             
    def delete(self,name,params={}):
        params.update({'action':'DELETE','name':name})
        self.client.get('admin/collections',params)
        
    def reload(self,name,params={}):
        params.update({'action':'RELOAD','name':name})
        self.client.get('admin/collections',params)

    def __getattr__(self, name):
        import index
        return index.SolrIndex(self.connection,name)

    def __getitem__(self, name):
        import index
        return index.SolrIndex(self.connection,name)

