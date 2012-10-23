from connection import ZConnection
import requests
from requests.exceptions import *

class SolrRequest(object):
    def __init__(self,zconnection,collection):
        self.zconnection = zconnection
        self.collection = collection
        self.client = requests.session()

    def _send(self,path,params,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        params['wt'] = 'json'

        servers = list(self.zconnection.servers)
        host = servers.pop(0)

        def make_request(host,path):
            fullpath = "%s/%s" % (host,path)
            try:
                r = self.client.get(fullpath,params=params)
                response = r.json
                if not response:
                    print 'exception:', r, path
                return response
            except ConnectionError:
                host = servers.pop(0)
                return make_request(host,path)
       
        result = make_request(host,path)
        return result
                    
    def search(self,params):
        path = "%s/select" % self.collection
        return self._send(path,params)

    def add(self,params):
        pass

    def delete(self,params):
        pass

    def optimize(self,params):
        pass

    def commit(self,params):
        pass
