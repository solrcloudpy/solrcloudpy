import unittest
import json
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
        coll2.delete()

    def test_reload(self):
        coll2 = self.conn.create_collection('coll2')
        res = json.loads(coll2.reload())
        self.assertTrue(res.has_key('success'))
        coll2.delete()

    def test_split_shard(self):
        coll2 = self.conn.create_collection('coll2')
        res = coll2.split_shard('shard1',ranges="80000000-90000000,90000001-7fffffff")
        self.assertTrue(res.has_key('success'))
        coll2.delete()

    def test_create_shard(self):
        coll2 = self.conn.create_collection('coll2',
                                            router_name='implicit',
                                            shards='myshard1',max_shards_per_node=3)
        res = coll2.create_shard('shard_my')
        self.assertTrue(res.has_key('success'))
        coll2.delete()

    def test_create_delete_alias(self):
        coll2 = self.conn.create_collection('coll2')
        coll2.create_alias('alias2')
        self.assertTrue(self.conn.a2.is_alias())
        coll2.delete_alias('alias2')
        coll2.delete()

    def test_delete_replica(self):
        coll2 = self.conn.create_collection('coll2',
                                            router_name='implicit',
                                            shards='myshard1',
                                            max_shards_per_node=6,
                                            replication_factor=2)
        coll2.delete_replica('core_node2','myshard1')
        coll2.delete()


if __name__ == '__main__':
    unittest.main()
