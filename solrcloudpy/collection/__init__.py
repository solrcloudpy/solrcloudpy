"""
Manage and search a Solr Collection.

The Collections API is used to enable you to create, remove, or reload collections.
Consult the `Collections API <https://cwiki.apache.org/confluence/display/solr/Collections+API>`_ for more details

    >>> from solrcloudpy.connection import SolrConnection
    >>> conn = SolrConnection()
    >>> coll = conn['test1'].create()
    >>> coll
    SolrCollection<collection1>

This class is also used for query a Solr collection. The endpoints supported by default are:

 - `/select` : the default Solr request handler
 - `/mlt`: the request handler for doing *more like this* search
 - `/clustering`: Solr's clustering component

Support will be coming for the following endpoints:

 - `/get`: Solr's real-time get request handler
 - `/highlight`: Solr's search highlight component
 - `/terms`: Term component


     >>> from solrcloudpy import SolrConnection
     >>> coll = SolrConnection()['collection1']
     >>> response = coll.search({'q': 'money'})
     >>> response
     <SolrResponse [200]>
     >>> response.result
     {
         "response": "SolrResponse << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }

"""
from .admin import SolrCollectionAdmin
from .search import SolrCollectionSearch


class SolrCollection(SolrCollectionAdmin, SolrCollectionSearch):
    def create(self, replication_factor=1, force=False, **kwargs):
        """
        Create a collection

        :param replication_factor: an integer indicating the number of replcas for this collection
        :type replication_factor: int

        :param force: a boolean value indicating whether to force the operation
        :type force: bool

        :param kwargs: additional parameters to be passed to this operation
        

        :Additional Parameters:
          - `router_name`: router name that will be used. defines how documents will be distributed among the shards
          - `num_shards`: number of shards to create for this collection
          - `shards`: A comma separated list of shard names. Required when using the `implicit` router
          - `max_shards_per_node`: max number of shards/replicas to put on a node for this collection
          - `create_node_set`: Allows defining which nodes to spread the new collection across.
          - `collection_config_name`: the name of the configuration to use for this collection
          - `router_field`: if this field is specified, the router will look at the value of the field in an input document to compute the hash and identify of a shard instead of looking at the `uniqueKey` field

        Additional parameters are further documented at https://cwiki.apache.org/confluence/display/solr/Collections+API#CollectionsAPI-CreateaCollection
        """

        admin = super(SolrCollection, self).create(replication_factor, force, **kwargs)
        return SolrCollection(admin.connection, admin.name)

    def __repr__(self):
        return "SolrCollection<%s>" % self.name

__all__ = ['SolrCollection']
