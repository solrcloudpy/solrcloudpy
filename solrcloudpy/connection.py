import urllib
import json

class HTTPConnection(object):
    """
    Connection to a solr server or several ones

    :param server:           The server. Can be a single one or a list of servers
                              Example: `localhost:8983` or ``[localhost,solr1.domain.com:8983]``

    :param detect_live_nodes : whether to detect live nodes automativally or not. This assumes 
                               that one is able to access the IPs listed by Zookeeper.
                               The default value is `Falsse`
    """
    def __init__(self,server="localhost:8983",detect_live_nodes=False):
        if type(server) == type(''):
            self.url = "http://%s/solr/" % server
            servers = [self.url,self.url]
            if detect_live_nodes:
                url = servers[0]
                self.servers = self.detect_nodes(url)
            else:
                self.servers = servers
        if type(server) == type([]):
            servers = ["http://%s/solr/" % a for a in server]
            if detect_live_nodes:
                url = servers[0]
                self.servers = self.detect_nodes(url)
            else:
                self.servers = servers
                
    def detect_nodes(self,url):
        url = url+'zookeeper?path=/live_nodes'
        live_nodes = urllib.urlopen(url).read()
        data = json.loads(live_nodes)
        children = [d['data']['title'] for d in data['tree'][0]['children']]
        nodes = [c.replace('_solr','') for c in children]
        return ["http://%s/solr/" % a for a in nodes]
