from connection import ZConnection
import requests

class SolrRequest(object):
    def __init__(self,zconnection):
        self.servers = zconnection.servers
        self.client = requests

    def _send(self,path,body,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        #params['wt'] = 'json'
                
    def search(self,params)
        pass

    def add(self,params):
        pass

    def delete(self,params):
        pass

    def optimize(self,params):
        pass

    def commit(self,params):
        pass
