import unittest
from solr_instance import SolrInstance
import time
from solrcloudpy import Connection, Collection

class TestConnection(unittest.TestCase):
    def setUp(self):
        self.conn = Connection()

    def test_list(self):
        colls = self.conn.list()
        self.assertTrue(len(colls)>=1)

    def test_live_nodes(self):
        nodes = self.conn.live_nodes
        self.assertTrue(len(nodes)==1)

    def test_cluster_leader(self):
        leader = self.conn.cluster_leader
        self.assertTrue(leader is not None)

    def test_create_collection(self):
        coll = self.conn.create_collection('test2')
        self.assertTrue(isinstance(coll,Collection))
        self.conn.test2.delete()

def setUpModule():
    # start solr
    solrprocess = SolrInstance("solr2")
    solrprocess.start()
    solrprocess.wait_ready()
    time.sleep(1)

def tearDownModule():
    # stop solr
    import subprocess
    subprocess.call(args=['killall -9 java'],shell=True)

if __name__ == '__main__':
    unittest.main()
