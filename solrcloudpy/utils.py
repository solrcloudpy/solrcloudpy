import json
import logging
import random
import uuid

import requests
from future.utils import iteritems
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, HTTPError

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
try:
    str

    def encodeUnicode(value):
        if isinstance(value, str):
            return value.encode("utf-8", "ignore")

        return value
except NameError:

    def encodeUnicode(value):
        return str


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
        if self.connection.auth:
            self.client.auth = self.connection.auth
        elif self.connection.user:
            self.client.auth = HTTPBasicAuth(
                self.connection.user, self.connection.password
            )

    def request(self, path, params=None, method="GET", body=None, asynchronous=False):
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
        :param asynchronous: whether to perform the action asynchronously (only for collections API)
        :type asynchronous: bool

        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        :rtype: SolrResponse
        :raise: SolrException
        """
        headers = {}
        params = params or {}
        if method.lower() != "get":
            headers = {"content-type": "application/json"}

        # https://github.com/solrcloudpy/solrcloudpy/issues/21
        # https://wiki.apache.org/solr/SolJSON
        resparams = {"wt": "json", "omitHeader": "true", "json.nl": "map"}

        if asynchronous:
            async_id = uuid.uuid4()
            logger.info("Sending request with async_id %s" % async_id)
            resparams["async"] = async_id

        if hasattr(params, "iteritems") or hasattr(params, "items"):
            resparams.update(iteritems(params))

        retry_states = dict([(server, 0) for server in self.connection.servers])
        servers = list(retry_states.keys())

        if not servers:
            raise SolrException("No servers available")

        result = None
        r = None
        while result is None:
            host = random.choice(servers)
            fullpath = urljoin(host, path)
            try:
                r = self.client.request(
                    method,
                    fullpath,
                    params=resparams,
                    data=body,
                    headers=headers,
                    timeout=self.timeout,
                )
                r.raise_for_status()

                if asynchronous:
                    result = AsyncResponse(r, async_id)
                else:
                    result = SolrResponse(r)

            except (ConnectionError, HTTPError) as e:
                logger.exception("Failed to connect to server at %s. e=%s", host, e)

                # Track retries, and take a server with too many retries out of the pool
                retry_states[host] += 1
                if retry_states[host] > self.connection.request_retries:
                    del retry_states[host]
                    servers = list(retry_states.keys())

                if len(servers) <= 0:
                    logger.error("No servers left to try")
                    raise SolrException("No servers available")
            finally:
                # avoid requests library's keep alive throw exception in python3
                if r is not None and r.connection:
                    r.connection.close()

        return result

    def update(self, path, params=None, body=None, asynchronous=False):
        """
        Posts an update request to Solr

        :param path: the path to the collection
        :type path: str
        :param params: query params
        :type params: dict
        :param body: the request body, a json string
        :type body: str
        :param asynchronous: whether to perform the action asynchronously (only for collections API)
        :type asynchronous: bool
        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        :rtype: SolrResponse
        :raise: SolrException
        """
        return self.request(
            path, params=params, method="POST", body=body, asynchronous=asynchronous
        )

    def get(self, path, params=None, asynchronous=False):
        """
        Sends a get request to Solr

        :param path: the path to the collection
        :type path: str
        :param params: query params
        :type params: dict
        :param asynchronous: whether to perform the action asynchronously (only for collections API)
        :type asynchronous: bool
        :returns response: an instance of :class:`~solrcloudpy.utils.SolrResponse`
        :rtype: SolrResponse
        :raise: SolrException
        """
        return self.request(
            path, params=params, method="GET", asynchronous=asynchronous
        )


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

        for k, v in iteritems(obj):
            k = encodeUnicode(k).decode("utf-8")
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
        for (k, v) in iteritems(self.__dict__):
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


class AsyncResponse(SolrResponse):
    def __init__(self, response_obj, async_id):
        """
        init this object
        :param response_obj: the `Response` object from the `requests` package
        :type response_obj: requests.Response
        :param async_id: the id we are using to identify the asynchronous interaction
        :type async_id: str
        """
        # try to parse the content of this response as json
        # if that fails, try to save the text
        try:
            result = response_obj.json()
        except ValueError:
            result = {"error": response_obj.text}

        self.result = SolrResult(result)
        self._response_obj = response_obj
        self.async_id = async_id


class SolrResponseJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, SolrResult):
            val = str(o.__dict__)
            if len(val) > 200:
                s = val[:100] + " ... "
            else:
                s = val
            return "%s << %s >>" % (o.__class__.__name__, s)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


class SolrException(Exception):
    pass
