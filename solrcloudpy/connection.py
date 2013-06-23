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
        
