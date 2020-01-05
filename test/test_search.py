import os
import time
import unittest

from solr_instance import SolrInstance
from solrcloudpy import SearchOptions, SolrConnection

solrprocess = None


class TestCollectionSearch(unittest.TestCase):
    def setUp(self):
        self.conn = SolrConnection(version=os.getenv("SOLR_VERSION", "6.1.0"))
        self.collparams = {}
        confname = os.getenv("SOLR_CONFNAME", "")
        if confname != "":
            self.collparams["collection_config_name"] = confname

    def test_add(self):
        coll2 = self.conn.create_collection("coll2", **self.collparams)
        docs = [{"id": str(_id), "includes": "silly text"} for _id in range(5)]

        coll2.add(docs)
        coll2.commit()
        res = coll2.search({"q": "id:1"}).result
        self.assertTrue(len(res.response.docs) == 1)
        coll2.drop()

    def test_delete(self):
        coll2 = self.conn.create_collection("coll2", **self.collparams)
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

    def test_custom_params_search(self):
        coll2 = self.conn.create_collection("coll2", **self.collparams)
        docs = [{"id": str(_id), "includes": "silly text"} for _id in range(5)]

        res_1 = coll2.add(docs, {"omitHeader": "false"})
        self.assertEqual(0, res_1.responseHeader.status)

        coll2.commit()
        res_2 = coll2.search({"q": "id:1", "omitHeader": "false"}).result
        self.assertEqual(0, res_2.responseHeader.status)

    def test_post_body_search(self):
        coll2 = self.conn.create_collection("coll2", **self.collparams)
        docs = [{"id": str(_id), "includes": "silly text"} for _id in range(5)]

        coll2.add(docs)
        coll2.commit()
        # JSON DSL Query format
        res = coll2.search({}, "POST", '{"query": "id:1"}').result
        self.assertTrue(len(res.response.docs) == 1)
        coll2.drop()


def setUpModule():
    if os.getenv("SKIP_STARTUP", False):
        return
    # start solr
    solrprocess = SolrInstance("solr2")
    solrprocess.start()
    solrprocess.wait_ready()
    time.sleep(3)


def tearDownModule():
    if os.getenv("SKIP_STARTUP", False):
        return
    if solrprocess:
        solrprocess.terminate()


if __name__ == "__main__":
    # run tests
    unittest.main()
