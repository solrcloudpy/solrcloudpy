import unittest
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
                
if __name__ == '__main__':
    unittest.main()
