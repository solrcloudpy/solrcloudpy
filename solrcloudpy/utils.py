from requests.exceptions import ConnectionError
import requests
import urlparse
import json

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
        return self.request(path,params,'POST',body)

    def get(self,path,params):
        return self.request(path,params,method='GET')

class DictObject(object):
    '''Recursive class for building and representing objects with'''
    def __init__(self, obj):
        if not obj:
            return

        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, k, DictObject(v))
            else:
                setattr(self, k.encode('utf8','ignore'), v)

    def __getitem__(self, val):
        return self.__dict__[val]

    def __repr__(self):
        value = DictObjectJSONEncoder(indent=4).encode(self.__dict__)
        return value

class DictObjectJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == type(DictObject({})):
            print 'Dictobject'
            val = str(o.__dict__)
            if len(val) > 200:
                s = val[:100] + ' ... '
            else:
                s = val
            return "DictObject << %s >>" % s

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)

class SolrResponse(DictObject):
    """ A generic representation of a solr response """

class SolrException(Exception):
    pass
