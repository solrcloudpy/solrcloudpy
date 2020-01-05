"""
Query and update a Solr collection
"""

import datetime as dt
import json

from future.utils import iterkeys

from solrcloudpy.utils import CollectionBase, SolrException, as_json_bool

# todo this seems funky -- only called once
dthandler = lambda obj: obj.isoformat() if isinstance(obj, dt.datetime) else None


class SolrCollectionSearch(CollectionBase):
    """
    Performs search-related operations on a collection
    """

    def __repr__(self):
        """
        :return: A string representation of the object
        :rtype: str
        """
        return "SolrIndex<%s>" % self.name

    def _get_response(self, path, params=None, method="GET", body=None):
        """
        Retrieves a response from the solr client

        :param path: the URL of the solr endpoint
        :type path: str
        :param params: query params
        :type params: dict
        :param method: the request method
        :type method: str
        :param body: the request body
        :type body: str
        :return: the response
        :rtype: SolrResponse
        """
        return self.client.request(path, params=params, method=method, body=body)

    def _update(self, body, params=None):
        """
        Sends and update request to the solr collection in JSON format
        :param body: the update JSON string
        :type: str
        :return: the response from Solr
        :rtype: SolrResponse
        :raise: SolrException
        """
        path = "%s/update/json" % self.name
        resp = self._get_response(path, method="POST", params=params, body=body)
        if resp.code != 200:
            raise SolrException(resp.result.error)
        return resp

    def search(self, params, method="GET", body=None):
        """
        Search this index

        :param params: query parameters. Here `params` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, a dictionary or a list of tuples
        :type params: SearchOptions
        :type params: dict
        :type params: list
        :param method: the request method
        :type method: str
        :param body: the request body
        :type body: str
        :return: the response from Solr
        :rtype: SolrResponse
        """
        return self._get_response("%s/select" % self.name, params, method, body)

    def clustering(self, params):
        """
        Perform clustering on a query

        :param params: query parameters. Here `params` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, a dictionary or a list of tuples
        :type params: SearchOptions
        :type params: dict
        :type params: list
        :return: the response from Solr
        :rtype: SolrResponse
        """
        return self._get_response("%s/clustering" % self.name, params)

    def mlt(self, params):
        """
        Perform MLT on this index

        :param params: query parameters. Here `params` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, a dictionary or a list of tuples
        :type params: SearchOptions
        :type params: dict
        :type params: list
        :return: the response from Solr
        :rtype: SolrResponse
        """
        return self._get_response("%s/mlt" % self.name, params)

    def add(self, docs, params=None):
        """
        Add a list of document to the collection

        :param docs: a list of documents to add
        :type docs: iterable<dict>
        :return: the response from Solr
        :rtype: SolrResponse
        :raise: SolrException
        """
        return self._update(json.dumps(docs, default=dthandler), params).result

    def delete(self, query, commit=True):
        """
        Delete documents in a collection.

        :param query: query parameters. Here `query` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, or a dictionary
        :type query: SearchOptions
        :type query: dict
        :param commit: whether to commit the change or not
        :type commit: bool
        :return: the response
        :rtype: SolrResponse
        :raise: SolrException
        """
        if "q" not in iterkeys(query):
            raise ValueError("query should have a 'q' parameter")

        if hasattr(query, "commonparams"):
            q = list(query.commonparams["q"])
            q = q[0]
        else:
            q = query["q"]

        m = json.dumps({"delete": {"query": "%s" % q}})

        response = self._update(m)
        if commit:
            self.commit()
        return response

    def optimize(self, wait_searcher=False, soft_commit=False, max_segments=1):
        """
        Optimize a collection for searching

        :param wait_searcher: whether to make the changes to the collection visible or not by opening a new searcher
        :type wait_searcher: bool
        :param soft_commit: whether to perform a soft commit when optimizing
        :type soft_commit: bool
        :param max_segments: the maximum number of segments in the index after optimization
        :type max_segments: int
        :return: the solr response
        :rtype: SolrResponse
        :raise: SolrException
        """
        params = {
            "softCommit": as_json_bool(soft_commit),
            "waitSearcher": as_json_bool(wait_searcher),
            "maxSegments": max_segments,
            "optimize": "true",
        }
        return self._get_response("%s/update" % self.name, params=params).result

    def commit(self):
        """
        Commit changes to a collection

        :return: the solr response
        :rtype: SolrResponse
        :raise: SolrException
        """
        return self._update('{"commit":{}}', {}).result
