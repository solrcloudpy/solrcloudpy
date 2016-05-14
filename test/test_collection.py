import unittest
import time
import os
from solr_instance import SolrInstance
from solrcloudpy import SolrConnection
from requests.adapters import ReadTimeout

solrprocess = None


class TestCollectionAdmin(unittest.TestCase):
    def setUp(self):
        self.conn = SolrConnection(version=os.getenv('SOLR_VERSION', '5.3.2'))

    def test_create_collection(self):
        original_count = len(self.conn.list())
        coll2 = self.conn.create_collection('coll2')
        self.assertEqual(len(self.conn.list()), original_count+1)
        self.conn.list()
        time.sleep(3)
        coll3 = self.conn.create_collection('coll3')
        self.assertEqual(len(self.conn.list()), original_count+2)
        # todo calling state here means the integration works, but what should we assert?
        coll2.state
        coll2.drop()
        self.assertEqual(len(self.conn.list()), original_count+1)
        time.sleep(3)
        coll3.drop()
        self.assertEqual(len(self.conn.list()), original_count)

    def test_reload(self):
        coll2 = self.conn.create_collection('coll2')
        time.sleep(3)
        res = coll2.reload()
        self.assertTrue(getattr(res, 'success') is not None)
        coll2.drop()

    def test_split_shard(self):
        coll2 = self.conn.create_collection('coll2')
        time.sleep(3)
        res = coll2.split_shard('shard1', ranges="80000000-90000000,90000001-7fffffff")
        time.sleep(3)
        self.assertTrue(getattr(res, 'success') is not None)
        coll2.drop()

    def test_create_shard(self):
        coll2 = self.conn.create_collection('coll2',
                                            router_name='implicit',
                                            shards='myshard1', max_shards_per_node=3)
        time.sleep(3)
        res = coll2.create_shard('shard_my')
        time.sleep(3)
        self.assertTrue(getattr(res, 'success') is not None)
        coll2.drop()

    def test_create_delete_alias(self):
        coll2 = self.conn.create_collection('coll2')
        coll2.create_alias('alias2')
        time.sleep(3)
        self.assertTrue(self.conn.alias2.is_alias())
        coll2.delete_alias('alias2')
        coll2.drop()

    def test_delete_replica(self):
        try:
            coll2 = self.conn.create_collection('test_delete_replica',
                                                router_name='implicit',
                                                shards='myshard1',
                                                max_shards_per_node=6,
                                                replication_factor=2)
        except ReadTimeout:
            print "Encountered read timeout while testing delete replicate"
            print "This generally doesn't mean the collection wasn't created with the settings passed."
            coll2 = self.conn['test_delete_replica']
        time.sleep(3)
        coll2.delete_replica('core_node2', 'myshard1')
        coll2.drop()


def setUpModule():
    if os.getenv('SKIP_STARTUP', False):
        return
    solrprocess = SolrInstance("solr2")
    solrprocess.start()
    solrprocess.wait_ready()
    time.sleep(1)
    
    
def tearDownModule():
    if os.getenv('SKIP_STARTUP', False):
        return
    if solrprocess:
        solrprocess.terminate()


if __name__ == '__main__':
    # run tests
    unittest.main()
