"""
Connecting to a set of solr servers.

To get a :class:`~solrcloudpy.SolrCollection` instance from a :class:`SolrConnection` use either dictionary-style or attribute-style access:


    >>> from solrcloudpy.connection import SolrConnection
    >>> conn = SolrConnection()
    >>> conn.list()
    [u'collection1']
    >>> conn['collection1']
    SolrCollection<collection1>


"""
import json

import semver
from future.utils import iteritems

import solrcloudpy.collection as collection
from solrcloudpy.utils import _Request

MIN_SUPPORTED_VERSION = ">5.4.0"

MAX_SUPPORTED_VERSION = "<=9.0.0"


class SolrConnection(object):

    """
    Connection to a solr server or several ones

    :param server: The server. Can be a single one or a list of servers. Example  ``localhost:8983`` or ``[localhost,solr1.domain.com:8983]``.
    :type server: str
    :param detect_live_nodes: whether to detect live nodes automativally or not. This assumes that one is able to access the IPs listed by Zookeeper. The default value is ``False``.
    :type detect_live_nodes: bool

    :param auth: custom authentication. Example  ``HTTPKerberosAuth``
    :type auth: object
    :param user: HTTP basic auth user name
    :type user: str
    :param password: HTTP basic auth password
    :type password: str
    :param timeout: timeout for HTTP requests
    :type timeout: int
    :param webappdir: the solr webapp directory; defaults to 'solr'
    :type webappdir: str
    :param version: the solr version we're currently running. defaults to 5.3.0 for backwards compatibility. must be semver compliant
    :type version: str
    :param request_retries: number of times to retry a request against the same server. particularly useful for load-balancing or proxy situations.
    :type request_retries: int
    :param use_https: True if https is required
    :type use_https: bool
    """

    def __init__(
        self,
        server="localhost:8983",
        detect_live_nodes=False,
        auth=None,
        user=None,
        password=None,
        timeout=10,
        webappdir="solr",
        version="7.7.0",
        request_retries=1,
        use_https=False,
    ):
        self.auth = auth
        self.user = user
        self.password = password
        self.timeout = timeout
        self.webappdir = webappdir
        self.version = version
        self.request_retries = request_retries

        if not semver.match(version, MIN_SUPPORTED_VERSION) and semver.match(
            version, MAX_SUPPORTED_VERSION
        ):
            raise Exception("Unsupported version %s" % version)

        self.zk_path = "/{webappdir}/admin/zookeeper".format(webappdir=self.webappdir)

        protocol = "https" if use_https else "http"

        self.url_template = "{protocol}://{{server}}/{webappdir}/".format(
            protocol=protocol, webappdir=self.webappdir
        )

        if type(server) == str:
            self.url = self.url_template.format(server=server)
            servers = [self.url, self.url]
            if detect_live_nodes:
                url = servers[0]
                self.servers = self.detect_nodes(url)
            else:
                self.servers = servers
        if type(server) == list:
            servers = [self.url_template.format(server=a) for a in server]
            if detect_live_nodes:
                url = servers[0]
                self.servers = self.detect_nodes(url)
            else:
                self.servers = servers

        self.client = _Request(self)

    def detect_nodes(self, _):
        """
        Queries Solr's zookeeper integration for live nodes

        DEPRECATED

        :return: a list of sorl URLs corresponding to live nodes in solrcloud
        :rtype: list
        """
        return self.live_nodes

    def list(self):
        """
        Lists out the current collections in the cluster
        This should probably be a recursive function but I'm not in the mood today

        :return: a list of collection names
        :rtype: list
        """
        params = {"detail": "false", "path": "/collections"}
        response = self.client.get(self.zk_path, params).result

        if "children" not in response["tree"][0]:
            return []

        if response["tree"][0]["data"]["title"] == "/collections":
            # solr 5.3 and older
            data = response["tree"][0]["children"]
        else:
            # solr 5.4+
            data = None
            for branch in response["tree"]:
                if data is not None:
                    break
                for child in branch["children"]:
                    if child["data"]["title"] == "/collections":
                        if "children" not in child:
                            return []
                        else:
                            data = child["children"]
                            break
        colls = []
        if data:
            colls = [node["data"]["title"] for node in data]
        return colls

    def _list_cores(self):
        """
        Retrieves a list of cores from solr admin
        :return: a list of cores
        :rtype: list
        """
        params = {
            "wt": "json",
        }
        response = self.client.get(
            ("/{webappdir}/admin/cores".format(webappdir=self.webappdir)), params
        ).result
        cores = list(response.get("status", {}).keys())
        return cores

    @property
    def cluster_health(self):
        """
        Determine the state of all nodes and collections in the cluster. Problematic nodes or
        collections are returned, along with their state, otherwise an `OK` message is returned

        :return: a dict representing the status of the cluster
        :rtype: dict
        """
        res = []
        if semver.match(self.version, "<5.4.0"):
            params = {"detail": "true", "path": "/clusterstate.json"}
            response = self.client.get(
                ("/{webappdir}/zookeeper".format(webappdir=self.webappdir)), params
            ).result
            data = json.loads(response["znode"]["data"])
            collections = self.list()
            for coll in collections:
                shards = data[coll]["shards"]
                for shard, shard_info in iteritems(shards):
                    replicas = shard_info["replicas"]
                    for replica, info in iteritems(replicas):
                        state = info["state"]
                        if state != "active":
                            item = {
                                "collection": coll,
                                "replica": replica,
                                "shard": shard,
                                "info": info,
                            }
                            res.append(item)
        else:
            params = {"action": "CLUSTERSTATUS", "wt": "json"}
            response = self.client.get(
                ("/{webappdir}/admin/collections".format(webappdir=self.webappdir)),
                params,
            ).result
            for collection_name, collection in list(
                response.dict["cluster"]["collections"].items()
            ):
                for shard_name, shard in list(collection["shards"].items()):
                    for replica_name, replica in list(shard["replicas"].items()):
                        if replica["state"] != "active":
                            item = {
                                "collection": collection_name,
                                "replica": replica_name,
                                "shard": shard_name,
                                "info": replica,
                            }
                            res.append(item)

        if not res:
            return {"status": "OK"}

        return {"status": "NOT OK", "details": res}

    @property
    def cluster_leader(self):
        """
        Gets the cluster leader

        :rtype: dict
        :return: a dict with the json loaded from the zookeeper response related to the cluster leader request
        """
        params = {"detail": "true", "path": "/overseer_elect/leader"}
        response = self.client.get(self.zk_path, params).result
        return json.loads(response["znode"]["data"])

    @property
    def live_nodes(self):
        """
        Lists all nodes that are currently online

        :return: a list of urls related to live nodes
        :rtype: list
        """
        params = {"detail": "true", "path": "/live_nodes"}
        response = self.client.get(self.zk_path, params).result
        children = [d["data"]["title"] for d in response["tree"][0]["children"]]
        nodes = [c.replace("_solr", "") for c in children]
        return [self.url_template.format(server=a) for a in nodes]

    def create_collection(self, collname, *args, **kwargs):
        r"""
        Create a collection.

        :param collname: The collection name
        :type collname: str
        :param \*args: additional arguments
        :param \*\*kwargs: additional named parameters

        :return: the created collection
        :rtype: SolrCollection
        """
        coll = collection.SolrCollection(self, collname)
        return coll.create(*args, **kwargs)

    def __getattr__(self, name):
        """
        Convenience method for retrieving a solr collection
        :param name: the name of the collection
        :type name: str
        :return: SolrCollection
        """
        return collection.SolrCollection(self, name)

    def __getitem__(self, name):
        """
        Convenience method for retrieving a solr collection
        :param name: the name of the collection
        :type name: str
        :return: SolrCollection
        """
        return collection.SolrCollection(self, name)

    def __dir__(self):
        """
        Convenience method for viewing servers available in this connection

        :return: a list of servers
        :rtype: list
        """
        return self.list()

    def __repr__(self):
        """
        Representation in Python outputs
        :return: string representation
        :rtype: str
        """
        return "SolrConnection %s" % str(self.servers)
