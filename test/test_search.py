import unittest
import time
from test.solr_instance import SolrInstance
from solrcloudpy import SolrConnection

class TestCollectionSearch(unittest.TestCase):
    def setUp(self):
        self.conn = SolrConnection()

    def test_add(self):
        coll2 = self.conn.create_collection('coll2')
        docs = [{"id":str(_id),"includes":"silly text"} for _id in range(5)]

        coll2.add(docs)
        coll2.commit()
        res = coll2.search({"q":"id:1"}).result
        self.assertTrue(len(res.response.docs)== 1)
        coll2.drop()

def setUpModule():
    # start solr
    solrprocess = SolrInstance("solr2")
    solrprocess.start()
    solrprocess.wait_ready()
    time.sleep(3)
    
def tearDownModule():
    # stop solr
    import subprocess
    subprocess.call(args=['killall -9 java'],shell=True)

if __name__ == '__main__':
    # run tests
    unittest.main()
