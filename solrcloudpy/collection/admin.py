"""
Manage and administer a collection
"""
from solrcloudpy.utils import SolrException, CollectionBase
from .stats import SolrIndexStats
from .schema import SolrSchema

import time
import json
import requests
import logging


class SolrCollectionAdmin(CollectionBase):
    """
    Manage and administer a collection
    """
    def __init__(self, connection, name):
        """
        :param connection: the connection to Solr
        :type connection: SolrConnection
        :param name: the name of the collection
        :type name: str
        """
        super(SolrCollectionAdmin, self).__init__(connection, name)
        
        # corresponding public methods are memoized for a lower memory footprint
        self._index_stats = None
        self._schema = None
        
    def exists(self):
        """
        Finds if a collection exists in the cluster
        :return: whether a collection exists in the cluster
        :rtype: bool
        """
        return self.name in self.connection.list()

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
        params = {'name': self.name,
                  'replicationFactor': replication_factor,
                  'action': 'CREATE'}
        router_name = kwargs.get("router_name", 'compositeId')
        params['router.name'] = router_name

        num_shards = kwargs.get("num_shards", "1")
        params['numShards'] = num_shards

        shards = kwargs.get("shards")
        if shards:
            params['shards'] = shards

        max_shards_per_node = kwargs.get('max_shards_per_node', 1)
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
        if not self.exists() or force:
            res = self.client.get('admin/collections', params).result
            if hasattr(res, 'success'):
                # Create the index and wait until it's available
                while True:
                    if not self._is_index_created():
                        logging.getLogger('solrcloud').info("index not created yet, waiting...")
                        time.sleep(1)
                    else: 
                        break
                    return SolrCollectionAdmin(self.connection,self.name)
            else:
                raise SolrException(str(res))

        # this collection is already present, just return it
        return SolrCollectionAdmin(self.connection, self.name)

    def _is_index_created(self):
        """
        Whether the index was created
        :rtype: bool
        """
        server = list(self.connection.servers)[0]
        req = requests.get('%s/solr/%s' % (server, self.name))
        return req.status_code == requests.codes.ok

    def is_alias(self):
        """
        Determines if this collection is an alias for a 'real' collection
        :rtype: bool
        """
        response = self.client.get('/solr/admin/collections', {'action': 'CLUSTERSTATUS', 'wt': 'json'}).result.dict
        if 'aliases' in response['cluster']:
            return self.name in response['cluster']['aliases']
        return False

    def drop(self):
        """
        Delete a collection
        
        :return: a response associated with the delete request
        :rtype: SolrResponse
        """
        return self.client.get('admin/collections', {'action': 'DELETE', 'name': self.name}).result

    def reload(self):
        """
        Reload a collection
        
        :return: a response associated with the reload request
        :rtype: SolrResponse
        """
        return self.client.get('admin/collections', {'action': 'RELOAD', 'name': self.name}).result

    def split_shard(self, shard, ranges=None, split_key=None):
        """
        Split a shard into two new shards

        :param shard: The name of the shard to be split.
        :type shard: str
        :param ranges: A comma-separated list of hash ranges in hexadecimal e.g. ranges=0-1f4,1f5-3e8,3e9-5dc
        :type ranges: str
        :param split_key: The key to use for splitting the index
        :type split_key: str
        :return: a response associated with the splitshard request
        :rtype: SolrResponse
        """
        params = {'action': 'SPLITSHARD', 'collection': self.name, 'shard': shard}
        if ranges:
            params['ranges'] = ranges
        if split_key:
            params['split.key'] = split_key
        return self.client.get('admin/collections', params).result

    def create_shard(self, shard, create_node_set=None):
        """
        Create a new shard

        :param shard: The name of the shard to be created.
        :type shard: str
        :param create_node_set: Allows defining the nodes to spread the new collection across.
        :type create_node_set: str
        :return: a response associated with the createshard request
        :rtype: SolrResponse
        """
        params = {'action': 'CREATESHARD', 'collection': self.name, 'shard': shard}
        if create_node_set:
            params['create_node_set'] = create_node_set
        return self.client.get('admin/collections', params).result

    def create_alias(self, alias):
        """
        Create or modify an alias for a collection

        :param alias: the name of the alias
        :type alias: str
        :return: a response associated with the createalias request
        :rtype: SolrResponse
        """
        params = {'action': 'CREATEALIAS', 'name': alias, 'collections': self.name}
        return self.client.get('admin/collections', params).result

    def delete_alias(self, alias):
        """
        Delete an alias for a collection

        :param alias: the name of the alias
        :type alias: str
        :return: a response associated with the deletealias request
        :rtype: SolrResponse
        """
        params = {'action': 'DELETEALIAS', 'name': alias}
        return self.client.get('admin/collections', params).result

    def delete_replica(self, replica, shard):
        """
        Delete a replica

        :param replica:  The name of the replica to remove.
        :type replica: str
        :param shard: The name of the shard that includes the replica to be removed.
        :type shard: str
        :return: a response associated with the deletereplica request
        :rtype: SolrResponse
        """
        params = {'action': 'DELETEREPLICA',
                  'replica': replica,
                  'collection': self.name,
                  'shard': shard}
        return self.client.get('admin/collections', params).result

    @property
    def state(self):
        """
        Get the state of this collection
        
        :return: the state of this collection
        :rtype: dict
        """
        if self.is_alias():
            return {"warn": "no state info available for aliases"}

        try:
            params = {'detail': 'true', 'path': '/clusterstate.json'}
            response = self.client.get('/solr/zookeeper', params).result
            data = json.loads(response['znode']['data'])
            return data[self.name]
        except KeyError:
            response = self.client.get(
                '/{webappdir}/admin/collections'.format(webappdir=self.connection.webappdir),
                dict(action='clusterstatus')
            ).result
            try:
                return response['cluster']['collections'][self.name]
            except KeyError:
                return {}

    @property
    def shards(self):
        """
        See state method
        :rtype: dict
        """
        return self.state

    @property
    def index_info(self):
        """
        Get a high-level overview of this collection's index
        :return: information about an index
        :rtype: dict
        """
        response = self.client.get('%s/admin/luke' % self.name, {}).result
        # XXX ugly
        data = response['index'].dict
        data.pop('directory', None)
        data.pop('userData', None)
        return data

    @property
    def index_stats(self):
        """
        Retrieves the SolrIndexStats class
        :return: SolrIndexStats class
        :rtype: SolrIndexStats
        """
        if self._index_stats is None:
            self._index_stats = SolrIndexStats(self.connection, self.name)
        return self._index_stats
    
    @property
    def schema(self):
        """
        Retrieves the SolrSchema class
        :return: SolrSchema class
        :rtype: SolrSchema
        """
        if self._schema is None:
            self._schema = SolrSchema(self.connection, self.name)
        return self._schema

    @property
    def stats(self):
        """
        Alias for retrieving the SolrIndexStats class
        :return: SolrIndexStats class
        :rtype: SolrIndexStats
        """
        return self.index_stats
