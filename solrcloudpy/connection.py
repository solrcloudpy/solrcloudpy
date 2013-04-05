from kazoo.client import KazooClient
from kazoo.recipe.watchers import DataWatch
import json
    
class ZConnection(object):
    """
    Connection to a Zookeeper instance of a cluster of Solr servers
    """
    def __init__(self,zookeper_address):
        self.zk = KazooClient(zookeper_address)
        self.zk.start()

        Watch1 = DataWatch(self.zk, '/live_nodes')
        Watch1(self.get_live_nodes)
        
        Watch2 = DataWatch(self.zk, '/clusterstate.json')
        Watch2(self.get_server_addresses)
        
    def get_live_nodes(self,*args):
        self.live_nodes = self.zk.get_children('/live_nodes')
        print 'live nodes changed: ', self.live_nodes
        return self.live_nodes
        
    def get_server_addresses(self,*args):
        res,node = self.zk.get('/clusterstate.json')
        res = json.loads(res)
        nodes = set()
        for config_dict in res.values():
            for shard_dicts in config_dict.values():
                replicas_dicts = shard_dicts['replicas']
                addresses = replicas_dicts.values()
                if addresses:
                    for address in addresses:
                        node_name = address.get('node_name')
                        if node_name in self.live_nodes: 
                            addr = address.get('base_url')
                            nodes.add(addr)
        
        self.servers = nodes
        return nodes

class HTTPConnection(object):
    """
    Connection to a single solr server not running in cloud mode
    """
    def __init__(self,url="http://localhost:8983/solr"):
        self.url = url
        self.servers = [url]

        
#c = ZConnection("localhost:9983")
#c.get_server_addresses()
#print c.servers

# import time; time.sleep(5)
# print c.get_live_nodes()
# #print c.live_nodes
