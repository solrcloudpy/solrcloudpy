import unittest
import time
from solr_instance import SolrInstance
from solrcloudpy import Connection

class TestCollection(unittest.TestCase):
    def setUp(self):
        self.solrprocess = SolrInstance("solr2")
        self.solrprocess.start()
        self.solrprocess.wait_ready()
        self.conn = Connection()

    def tearDown(self):
        self.solrprocess.terminate()

    def test_create_collection(self):
        coll2 = self.conn.create_collection('coll2')
        time.sleep(3)
        coll2.delete()
        time.sleep(3)

    def test_reload(self):
        coll2 = self.conn.create_collection('coll2')
        time.sleep(3)
        res = coll2.reload()
        self.assertTrue(getattr(res,'success') is not None)
        coll2.delete()
        time.sleep(3)

    def test_split_shard(self):
        coll2 = self.conn.create_collection('coll2')
        time.sleep(3)
        res = coll2.split_shard('shard1',ranges="80000000-90000000,90000001-7fffffff")
        time.sleep(3)
        self.assertTrue(getattr(res,'success') is not None)
        coll2.delete()
        time.sleep(3)

    def test_create_shard(self):
        coll2 = self.conn.create_collection('coll2',
                                            router_name='implicit',
                                            shards='myshard1',max_shards_per_node=3)
        time.sleep(3)
        res = coll2.create_shard('shard_my')
        time.sleep(3)
        self.assertTrue(getattr(res,'success') is not None)
        coll2.delete()

    def test_create_delete_alias(self):
        coll2 = self.conn.create_collection('coll2')
        time.sleep(3)
        coll2.create_alias('alias2')
        time.sleep(3)
        self.assertTrue(self.conn.alias2.is_alias())
        coll2.delete_alias('alias2')
        coll2.delete()
        time.sleep(3)

    def test_delete_replica(self):
        coll2 = self.conn.create_collection('coll2',
                                            router_name='implicit',
                                            shards='myshard1',
                                            max_shards_per_node=6,
                                            replication_factor=2)
        time.sleep(3)
        coll2.delete_replica('core_node2','myshard1')
        time.sleep(3)
        coll2.delete()
        time.sleep(3)
        
if __name__ == '__main__':
    unittest.main()
