from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth

import requests
import urlparse
import json
import itertools

class _Request(object):
    """
    Issues requests to the collections API
    """
    def __init__(self,connection):
        self.connection = connection
        self.client = requests.Session()
        if self.connection.user:
            self.client.auth = HTTPBasicAuth(self.connection.user,self.connection.password)

    def request(self,path,params,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        extraparams = {'wt':'json',
                       'omitHeader':'true',
                       'json.nl':'map'}

        resparams = itertools.chain(params.iteritems(),
                                    extraparams.iteritems())

        servers = list(self.connection.servers)
        host = servers.pop(0)

        def make_request(host,path):
            fullpath = urlparse.urljoin(host,path)
            try:
                r = self.client.request(method,fullpath,
                                        params=resparams,
                                        headers=headers,data=body,timeout=10.0)

                if r.status_code == requests.codes.ok:
                    response = r.json()
                else:
                    response = r.text
                return response

            except ConnectionError as e:
                print 'exception: ', e
                host = servers.pop(0)
                return make_request(host,path)

        result = make_request(host,path)
        return result

    def update(self,path,params,body):
        return self.request(path,params,'POST',body)

    def get(self,path,params):
        return self.request(path,params,method='GET')

class DictObject(object):
    def __init__(self, obj):
        if not obj:
            return

        for k, v in obj.iteritems():
            if isinstance(v, dict):
                # create a new object from this (sub)class,
                # not necessarily from DictObject
                setattr(self, k, self.__class__(v))
            else:
                setattr(self, k.encode('utf8','ignore'), v)

    def __getitem__(self, val):
        return self.__dict__[val]


class SolrResponseJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == type(SolrResponse({})):
            val = str(o.__dict__)
            if len(val) > 200:
                s = val[:100] + ' ... '
            else:
                s = val
            return "%s << %s >>" % (o.__class__.__name__,s)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)

class SolrResponse(DictObject):
    """ A generic representation of a solr response """
    def __repr__(self):
        value = SolrResponseJSONEncoder(indent=4).encode(self.__dict__)
        return value

class SolrException(Exception):
    pass
