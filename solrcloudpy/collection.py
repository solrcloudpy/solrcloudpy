from requests.exceptions import ConnectionError

import solrcloudpy.index as index
import requests
import urlparse
import time

class _Request(object):
    """
    Issues requests to the collections API
    """
    def __init__(self,connection):
        self.connection = connection
        self.client = requests.Session()

    def request(self,path,params,method='GET',body=None):
        headers = {'content-type': 'application/json'}
        params['wt'] = 'json'

        servers = list(self.connection.servers)
        host = servers.pop(0)

        def make_request(host,path):
            fullpath = urlparse.urljoin(host,path)
            try:
                r = self.client.request(method,fullpath,
                                        params=params,
                                        headers=headers,data=body)

                if r.status_code == requests.codes.ok:
                    response = r.json()
                else:
                    response = r.text
                return response

            except ConnectionError:
                host = servers.pop(0)
                return make_request(host,path)

        result = make_request(host,path)
        return result

    def update(self,path,params,body):
        return self.request(path,params,'POST',body)

    def get(self,path,params):
        return self.request(path,params,method='GET')

class Collection(object):
    """
    Class to manage collections
    """
    def __init__(self,connection,name):
        self.connection = connection
        self.name = name
        self.client = _Request(connection)

    def list(self):
        """
        Lists out the current collections in the cluster
        """
        params = {'wt':'json','detail':'false','path':'/collections'}
        response = self.client.get('/solr/zookeeper',params)
        data = response['tree'][0]['children']
        colls = [node['data']['title'] for node in data]
        return colls

    def _list_cores(self):
        params = {'wt':'json',}
        response = self.client.get('admin/cores',params)
        cores = response.get('status',{}).keys()
        return cores

    def exists(self):
        """
        Finds if a collection exists in the cluster

        :param collection : the collection to find
        """
        return self.name in self.list()

    def create(self, replication_factor=1, force=False, **kwargs):
        """
        Create a collection

        :param name               : a string indicating the name of the collection

        :param num_shards         : an integer indicating the number of shards for this collection

        :param replication_factor : an integer indicating the number of replcas for this collection

        :param force              : a boolean value indicating whether to force the operation or not
                                    The default is `False`

        :param params             : additional parameters to be passed to this operation
        """
        params = {'name':self.name,
                  'replication_factor':replication_factor,
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


        if not self.exists() or force == True:
            self.client.get('admin/collections',params)
            # Create the index and wait until it's available
            while True:
                if not self._is_index_created():
                    print "index not created yet, waiting..."
                    time.sleep(1)
                break

        return index.SolrIndex(self.connection,self.name)

    def _is_index_created(self):
        """

        """
        server = list(self.connection.servers)[0]
        req = requests.get('%s/solr/%s' % (server,self.name))
        if req.status_code != requests.codes.ok:
            return False
        return True

    def delete(self):
        """
        Delete a collection

        :param name   : a string indicating the name of the collection

        :param params : additional parameters to be passed to this operation
        """
        return self.client.get('admin/collections',{'action':'DELETE','name':self.name})

    def reload(self):
        """
        Reload a collection

        :param name   : a string indicating the name of the collection

        :param params : additional parameters to be passed to this operation
        """
        self.client.get('admin/collections',{'action':'RELOAD','name':self.name})

    def split_shard(self, shard, ranges=None, split_key=None):
        """
        """
        params = {'action':'SPLITSHARD','name':self.name,'shard':shard}
        if ranges:
            params['ranges'] = ranges
        if split_key:
            params['split.key'] = split_key
        self.client.get('admin/collections',params)

    def create_shard(self, shard, create_node_set=None):
        """
        """
        params = {'action':'CREATESHARD','collection':self.name,
                  'shard':shard }
        if create_node_set:
            params['create_node_set'] = create_node_set
        self.client.get('admin/collections',params)

    def create_alias(self, collections):
        """

        """
        params = {'action':'CREATEALIAS',
                  'name':self.name,'collections':collections}
        self.client.get('admin/collections',params)

    def delete_alias(self):
        """

        """
        params = {'action':'DELETEALIAS','name':self.name,}
        self.client.get('admin/collections',params)

    def delete_replica(self, replica):
        """

        """
        params = {'action':'DELETEREPLICA',
                  'replica':replica,'collection':self.name}
        self.client.get('admin/collections',params)

    def __getattr__(self,name):
        ind = index.SolrIndex(self.connection,self.name)
        return getattr(ind,name)
