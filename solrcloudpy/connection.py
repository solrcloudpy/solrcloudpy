class HTTPConnection(object):
    """
    Connection to a solr server or several ones

    :param server: The server. Can be a single one or a list of servers
                    Example: `localhost:8983` or ``[localhost,solr1.domain.com:8983]``
    """
    def __init__(self,server="localhost:8983"):
        if type(address) == type(''):
            self.url = "http://%s/solr/" % address
            self.servers = [self.url,self.url]
        if type(address) == type([]):
            self.servers = ["http://%s/solr/" % a for a in address]
        
