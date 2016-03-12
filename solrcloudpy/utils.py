from requests.exceptions import ConnectionError, HTTPError
from requests.auth import HTTPBasicAuth

import requests
import urlparse
import json
import random
import logging
logger = logging.getLogger(__name__)


def as_json_bool(value):
    """
    Casts a value as a json-compatible boolean string
    :param value: the value we want to force to a json-compatible boolean string
    :type value: bool
    :return: json-compatible boolean string
    :rtype: str
    """
    return str(bool(value)).lower()


class _Request(object):

    """
    Issues requests to the collections API
    """

    def __init__(self, connection):
        """
        :param connection: the solr connection
        :type connection: SolrConnection
        """
        self.connection = connection
        self.client = requests.Session()
        self.timeout = connection.timeout
        if self.connection.user:
            self.client.auth = HTTPBasicAuth(
                self.connection.user, self.connection.password)

    def request(self, path, params={}, method='GET', body=None):
        """
        Send a request to a collection

        :param path: The relative path of the request
        :type path: str
        :param params: The parameters of this request. Has to be an objects that implements `iteritems`. Most often this will be an instance :class:`~solrcloudpy.parameter.SearchOptions` or a dictionary
        :type params: SearchOptions
        :type params: dict
        :param method: The request method, e.g. `GET`
        :type method: str
        :param body: The request body, if any -- should be a json string
        :type body: str

        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        :rtype: SolrResponse
        :raise: SolrException
        """
        headers = {}
        if method.lower() != 'get':
            headers = {'content-type': 'application/json'}

        # https://github.com/solrcloudpy/solrcloudpy/issues/21
        # https://wiki.apache.org/solr/SolJSON
        resparams = {'wt': 'json',
                     'omitHeader': 'true',
                     'json.nl': 'map'}

        if hasattr(params, 'iteritems'):
            resparams.update(params.iteritems())

        servers = list(self.connection.servers)
        
        if not servers:
            raise SolrException("No servers available")
        
        random.shuffle(servers)

        result = None
        while len(servers) > 0 and result is None:
            try:
                host = servers.pop(0)
            except IndexError:
                raise SolrException("No servers available")
            fullpath = urlparse.urljoin(host, path)
            try:
                r = self.client.request(method, fullpath,
                                        params=resparams,
                                        data=body,
                                        headers=headers,
                                        timeout=self.timeout)
                r.raise_for_status()

                result = SolrResponse(r)

            except (ConnectionError, HTTPError) as e:
                logger.exception('Failed to connect to server at %s. e=%s',
                                 host, e)

                if len(servers) <= 0:
                    logger.error('No servers left to try')
                    raise SolrException('No servers available')

        return result

    def update(self, path, params={}, body=None):
        """
        Posts an update request to Solr
        
        :param path: the path to the collection
        :type path: str
        :param params: query params
        :type params: dict
        :param body: the request body, a json string
        :type body: str
        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        :rtype: SolrResponse
        :raise: SolrException
        """
        return self.request(path, params, 'POST', body)

    def get(self, path, params={}):
        """
        Sends a get request to Solr

        :param path: the path to the collection
        :type path: str
        :param params: query params
        :type params: dict
        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        :rtype: SolrResponse
        :raise: SolrException
        """
        return self.request(path, params, method='GET')


class CollectionBase(object):

    """
    Base class for operations on collections
    """

    def __init__(self, connection, name):
        """
        :param connection: the solr connection
        :type connection: SolrConnection
        :param name: the name of the collection
        :type name: str
        """
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
        
        :return: a dict
        :rtype: dict
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

        :param response_obj: the `Response` object from the `requests` package
        :type response_obj: requests.Response
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
        """
        Status code of this response
        :return: http status code
        :rtype: int
        """
        return self._response_obj.status_code

    def __repr__(self):
        """
        :rtype: str
        :return: representation in python
        """
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
