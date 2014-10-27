"""
Query and update a Solr collection
"""

from solrcloudpy.utils import CollectionBase, SolrException

import datetime as dt
import json

dthandler = lambda obj: obj.isoformat() if isinstance(obj, dt.datetime) else None


class SolrCollectionSearch(CollectionBase):

    """
    Performs search-related operations on a collection
    """

    def __repr__(self):
        return "SolrIndex<%s>" % self.name

    def _get_response(self, path, params, method='GET', body=None):
        return self.client.request(path, params, method=method, body=body)

    def _update(self, body):
        path = '%s/update/json' % self.name
        resp = self._get_response(path, method='POST', params={}, body=body)
        if resp.code != 200:
            raise SolrException(resp.result.error)
        return resp

    def search(self, params):
        """
        Search this index

        :param params: query parameters. Here `params` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, a dictionary or a list of tuples

        """
        path = "%s/select" % self.name
        data = self._get_response(path, params)
        return data

    def clustering(self, params):
        """
        Perform clustering on a query

        :param params: query parameters. Here `params` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, a dictionary or a list of tuples

        """
        path = "%s/clustering" % self.name
        data = self._get_response(path, params)
        return data

    def mlt(self, params):
        """
        Perform MLT on this index

        :param params: query parameters. Here `params` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, a dictionary or a list of tuples
        """
        path = "%s/mlt" % self.name
        data = self._get_response(path, params)
        return data

    def add(self, docs):
        """
        Add a list of document to the collection

        :param docs: a list of documents to add
        """
        message = json.dumps(docs, default=dthandler)
        response = self._update(message).result
        return response

    def delete(self, query, commit=True):
        """
        Delete documents in a collection.

        :param query: query parameters. Here `query` can be a :class:`~solrcloudpy.parameters.SearchOptions` instance, or a dictionary


        :param commit: whether to commit the change or not
        """
        if 'q' not in query.iterkeys():
            raise ValueError("query should have a 'q' parameter")

        q = None
        if hasattr(query, 'commonparams'):
            q = list(query.commonparams['q'])
            q = q[0]
        else:
            q = query['q']

        m = json.dumps({"delete": {"query": "%s" % q}})

        self._update(m)
        if commit:
            self.commit()

    def optimize(self, wait_searcher=False, soft_commit=False, max_segments=1):
        """
        Optimize a collection for searching

        :param waitsearcher: whether to make the changes to the collection visible or not
                          by opening a new searcher

        :param softcommit: whether to perform a soft commit when optimizing
        """
        waitsearcher = str(wait_searcher).lower()
        softcommit = str(soft_commit).lower()
        params = {'softCommit': softcommit,
                  'waitSearcher': waitsearcher,
                  'maxSegments': max_segments,
                  'optimize': 'true'
                  }
        path = '%s/update' % self.name
        res = self._get_response(path, params=params).result
        return res

    def commit(self):
        """ Commit changes to a collection """
        response = self._update('{"commit":{}}').result
        return response
