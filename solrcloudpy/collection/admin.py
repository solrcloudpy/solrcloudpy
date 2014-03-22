"""
Manage a Solr Collection.

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
     >>> coll.search(**{'q':'money'})
     {
         "response": "SolrResponse << {'start': 0, 'numFound': 0, 'docs': []} >>"
     }

"""
import solrcloudpy.collection.search as search
from solrcloudpy.utils import SolrException, CollectionBase

import time
import json
import requests

class CollectionAdmin(CollectionBase):
    """
    Class to create, remove, reload, split, migrate collections

    """

    def exists(self):
        """
        Finds if a collection exists in the cluster

        :param collection: the collection to find

        """
        return self.name in self.connection.list()

    def create(self, replication_factor=1, force=False, **kwargs):
        """
        Create a collection

        :param num_shards: an integer indicating the number of shards for this collection

        :param replication_factor: an integer indicating the number of replcas for this collection

        :param force: a boolean value indicating whether to force the operation

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
        params = {'name':self.name,
                  'replicationFactor':replication_factor,
                  'action':'CREATE'}
        router_name = kwargs.get("router_name",'compositeId')
        params['router.name'] = router_name

        num_shards = kwargs.get("num_shards","1")
        params['numShards'] = num_shards

        shards = kwargs.get("shards")
        if shards:
            params['shards'] = shards

        max_shards_per_node = kwargs.get('max_shards_per_node',1)
        params['maxShardsPerNode'] = max_shards_per_node

        create_node_set = kwargs.get('create_node_set')
        if create_node_set:
            params['createNodeSet'] = create_node_set

        collection_config_name = kwargs.get('collection_config_name')
        if collection_config_name:
            params['collection.configName'] = collection_config_name

        router_field = kwargs.get('router_field')
        if router_field:
            params['router.field'] = router_field

        # this collection doesn't exist yet, actually create it
        if not self.exists() or force == True:
            res = self.client.get('admin/collections',params).result
            if hasattr(res,'success'):
                # Create the index and wait until it's available
                while True:
                    if not self._is_index_created():
                        print "index not created yet, waiting..."
                        time.sleep(1)
                    else: break

                    return Collection(self.connection,self.name)
            else:
                raise SolrException(str(res))

        # this collection is already present, just return it
        return Collection(self.connection,self.name)

    def _is_index_created(self):
        server = list(self.connection.servers)[0]
        req = requests.get('%s/solr/%s' % (server,self.name))
        if req.status_code != requests.codes.ok:
            return False
        return True

    def is_alias(self):
        """
        Determines if this collection is an alias for a 'real' collection
        """
        params = {'detail':'true','path':'/aliases.json'}
        response = self.client.get('/solr/zookeeper',params).result
        if hasattr(response['znode'],'data'):
            data = json.loads(response['znode']['data'])
        else:
            data = {}
        if not data:
            return False
        collections = data['collection']
        for alias in collections.iterkeys():
            if self.name == alias:
                return True
        return False

    def drop(self):
        """
        Delete a collection
        """
        return self.client.get('admin/collections',{'action':'DELETE','name':self.name}).result

    def reload(self):
        """
        Reload a collection
        """
        return self.client.get('admin/collections',{'action':'RELOAD','name':self.name}).result

    def split_shard(self, shard, ranges=None, split_key=None):
        """
        Split a shard into two new shards

        :param shard: The name of the shard to be split.
        :param ranges: A comma-separated list of hash ranges in hexadecimal e.g. ranges=0-1f4,1f5-3e8,3e9-5dc
        :param split_key: The key to use for splitting the index

        """
        params = {'action':'SPLITSHARD','collection':self.name,'shard':shard}
        if ranges:
            params['ranges'] = ranges
        if split_key:
            params['split.key'] = split_key
        return self.client.get('admin/collections',params).result

    def create_shard(self, shard, create_node_set=None):
        """
        Create a new shard

        :param shard: The name of the shard to be created.

        :param create_node_set: Allows defining the nodes to spread the new collection across.
        """
        params = {'action':'CREATESHARD','collection':self.name,
                  'shard':shard }
        if create_node_set:
            params['create_node_set'] = create_node_set
        return self.client.get('admin/collections',params).result

    def create_alias(self, alias):
        """
        Create or modify an alias for a collection

        :param alias: the name of the alias
        """
        params = {'action':'CREATEALIAS',
                  'name':alias,'collections':self.name}
        return self.client.get('admin/collections',params).result

    def delete_alias(self,alias):
        """
        Delete an alias for a collection

        :param alias: the name of the alias
        """
        params = {'action':'DELETEALIAS','name':alias,}
        return self.client.get('admin/collections',params).result

    def delete_replica(self, replica, shard):
        """
        Delete a replica

        :param replica:  The name of the replica to remove.

        :param shard: The name of the shard that includes the replica to be removed.
        """
        params = {'action':'DELETEREPLICA',
                  'replica':replica,
                  'collection':self.name,
                  'shard':shard}
        return self.client.get('admin/collections',params).result


    @property
    def state(self):
        """Get the state of this collection"""
        if self.is_alias():
            return {"warn":"no state info avilable for aliases"}

        params = {'detail':'true','path':'/clusterstate.json'}
        response = self.client.get('/solr/zookeeper',params).result
        data = json.loads(response['znode']['data'])
        return data[self.name]

    @property
    def shards(self):
        return self.state

    def __repr__(self):
        return "Collection<%s>" % self.name


class Collection(CollectionAdmin,search.CollectionSearch):
    pass
