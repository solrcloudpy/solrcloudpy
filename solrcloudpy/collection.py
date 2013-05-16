from requests.exceptions import *
from requests.models import Response

from time import time

import requests
import urlparse
import json

import index

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
                                        headers=headers,data=body)
                                
                if r.status_code == requests.codes.ok:
                    response = r.json()
                else:
                    response = r.text
                return response

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

        self.collectionscache = {}
        self.collectionscache['ts'] = time()
        
    def list(self):
        current = time()
        start = self.collectionscache['ts']

        if current - start > 10 or self.collectionscache.get('collections') is None:
            # cache has expired, query zk
            self.connection.zk.start()
            res,node = self.connection.zk.get('/clusterstate.json')
            res = json.loads(res)
            self.connection.zk.stop()
            self.collectionscache['collections'] = res.keys()
            self.collectionscache['ts'] = time()
            return res.keys()

        return self.collectionscache['collections']
        
    def exists(self,collection):
        return collection in self.list()
    
    def create(self,name,num_shards,params={}):
        if not self.exists(name):
            params.update({'action':'CREATE','name':name,'numShards':num_shards})
            self.client.get('admin/collections',params)
        return index.SolrIndex(self.connection,name)

    def delete(self,name,params={}):
        params.update({'action':'DELETE','name':name})
        self.client.get('admin/collections',params)
        
    def reload(self,name,params={}):
        params.update({'action':'RELOAD','name':name})
        self.client.get('admin/collections',params)

    def __getattr__(self, name):
        return index.SolrIndex(self.connection,name)

    def __getitem__(self, name):
        return index.SolrIndex(self.connection,name)
