import unittest
import time
from solr_instance import SolrInstance
from solrcloudpy import SolrConnection, SearchOptions


class TestCollectionSearch(unittest.TestCase):

    def setUp(self):
        self.conn = SolrConnection()

    def test_add(self):
        coll2 = self.conn.create_collection('coll2')
        docs = [{"id": str(_id), "includes": "silly text"} for _id in range(5)]

        coll2.add(docs)
        coll2.commit()
        res = coll2.search({"q": "id:1"}).result
        self.assertTrue(len(res.response.docs) == 1)
        coll2.drop()

    def test_delete(self):
        coll2 = self.conn.create_collection('coll2')
        docs = [{"id": str(_id), "includes": "silly text"} for _id in range(5)]

        coll2.add(docs)
        coll2.commit()

        # delete w/ object
        so = SearchOptions()
        so.commonparams.q("id:1")
        coll2.delete(so)
        res = coll2.search({"q": "id:1"}).result
        self.assertTrue(len(res.response.docs) == 0)

        # delete w/ dict
        so = {"q": "id:2"}
        coll2.delete(so)
        res = coll2.search({"q": "id:2"}).result
        self.assertTrue(len(res.response.docs) == 0)

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
    subprocess.call(args=['killall -9 java'], shell=True)

if __name__ == '__main__':
    # run tests
    unittest.main()
