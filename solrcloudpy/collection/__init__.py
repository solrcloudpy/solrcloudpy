"""
Manage and search a Solr Collection.

The Collections API is used to enable you to create, remove, or reload collections.
Consult the `Collections API <https://cwiki.apache.org/confluence/display/solr/Collections+API>`_ for more details

    >>> from solrcloudpy.connection import Connection
    >>> conn = Connection()
    >>> coll = conn['test1'].create('test1')
    >>> coll
    Collection<collection1>

This class is also used for query a Solr collection. The endpoints supported by default are:

 - `/select` : the default Solr request handler
 - `/mlt`: the request handler for doing *more like this* search
 - `/clustering`: Solr's clustering component

Support will be coming for the following endpoints:

 - `/get`: Solr's real-time get request handler
 - `/highlight`: Solr's search highlight component
 - `/terms`: Term component


     >>> from solrcloudpy import Connection
     >>> coll = Connection()['collection1']
     >>> response = coll.search({'q':'money'})
     >>> response
     <SolrResponse [200]>
     >>> response.result
     {
         "response": "SolrResponse << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }

"""
from .admin import CollectionAdmin
from .search import CollectionSearch

class Collection(CollectionAdmin,CollectionSearch):
    def create(self, replication_factor=1, force=False, **kwargs):
        admin = super(Collection,self).create(replication_factor,
                                              force, **kwargs)
        return Collection(admin.connection,admin.name)

__all__ = ['Collection']
