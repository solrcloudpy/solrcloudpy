from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth

import requests
import urlparse
import json
import itertools
import random


class _Request(object):

    """
    Issues requests to the collections API
    """

    def __init__(self, connection):
        self.connection = connection
        self.client = requests.Session()
        self.timeout = connection.timeout
        if self.connection.user:
            self.client.auth = HTTPBasicAuth(self.connection.user, self.connection.password)

    def request(self, path, params, method='GET', body=None):
        """
        Send a request to a collection

        :param path: The relative path of the request
        :param params: the parameters of this request. Has to be an objects that implemetns `iteritems`. Most often this will be an instance :class:`~solrcloudpy.parameter.SearchOptions`
        :param method: Tje request method, e.g. `GET`
        :param body: The request body, if any

        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        """
        headers = {'content-type': 'application/json'}
        extraparams = {'wt': 'json',
                       'omitHeader': 'true',
                       'json.nl': 'map'}

        # pass either a dictionary or a tuple
        if hasattr(params, 'iteritems'):
            params = params.iteritems()

        resparams = dict(itertools.chain(params,
                                    extraparams.iteritems()))

        servers = list(self.connection.servers)
        random.shuffle(servers)
        host = servers.pop(0)

        def make_request(host, path):
            fullpath = urlparse.urljoin(host, path)
            try:
                r = self.client.request(method, fullpath,
                                        params=resparams,
                                        headers=headers, data=body, timeout=self.timeout)

                return SolrResponse(r)

            except ConnectionError as e:
                print 'exception: ', e
                host = servers.pop(0)
                return make_request(host, path)

        result = make_request(host, path)
        return result

    def update(self, path, params, body):
        return self.request(path, params, 'POST', body)

    def get(self, path, params):
        return self.request(path, params, method='GET')


class CollectionBase(object):

    """
    Base class for operations on collections
    """

    def __init__(self, connection, name):
        self.connection = connection
        self.name = name
        self.client = _Request(connection)


class DictObject(object):
    # XXX TODO: make all dict ops work on this object

    def __init__(self, obj):
        if not obj:
            return

        for k, v in obj.iteritems():
            if isinstance(k, unicode):
                k = k.encode('utf8', 'ignore')
            if isinstance(v, dict):
                # create a new object from this (sub)class,
                # not necessarily from DictObject
                setattr(self, k, self.__class__(v))
            else:
                setattr(self, k, v)

    def __getitem__(self, val):
        return self.__dict__[val]


class SolrResult(DictObject):

    """
    Generic representation of a Solr search result. The response is a
    object whose attributes can be also accessed as dictionary keys.

    Example:

         >>> result
         {
         "response": "SolrResponse << {'start': 0, 'numFound': 0, 'docs': []} >>"
         }
         >>> result['response'].start
         0
         >>> result.response.numFound
         0

    """

    def __repr__(self):
        value = SolrResponseJSONEncoder(indent=4).encode(self.__dict__)
        return value

    @property
    def dict(self):
        """
        Convert this result into a python `dict` for easier manipulation
        """
        res = {}
        for (k, v) in self.__dict__.iteritems():
            if isinstance(v, SolrResult):
                res[k] = v.dict
            else:
                res[k] = v
        return res


class SolrResponse(object):

    """
    A generic representation of a solr response. This objects contains both the `Response` object variable from the `requests` package and the parsed content in a :class:`~solrcloudpy.utils.SolrResult` instance.

    """

    def __init__(self, response_obj):
        """
        Init this object.

        :param response_object: the `Response` object from the `requests` package
        """
        # try to parse the content of this response as json
        # if that fails, try to save the text
        result = None
        try:
            result = response_obj.json()
        except ValueError:
            result = {"error": response_obj.text}

        self.result = SolrResult(result)
        self._response_obj = response_obj

    @property
    def code(self):
        """Status code of this response"""
        return self._response_obj.status_code

    def __repr__(self):
        return "<SolrResponse [%s]>" % self.code


class SolrResponseJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if type(o) == type(SolrResult({})):
            val = str(o.__dict__)
            if len(val) > 200:
                s = val[:100] + ' ... '
            else:
                s = val
            return "%s << %s >>" % (o.__class__.__name__, s)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


class SolrException(Exception):
    pass
