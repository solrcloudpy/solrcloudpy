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

        Watch1 = self.zk.DataWatch('/live_nodes')
        Watch1(self.get_live_nodes)
        
        Watch2 = self.zk.DataWatch('/clusterstate.json')
        Watch2(self.get_server_addresses)

        self.servers = []
        
    def get_live_nodes(self,data,stat):
        self.live_nodes = self.zk.get_children('/live_nodes')
        return self.live_nodes

    def get_server_addresses(self,data,stat):
        res = json.loads(data)
        nodes = set()
        for config_dict in res.values():
            for shard_dicts in config_dict.values():
                if type(shard_dicts) != type({}):
                    continue
                
                for key,value in shard_dicts.items():
                    #print key
                    if type(value) != type({}):
                        continue
                    replicas_dicts = value.get('replicas')
                    addresses = replicas_dicts.values()
                    if addresses:
                        for address in addresses:
                            node_name = address.get('node_name')
                            if node_name in self.live_nodes: 
                                addr = address.get('base_url')+'/'
                                nodes.add(addr)
        
        self.servers = nodes
        try:
            self.zk.stop()
        except Exception as e:
            pass    

        return nodes

class HTTPConnection(object):
    """
    Connection to a single solr server not running in cloud mode
    """
    def __init__(self,address="http://localhost:8983/solr"):
        if type(address) == type(''):
            self.url = "http://%s/solr/" % address
            self.servers = [self.url,self.url]
        if type(address) == type([]):
            self.servers = ["http://%s/solr/" % a for a in address]
            
        print self.servers    
            
