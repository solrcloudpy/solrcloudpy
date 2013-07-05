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
    def __init__(self,connection):
        self.connection = connection
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

    def list(self):
        """
        Lists out the current collections in the cluster
        """
        params = {'wt':'json','detail':'false','path':'/collections'}
        response = self.client.get('/solr/zookeeper',params)
        data = response['tree'][0]['children']
        colls = [node['data']['title'] for node in data]
        return colls

    def _list_cores(self):
        params = {'wt':'json',}
        response = self.client.get('admin/cores',params)
        cores = response.get('status',{}).keys()
        return cores
    
    def exists(self,collection):
        """
        Finds if a collection exists in the cluster
        
        :param collection : the collection to find 
        """
        return collection in self.list()
    
    def create(self,name,num_shards,replication_factor,force=False,params={}):
        """
        Create a collection

        :param name               : a string indicating the name of the collection

        :param num_shards         : an integer indicating the number of shards for this collection

        :param replication_factor : an integer indicating the number of replcas for this collection

        :param force              : a boolean value indicating whether to force the operation or not
                                    The default is `False`

        :param params             : additional parameters to be passed to this operation
        """
        if not self.exists(name) or force == True:
            params.update(
                {
                    'action':'CREATE',
                    'name':name,
                    'numShards':num_shards,
                    'replicationFactor': replication_factor,
                })
            
            self.client.get('admin/collections',params)
        return index.SolrIndex(self.connection,name)

    def delete(self,name,params={}):
        """
        Delete a collection

        :param name   : a string indicating the name of the collection

        :param params : additional parameters to be passed to this operation
        """
        params.update({'action':'DELETE','name':name})
        return self.client.get('admin/collections',params)
        
    def reload(self,name,params={}):
        """
        Reload a collection

        :param name   : a string indicating the name of the collection

        :param params : additional parameters to be passed to this operation
        """

        params.update({'action':'RELOAD','name':name})
        self.client.get('admin/collections',params)

    def __getattr__(self, name):
        return index.SolrIndex(self.connection,name)

    def __getitem__(self, name):
        return index.SolrIndex(self.connection,name)
