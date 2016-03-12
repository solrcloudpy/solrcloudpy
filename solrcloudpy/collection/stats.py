"""
Get different statistics about the underlying index in a collection
"""
from solrcloudpy.utils import _Request, SolrResult


class SolrIndexStats(object):
    """
    Get different statistics about the underlying index in a collection
    """
    def __init__(self, connection, name):
        """
        :param connection: the connection to solr
        :type connection: SolrConnection
        :param name: the name of the index
        :type name: str
        """
        self.connection = connection
        self.name = name
        self.client = _Request(connection)

    @property
    def cache_stats(self):
        """
        Get cache statistics about the index.
        We retrieve cache stats for the document, filter, fiedvalue, fieldcache caches

        :return: The result
        :rtype: SolrResult
        """
        params = {'stats': 'true', 'cat': 'CACHE'}
        result = self.client.get('/solr/%s/admin/mbeans' % self.name, params).result.dict
        caches = result['solr-mbeans']['CACHE']
        res = {}
        for cache, info in caches.iteritems():
            if cache == 'fieldCache':
                res[cache] = {'entries_count': info['stats'].get('entries_count', 0)}
                continue

            res[cache] = info['stats']

        return SolrResult(res)

    @property
    def queryhandler_stats(self):
        """
        Get query handler statistics for all of the handlers used in this Solr node
        
        :return: The result
        :rtype: SolrResult
        """
        params = {'stats': 'true', 'cat': 'QUERYHANDLER'}
        result = self.client.get('/solr/%s/admin/mbeans' % self.name, params).result.dict
        caches = result['solr-mbeans']['QUERYHANDLER']
        res = {}
        for cache, info in caches.iteritems():
            res[cache] = info['stats']

        return SolrResult(res)
