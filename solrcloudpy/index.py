from connection import ZConnection, HTTPConnection
from requests.exceptions import *
from requests.models import Response

import requests
import urlparse
import json

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime) else None

class SolrResponse(object):
    def __init__(self,_dict):
        self.dict = _dict
        if not self.dict:
            return

        response = self.dict['response']
        self.hits = int(response['numFound'])
        self.docs = response['docs']

    def __repr__(self):
        if not self.dict:
            return "Empty SolrResponse"
        
        return "SolrResponse(hits=%i)" % (self.hits)
    
class SolrIndex(object):
    def __init__(self,connection,collection):
        self.connection = connection
        self.collection = collection
        self.client = requests.Session()
        
    def _send(self,path,params,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        params['wt'] = 'json'

        servers = list(self.connection.servers)
        host = servers.pop(0)

        def make_request(host,path):
            fullpath = urlparse.urljoin(host,path)
            print fullpath
            try:
                r = self.client.request(method,fullpath,
                                        params=params,
                                        headers=headers)
                
                response = SolrResponse(r.json)
                return response
            except ConnectionError:
                host = servers.pop(0)
                return make_request(host,path)
       
        result = make_request(host,path)
        return result

    def _update(self,body):
        path = '%s/update/json' % self.collection
        return self._send(path,method='POST',params={},body=body)

    def search(self,q,params={}):
        path = "%s/select" % self.collection
        params['q'] = q
        return self._send(path,params)

    def add(self,docs):
        message = json.dumps(docs,default=dthandler)
        response = self._update(message)
        return response

    def delete(self,id=None,q=None):
        if id is None and q is None:
            raise ValueError('You must specify "id" or "q".')
        elif id is not None and q is not None:
            raise ValueError('You many only specify "id" OR "q", not both.')
        elif id is not None:
            m = json.dumps({"delete":{"id":"%s" % id }})
        elif q is not None:
            m = json.dumps({"delete":{"query":"%s" % q }})
            
        response = self._update(m)
        if commit:
            self.commit()
            
    def optimize(self,waitsearcher=True,softcommit=False):
        waitsearcher = str(waitsearcher).lower()
        softcommit = str(softcommit).lower()
        params = {'softCommit': softcommit,
                  'waitSearcher': waitsearcher,
                  'optimize': 'true'
                  }
        path = '%s/update' % self.collection
        response = self._send(path,params)

    def commit(self):
        response = self._update('{"commit":{}}')
